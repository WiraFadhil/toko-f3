from datetime import datetime, timedelta

LAYANAN_DEFAULT = [
    # ---- custom ----
    {
        'nama_jasa': 'Jahit Kebaya',
        'kategori': 'custom',
        'harga_kisaran': 'Rp 250.000 - Rp 600.000',
        'deskripsi': 'Kebaya modern atau klasik dengan ukuran diambil langsung di badan, jahitan rapi sampai detail sulam.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Jahit Gamis / Baju Koko',
        'kategori': 'custom',
        'harga_kisaran': 'Rp 150.000 - Rp 400.000',
        'deskripsi': 'Gamis pria/wanita dan baju koko sesuai model dan bahan yang dipilih atau dibawa sendiri.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Jahit Gaun / Dress',
        'kategori': 'custom',
        'harga_kisaran': 'Rp 200.000 - Rp 500.000',
        'deskripsi': 'Gaun pesta, dress harian, sampai busana acara keluarga dengan ukuran yang presisi.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Jahit Celana & Rok',
        'kategori': 'custom',
        'harga_kisaran': 'Rp 80.000 - Rp 200.000',
        'deskripsi': 'Celana panjang, celana pendek, dan rok berbagai model dari bahan sendiri atau kami sediakan.',
        'aktif': True,
    },
    # ---- permak ----
    {
        'nama_jasa': 'Permak Celana',
        'kategori': 'permak',
        'harga_kisaran': 'Rp 25.000 - Rp 60.000',
        'deskripsi': 'Panjangkan/pendekkan, kecilkan atau longgarkan pinggang, dan perbaiki jahitan celana.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Permak Baju',
        'kategori': 'permak',
        'harga_kisaran': 'Rp 20.000 - Rp 75.000',
        'deskripsi': 'Kecilkan/besarkan badan baju, ubah garis leher, dan perbaiki jahitan yang rusak.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Pasang Resleting',
        'kategori': 'permak',
        'harga_kisaran': 'Rp 15.000 - Rp 40.000',
        'deskripsi': 'Ganti resleting yang putus atau pasang resleting baru pada celana, rok, dan jaket.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Ganti Kancing / Karet',
        'kategori': 'permak',
        'harga_kisaran': 'Rp 10.000 - Rp 30.000',
        'deskripsi': 'Ganti kancing lepas, karet serut, dan perbaikan kecil lainnya yang cepat selesai.',
        'aktif': True,
    },
    # ---- seragam ----
    {
        'nama_jasa': 'Seragam Sekolah',
        'kategori': 'seragam',
        'harga_kisaran': 'Rp 90.000 - Rp 180.000 / set',
        'deskripsi': 'Seragam SD/SMP/SMA, satuan maupun borongan satu kelas, dengan ukuran konsisten.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Seragam Kerja / Instansi',
        'kategori': 'seragam',
        'harga_kisaran': 'Rp 150.000 - Rp 350.000 / set',
        'deskripsi': 'Seragam kantor, instansi, restoran, dan event dalam jumlah banyak.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Seragam Organisasi / Komunitas',
        'kategori': 'seragam',
        'harga_kisaran': 'Rp 120.000 - Rp 250.000 / set',
        'deskripsi': 'Seragam kegiatan dan komunitas dengan jadwal pengerjaan yang bisa disepakati.',
        'aktif': True,
    },
    # ---- lainnya ----
    {
        'nama_jasa': 'Jas & Blazer',
        'kategori': 'lainnya',
        'harga_kisaran': 'Rp 400.000 - Rp 900.000',
        'deskripsi': 'Jas dan blazer custom untuk kantor atau acara resmi, dengan pelapis dan furing pilihan.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Gorden & Horden',
        'kategori': 'lainnya',
        'harga_kisaran': 'Rp 60.000 - Rp 200.000 / panel',
        'deskripsi': 'Gorden rumah atau kantor dengan model lipit maupun kuping, diukur langsung ke lokasi.',
        'aktif': True,
    },
    {
        'nama_jasa': 'Pesanan Khusus',
        'kategori': 'lainnya',
        'harga_kisaran': 'Harga menyesuaikan',
        'deskripsi': 'Kebutuhan jahitan di luar daftar — konsultasikan dulu via WhatsApp untuk harga dan jadwal.',
        'aktif': True,
    },
]

GALERI_SAMPLE = [
    {
        'url_foto': 'https://images.pexels.com/photos/8387807/pexels-photo-8387807.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Baju jadi yang siap diambil',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/14440412/pexels-photo-14440412.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Baju adat & kebaya custom',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/16678677/pexels-photo-16678677.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Seragam / jersey pesanan',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/7026778/pexels-photo-7026778.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Jaket hasil jahitan',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/11788012/pexels-photo-11788012.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Kemeja hasil permak',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/6070058/pexels-photo-6070058.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Dress & kemeja pas di badan',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/8619007/pexels-photo-8619007.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Busana wanita siap antar',
    },
    {
        'url_foto': 'https://images.pexels.com/photos/20544951/pexels-photo-20544951.jpeg?auto=compress&cs=tinysrgb&w=800',
        'keterangan': 'Gaun pilihan pelanggan',
    },
]

