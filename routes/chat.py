from flask import Blueprint, request, jsonify
import re

from services import rag, llm_router
from models.chat_log import ChatLog, is_keluhan_message, extract_nama, extract_no_wa

chat_bp = Blueprint('chat', __name__)

NAMA_TOKO = 'F3'

SYSTEM_PROMPT = f"""Kamu adalah "{NAMA_TOKO}", asisten customer service toko jahit di Jeneponto.
Tugasmu menjawab pertanyaan pelanggan seputar LAYANAN, GALERI (hasil jahitan), dan PESANAN.

Aturan:
1. Selalu jawab dalam Bahasa Indonesia yang ramah, hangat, dan RAPI. Maksimal 4-5 baris.
2. DILARANG memakai tanda markdown apa pun: jangan gunakan **, *, #,
Demikian juga jangan garis miring untuk keterangan (em dash boleh).
3. Untuk daftar harga/layanan/status, tulis satu item per baris diawali tanda "- "
   tanpa tanda lainnya. Contoh:
   - Jahit kebaya: mulai Rp 250.000
   - Permak celana: Rp 25.000
   Bila tidak ada daftar, tulis 2-3 kalimat pendek.
4. Gunakan HANYA data yang diberikan di bawah pertanyaan pengguna. Jangan mengarang harga, jadwal, atau fakta lain.
5. Jika data tidak cukup, arahkan pelanggan ke halaman layanan (/layanan), galeri (/galeri), form pemesanan (/pesan), atau WhatsApp yang tertera di situs.
6. Jika diminta contoh / foto / hasil jahitan, pilih 1-4 foto dari daftar GALERI yang paling sesuai, lalu tulis url-nya pada kunci "gambar".
7. Untuk pertanyaan status pesanan, jawab sesuai data PESANAN yang diberikan. Jangan bocorkan nomor WhatsApp pelanggan.
8. Jika pertanyaan tidak ada hubungannya dengan toko jahit, tetap ramah tolak dengan halus dan arahkan kembali ke layanan kami.

Balasan HARUS berupa JSON murni tanpa teks tambahan, format:
{{"jawaban": "teks jawaban", "gambar": ["url1", "url2"]}}
Jika tidak ada foto, gunakan "gambar": []."""


def _get_db():
    from app import get_db
    return get_db()


def _build_user_prompt(message, context):
    lines = [f'Pertanyaan pelanggan: "{message}"', '']
    lines.append('DATA LAYANAN:')
    for l in context['layanan']:
        lines.append(l)
    lines.append('')
    lines.append('GALERI (foto hasil jahitan, url + keterangan):')
    for g in context['galeri']:
        lines.append(f"- {g.get('url')} | {g.get('keterangan')}")
    if not context['galeri']:
        lines.append('- (tidak ada)')
    lines.append('')
    lines.append('DATA PESANAN (nama pelanggan, layanan, ukuran, status, catatan):')
    for p in context['pesanan']:
        lines.append(f"- {p.get('nama')} | {p.get('layanan')} | ukuran {p.get('ukuran')} | status: {p.get('status')} | {p.get('catatan')}")
    if not context['pesanan']:
        lines.append('- (tidak ada)')
    return '\n'.join(lines)


def _layanan_line(l):
    parts = [p.strip() for p in l.split('|')]
    nama = parts[0].replace('- ', '').strip()
    nama = re.sub(r'\s*\[[^\]]*\]\s*', '', nama)
    harga = parts[1].strip() if len(parts) > 1 else '-'
    return f'- {nama}: {harga}'


def _offline_reply(message, context):
    msg = message.lower()
    minta_foto = any(k in msg for k in ('foto', 'contoh', 'gambar', 'lihat hasil', 'model', 'referensi'))
    tanya_pesanan = any(k in msg for k in ('pesanan', 'status', 'dikerjakan', 'selesai', 'dibatalkan', 'baru', 'di mana pesanan', 'dimana pesanan'))

    galeri = context['galeri']
    layanan = context['layanan']

    if tanya_pesanan and context['pesanan']:
        daftar = '\n'.join(
            f"- {p['nama']}: {p['layanan']} ({p['status']})" for p in context['pesanan'][:4]
        )
        return {
            'jawaban': f'Berikut ringkasan pesanan yang relevan:\n{daftar}\nUntuk detail lebih lengkap, silakan hubungi admin F3 via WhatsApp ya!',
            'gambar': [],
        }

    if minta_foto and galeri:
        contoh = '\n'.join(f'- {g["keterangan"]}' for g in galeri[:3])
        return {
            'jawaban': f'Berikut contoh hasil jahitan kami:\n{contoh}\nFoto lainnya bisa dilihat di halaman Galeri ya!',
            'gambar': [g['url'] for g in galeri[:4]],
        }

    if layanan:
        daftar = '\n'.join(_layanan_line(l) for l in layanan[:6])
        return {
            'jawaban': f'Berikut layanan yang tersedia:\n{daftar}\nUntuk keterangan lengkap, buka halaman Layanan atau klik "Pesan sekarang"!',
            'gambar': [],
        }

    return {
        'jawaban': 'Halo! Saya asisten F3. Anda bisa bertanya soal layanan jahit, contoh hasil jahitan/galeri, atau status pesanan. Kalau butuh bantuan admin, silakan WhatsApp kami langsung ya!',
        'gambar': [],
    }


@chat_bp.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'reply': 'Silakan tulis pertanyaan Anda.', 'gambar': [], 'provider': None}), 400
    if len(message) > 2000:
        return jsonify({'reply': 'Pertanyaan terlalu panjang, mohon dipersingkat.', 'gambar': [], 'provider': None}), 400

    db = _get_db()
    context = rag.build_context(db, message)
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': _build_user_prompt(message, context)},
    ]

    result = llm_router.chat(messages)

    if result['error'] and not result['content']:
        parsed = _offline_reply(message, context)
        provider = None
        error = result['error']
    else:
        parsed = llm_router.parse_reply(result['content'])
        provider = result['provider']
        error = result['error']
        if provider is None:
            parsed = _offline_reply(message, context)

    reply = parsed['jawaban']
    gambar = parsed['gambar']

    minta_foto = any(k in message.lower() for k in ('foto', 'contoh', 'gambar', 'hasil jahit'))
    if not gambar and minta_foto and context['galeri']:
        gambar = [g['url'] for g in context['galeri'][:4]]

    is_keluhan = is_keluhan_message(message)
    ChatLog(db).create(
        message=message,
        reply=reply,
        gambar=gambar,
        provider=provider,
        is_keluhan=is_keluhan,
        error=error,
        nama=extract_nama(message),
        no_wa=extract_no_wa(message),
    )

    return jsonify({'reply': reply, 'gambar': gambar, 'provider': provider})