import re

STOP_KATA = {
    'apa', 'berapa', 'yang', 'dengan', 'untuk', 'dari', 'pada', 'di', 'ke', 'ini',
    'itu', 'saya', 'aku', 'kamu', 'anda', 'bagaimana', 'ada', 'tolong', 'bisa',
    'mau', 'ingin', 'minta', 'mulai', 'untuk', 'berapa', 'apakah', 'kapan', 'dimana',
    'mana', 'dengan', 'sama', 'atau', 'dan', 'juga', 'tidak', 'sudah', 'akan',
    'yang', 'kak', 'mas', 'mbak', 'bang', 'pak', 'bu', 'bro', 'gan', 'sist',
}


def _keywords(text):
    words = re.findall(r'[a-z0-9]+', (text or '').lower())
    return [w for w in words if w not in STOP_KATA and len(w) > 2]


def _hits(text, keywords):
    if not keywords:
        return 0
    t = (text or '').lower()
    score = 0
    for k in keywords:
        if k in t:
            score += 1
            if re.search(r'\b' + re.escape(k) + r'\b', t):
                score += 1
    return score


def layanan_context(db, keywords):
    docs = list(db['layanan'].find({'aktif': True}).sort('nama_jasa', 1))
    scored = sorted(
        docs,
        key=lambda d: _hits(d.get('nama_jasa', '') + ' ' + d.get('kategori', '') + ' ' + d.get('deskripsi', ''), keywords),
        reverse=True,
    )
    lines = []
    for d in scored:
        lines.append(
            f"- {d.get('nama_jasa')} [{d.get('kategori')}] | {d.get('harga_kisaran')} | {d.get('deskripsi')}"
        )
    return lines


def galeri_context(db, keywords):
    docs = list(db['galeri'].find().sort('created_at', -1))
    hasil = []
    for d in docs:
        ket = d.get('keterangan', '')
        score = _hits(ket + ' ', keywords)
        hasil.append({'url': d.get('url_foto', ''), 'keterangan': ket, '_score': score})
    hasil.sort(key=lambda x: x['_score'], reverse=True)
    return hasil


def pesanan_context(db, keywords):
    docs = list(db['pesanan'].find().sort('created_at', -1))
    layanan_nama = {}
    for l in db['layanan'].find():
        layanan_nama[str(l.get('_id'))] = l.get('nama_jasa', '')
    status_label = {
        'baru': 'Baru',
        'dikerjakan': 'Sedang Dikerjakan',
        'selesai': 'Selesai',
        'dibatalkan': 'Dibatalkan',
    }
    hasil = []
    for p in docs:
        layanan = layanan_nama.get(str(p.get('layanan_id')), '')
        text = (
            p.get('nama_pelanggan', '') + ' ' + layanan + ' '
            + p.get('status', '') + ' ' + status_label.get(p.get('status', ''), '')
            + ' ' + p.get('catatan', '')
        )
        score = _hits(text, keywords)
        if score > 0:
            hasil.append({
                '_score': score,
                'nama': p.get('nama_pelanggan', ''),
                'layanan': layanan,
                'ukuran': p.get('ukuran', ''),
                'status': status_label.get(p.get('status', ''), p.get('status', '')),
                'catatan': p.get('catatan', ''),
            })
    hasil.sort(key=lambda x: x['_score'], reverse=True)
    return hasil


def build_context(db, message):
    keywords = _keywords(message)

    layanan = layanan_context(db, keywords)
    galeri = galeri_context(db, keywords)
    pesanan = pesanan_context(db, keywords)

    # daftar galeri relevan (untuk dikirimkan sebagai foto contoh)
    galeri_pilihan = [g for g in galeri if g.get('_score', 0) > 0][:6]

    if not galeri_pilihan:
        galeri_pilihan = galeri[:4]

    return {
        'layanan': layanan,
        'galeri': galeri_pilihan,
        'pesanan': pesanan[:8],
        'keywords': keywords,
    }