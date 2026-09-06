# Design Document — Website Toko Jahit [Nama Toko]

> Dokumen ini adalah lanjutan teknis dari PRD. Fokus di sini: arsitektur, skema database, struktur folder, daftar route, dan rencana deployment.

## 1. Ringkasan Arsitektur

```
[Pengunjung/Pelanggan] ──> [Flask App (Render/Railway)] ──> [MongoDB Atlas M0]
                                     │
                                     └──> [Cloudinary] (simpan foto galeri)
```

- **Frontend**: Server-rendered dengan Jinja2 (template Flask) — tidak perlu framework JS terpisah untuk skala ini.
- **Backend**: Flask (Python), menangani halaman publik, form pemesanan, dan admin panel.
- **Database**: MongoDB Atlas (free tier M0) — menyimpan layanan, pesanan, akun admin, metadata galeri.
- **Penyimpanan gambar**: Cloudinary (free tier) — MongoDB hanya menyimpan URL, bukan file gambar.
- **Autentikasi admin**: session-based login (Flask-Login) dengan password di-hash (bcrypt), bukan role kompleks — cukup 1 akun admin (mama) untuk MVP.

## 2. Tech Stack

| Layer | Teknologi |
|---|---|
| Backend framework | Flask |
| Template engine | Jinja2 |
| Database | MongoDB Atlas (via PyMongo) |
| Auth | Flask-Login + bcrypt |
| Penyimpanan gambar | Cloudinary |
| Hosting backend | Render atau Railway (free tier) |
| Styling | CSS biasa atau Tailwind (CDN, tanpa build step supaya simpel) |

## 3. Skema Database (MongoDB Collections)

### `users`
```json
{
  "_id": ObjectId,
  "username": "string",
  "password_hash": "string",
  "role": "admin",
  "created_at": "datetime"
}
```

### `layanan`
```json
{
  "_id": ObjectId,
  "nama_jasa": "string",
  "kategori": "custom | permak | seragam | lainnya",
  "harga_kisaran": "string",
  "deskripsi": "string",
  "aktif": true
}
```

### `galeri`
```json
{
  "_id": ObjectId,
  "url_foto": "string (URL dari Cloudinary)",
  "keterangan": "string",
  "uploaded_by": ObjectId (ref users),
  "created_at": "datetime"
}
```

### `pesanan`
```json
{
  "_id": ObjectId,
  "nama_pelanggan": "string",
  "no_wa": "string",
  "layanan_id": ObjectId (ref layanan),
  "ukuran": "string",
  "catatan": "string",
  "foto_referensi": "string (opsional, URL Cloudinary)",
  "tanggal_jadi_diinginkan": "date",
  "status": "baru | dikerjakan | selesai | dibatalkan",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 4. Daftar Halaman & Route

### Halaman Publik
| Route | Method | Deskripsi |
|---|---|---|
| `/` | GET | Beranda |
| `/tentang` | GET | Tentang kami |
| `/layanan` | GET | Daftar layanan & harga (dari collection `layanan`) |
| `/galeri` | GET | Galeri hasil jahitan (dari collection `galeri`) |
| `/kontak` | GET | Info kontak, alamat, jam operasional |
| `/pesan` | GET, POST | Form pemesanan → simpan ke `pesanan` |

### Admin Panel (perlu login)
| Route | Method | Deskripsi |
|---|---|---|
| `/admin/login` | GET, POST | Login admin |
| `/admin/logout` | GET | Logout |
| `/admin` | GET | Dashboard ringkas (jumlah pesanan baru, dll) |
| `/admin/pesanan` | GET | Daftar semua pesanan |
| `/admin/pesanan/<id>` | GET, POST | Detail pesanan + update status |
| `/admin/layanan` | GET, POST | Kelola daftar layanan & harga |
| `/admin/layanan/<id>` | POST | Edit/hapus layanan |
| `/admin/galeri` | GET, POST | Upload/hapus foto galeri (ke Cloudinary) |

## 5. Struktur Folder (Flask)

```
toko-jahit/
├── app.py
├── config.py
├── requirements.txt
├── .env                    # kredensial MongoDB & Cloudinary (jangan commit)
├── models/
│   ├── layanan.py
│   ├── pesanan.py
│   └── galeri.py
├── routes/
│   ├── public.py           # route halaman publik
│   └── admin.py            # route admin panel
├── templates/
│   ├── base.html
│   ├── public/
│   │   ├── beranda.html
│   │   ├── layanan.html
│   │   ├── galeri.html
│   │   ├── kontak.html
│   │   └── pesan.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       ├── pesanan.html
│       └── layanan.html
└── static/
    ├── css/
    └── js/
```

## 6. Alur Data Form Pemesanan (ringkas)

1. Pelanggan isi form di `/pesan` (nama, no WA, pilih layanan, ukuran, catatan, tanggal jadi diinginkan).
2. Data masuk ke collection `pesanan` dengan status `baru`.
3. (Opsional tahap lanjut) Kirim notifikasi otomatis ke WhatsApp mama via link `wa.me` yang di-generate setelah submit, atau integrasi WhatsApp API sederhana.
4. Mama buka `/admin/pesanan`, lihat pesanan baru, update status seiring proses (`dikerjakan` → `selesai`).

## 7. Rencana Deployment (Gratis)

1. **Database**: buat cluster MongoDB Atlas M0, whitelist IP `0.0.0.0/0` (untuk kemudahan, karena skala kecil) atau IP hosting spesifik.
2. **Gambar**: daftar Cloudinary free tier, simpan API key di `.env`.
3. **Backend**: push kode ke GitHub, deploy ke Render/Railway (free tier), set environment variables (`MONGODB_URI`, `CLOUDINARY_URL`, `SECRET_KEY`).
4. **Domain**: bisa pakai subdomain gratis dari Render/Railway dulu, upgrade ke domain custom (`.com`/`.id`) belakangan kalau sudah siap.

## 8. Catatan Keamanan Dasar

- Password admin di-hash dengan bcrypt, jangan disimpan plain text.
- Batasi akses `/admin/*` dengan `@login_required` di semua route admin.
- Validasi input form pemesanan di sisi server (bukan cuma HTML `required`), untuk cegah data kosong/spam.
- `.env` untuk semua kredensial, jangan pernah di-commit ke Git (tambahkan ke `.gitignore`).
