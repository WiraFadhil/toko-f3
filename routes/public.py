from flask import Blueprint, render_template, request, redirect, url_for, flash
from urllib.parse import quote
from bson import ObjectId
from models.layanan import Layanan
from models.pesanan import Pesanan
from models.galeri import Galeri

public_bp = Blueprint('public', __name__)

NAMA_TOKO = 'F3'
NO_WA_TOKO = '6281234567890'


def get_models():
    from app import get_db
    db = get_db()
    return {
        'layanan': Layanan(db),
        'pesanan': Pesanan(db),
        'galeri': Galeri(db)
    }


@public_bp.route('/')
def beranda():
    models = get_models()
    layanan = models['layanan'].all_aktif()
    galeri = models['galeri'].all()[:8]
    return render_template('public/beranda.html', layanan=layanan, galeri=galeri)


@public_bp.route('/tentang')
def tentang():
    return render_template('public/tentang.html')


@public_bp.route('/layanan')
def layanan():
    models = get_models()
    layanan_list = models['layanan'].all_aktif()
    return render_template('public/layanan.html', layanan=layanan_list)


@public_bp.route('/galeri')
def galeri():
    models = get_models()
    galeri_list = models['galeri'].all()
    return render_template('public/galeri.html', galeri=galeri_list)


@public_bp.route('/kontak')
def kontak():
    return render_template('public/kontak.html')


@public_bp.route('/pesan', methods=['GET', 'POST'])
def pesan():
    models = get_models()
    layanan_list = models['layanan'].all_aktif()
    error = None
    submitted = False
    wa_link = None

    if request.method == 'POST':
        nama_pelanggan = request.form.get('nama_pelanggan', '').strip()
        no_wa = request.form.get('no_wa', '').strip()
        layanan_id = request.form.get('layanan_id', '').strip()
        ukuran = request.form.get('ukuran', '').strip()
        catatan = request.form.get('catatan', '').strip()
        tanggal_jadi = request.form.get('tanggal_jadi', '').strip()

        if not nama_pelanggan:
            error = 'Nama pelanggan wajib diisi.'
        elif not no_wa:
            error = 'Nomor WhatsApp wajib diisi.'
        elif not layanan_id:
            error = 'Silakan pilih layanan.'
        elif not ukuran:
            error = 'Ukuran wajib diisi.'
        elif not tanggal_jadi:
            error = 'Tanggal jadi diinginkan wajib diisi.'
        elif not ObjectId.is_valid(layanan_id):
            error = 'Layanan tidak valid.'
        else:
            layanan_obj = models['layanan'].get(layanan_id)
            if not layanan_obj:
                error = 'Layanan tidak ditemukan.'
            else:
                models['pesanan'].create({
                    'nama_pelanggan': nama_pelanggan,
                    'no_wa': no_wa,
                    'layanan_id': ObjectId(layanan_id),
                    'ukuran': ukuran,
                    'catatan': catatan,
                    'tanggal_jadi_diinginkan': tanggal_jadi
                })
                submitted = True
                text = (
                    f'Halo, saya {nama_pelanggan}. Saya ingin memesan jasa '
                    f'"{layanan_obj.get("nama_jasa")}" (ukuran: {ukuran}, '
                    f'tanggal jadi diinginkan: {tanggal_jadi}). {catatan}'
                )
                wa_link = f'https://wa.me/{NO_WA_TOKO}?text={quote(text)}'

    return render_template(
        'public/pesan.html',
        layanan=layanan_list,
        error=error,
        submitted=submitted,
        wa_link=wa_link
    )