PESANAN_SAMPLE = [
    # (nama, no_wa, layanan_nama, ukuran, tanggal_jadi_str, status, days_ago, catatan)
    ('Siti Rahma', '081234567890', 'Jahit Gamis / Baju Koko', 'M', '2026-09-12', 'baru', 0,
     'Motif bunga, warna biru tua, model lengan lonceng.'),
    ('Andi Firmansyah', '081298765432', 'Permak Celana', '32', '2026-09-08', 'dikerjakan', 1,
     'Celana kerja dipendekkan 3 cm.'),
    ('Nurul Hikmah', '081255500111', 'Jahit Kebaya', 'L', '2026-09-20', 'baru', 0,
     'Kebaya brokat untuk acara keluarga, ukuran diambil nanti sore.'),
    ('Devi Lestari', '081377788899', 'Seragam Sekolah', 'S', '2026-09-10', 'selesai', 3,
     'Paket seragam 2 stel, dikirim ke rumah.'),
    ('Rizky Ramadhan', '081266677788', 'Jas & Blazer', 'XL', '2026-09-25', 'dikerjakan', 2,
     'Blazer hitam untuk wisuda, mau coba dulu sebelum dirapikan.'),
    ('Mbak Yuni Catering', '081588899900', 'Seragam Kerja / Instansi', 'L', '2026-09-15', 'selesai', 6,
     'Seragam 10 orang karyawan, warna maroon.'),
    ('Pak Haji Salim', '081566677788', 'Gorden & Horden', 'Custom', '2026-09-22', 'dibatalkan', 5,
     'Diukur ke rumah dulu, tapi tanah masih diproses.' ),
    ('Indah Permata', '081255544433', 'Jahit Gaun / Dress', 'M', '2026-09-14', 'selesai', 9,
     'Gaun pesta salem, model off-shoulder.'),
]


def ensure_collections(db):
    existing = set(db.list_collection_names())
    for name in ('users', 'layanan', 'pesanan', 'galeri'):
        if name not in existing:
            try:
                db.create_collection(name)
            except Exception:
                pass


def ensure_indexes(db):
    db.users.create_index('username', unique=True)
    db.layanan.create_index('kategori')
    db.layanan.create_index('aktif')
    db.pesanan.create_index('status')
    db.pesanan.create_index('created_at')
    db.galeri.create_index('created_at')


def seed_layanan(db):
    if db.layanan.count_documents({}) > 0:
        return False
    db.layanan.insert_many([dict(x) for x in LAYANAN_DEFAULT])
    return True


def seed_galeri(db):
    if db.galeri.count_documents({}) > 0:
        return False
    admin = db.users.find_one({'username': 'admin'})
    uploaded_by = admin['_id'] if admin else None
    docs = []
    for i, g in enumerate(GALERI_SAMPLE):
        docs.append({
            'url_foto': g['url_foto'],
            'keterangan': g['keterangan'],
            'uploaded_by': uploaded_by,
            'created_at': datetime.utcnow() - timedelta(days=len(GALERI_SAMPLE) - i),
        })
    db.galeri.insert_many(docs)
    return True


def seed_pesanan(db):
    if db.pesanan.count_documents({}) > 0:
        return False
    layanan_by_name = {d['nama_jasa']: d['_id'] for d in db.layanan.find()}
    docs = []
    for (nama, no_wa, layanan_nama, ukuran, tgl_jadi, status, days_ago, catatan) in PESANAN_SAMPLE:
        layanan_id = layanan_by_name.get(layanan_nama)
        if not layanan_id:
            continue
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        docs.append({
            'nama_pelanggan': nama,
            'no_wa': no_wa,
            'layanan_id': layanan_id,
            'ukuran': ukuran,
            'catatan': catatan,
            'tanggal_jadi_diinginkan': tgl_jadi,
            'status': status,
            'created_at': created_at,
            'updated_at': created_at,
        })
    if docs:
        db.pesanan.insert_many(docs)
    return True


def init_data(db):
    ensure_collections(db)
    ensure_indexes(db)
    return {
        'layanan': seed_layanan(db),
        'galeri': seed_galeri(db),
        'pesanan': seed_pesanan(db),
    }


if __name__ == '__main__':
    import config
    from pymongo import MongoClient

    client = MongoClient(config.MONGODB_URI)
    db_name = config.MONGODB_URI.rsplit('/', 1)[-1]
    if not db_name or '/' in db_name:
        db_name = 'toko_jahit'
    result = init_data(client[db_name])
    print('Seeding selesai:', result)