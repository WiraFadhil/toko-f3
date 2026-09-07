import os
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import bcrypt
import cloudinary
import cloudinary.uploader
from bson import ObjectId

from models.user import User
from models.layanan import Layanan
from models.pesanan import Pesanan
from models.galeri import Galeri
from models.chat_log import ChatLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def get_models():
    from app import get_db
    db = get_db()
    return {
        'user': User(db),
        'layanan': Layanan(db),
        'pesanan': Pesanan(db),
        'galeri': Galeri(db),
        'chat_log': ChatLog(db),
    }


def init_cloudinary():
    from flask import current_app
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET']
    )


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        models = get_models()
        user = models['user'].find_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            from flask_login import UserMixin

            class AdminUser(UserMixin):
                def __init__(self, uid, uname):
                    self.id = str(uid)
                    self.username = uname
                def get_id(self):
                    return self.id

            auth_user = AdminUser(user['_id'], user['username'])
            login_user(auth_user)
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Username atau password salah.'

    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    models = get_models()
    pesanan_baru = models['pesanan'].count_by_status('baru')
    pesanan_dikerjakan = models['pesanan'].count_by_status('dikerjakan')
    pesanan_selesai = models['pesanan'].count_by_status('selesai')
    pesanan_dibatalkan = models['pesanan'].count_by_status('dibatalkan')
    total_layanan = len(models['layanan'].all())
    total_foto = len(models['galeri'].all())
    total_keluhan = models['chat_log'].count_keluhan()

    recent = models['pesanan'].all()[:5]

    return render_template('admin/dashboard.html',
                           pesanan_baru=pesanan_baru,
                           pesanan_dikerjakan=pesanan_dikerjakan,
                           pesanan_selesai=pesanan_selesai,
                           pesanan_dibatalkan=pesanan_dibatalkan,
                           total_layanan=total_layanan,
                           total_foto=total_foto,
                           total_keluhan=total_keluhan,
                           recent=recent,
                           status_label=Pesanan.STATUS_LABEL)


@admin_bp.route('/pesanan')
@login_required
def pesanan_list():
    models = get_models()
    status = request.args.get('status', '')
    if status and status in Pesanan.STATUS_LABEL:
        pesanan_list = models['pesanan'].filter_status(status)
    else:
        pesanan_list = models['pesanan'].all()
        status = ''

    layanan_map = {}
    for l in models['layanan'].all():
        layanan_map[str(l['_id'])] = l

    return render_template('admin/pesanan.html',
                           pesanan=pesanan_list,
                           status=status,
                           layanan_map=layanan_map,
                           status_label=Pesanan.STATUS_LABEL)


@admin_bp.route('/pesanan/<pesanan_id>', methods=['GET', 'POST'])
@login_required
def pesanan_detail(pesanan_id):
    models = get_models()
    pesanan = models['pesanan'].get(pesanan_id)
    if not pesanan:
        flash('Pesanan tidak ditemukan.', 'error')
        return redirect(url_for('admin.pesanan_list'))

    layanan = models['layanan'].get(str(pesanan['layanan_id'])) if pesanan.get('layanan_id') else None

    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'update_status':
            new_status = request.form.get('status', '')
            if new_status in Pesanan.STATUS_LABEL:
                models['pesanan'].update_status(pesanan_id, new_status)
                flash('Status pesanan diperbarui.', 'success')
                return redirect(url_for('admin.pesanan_detail', pesanan_id=pesanan_id))
        elif action == 'delete':
            models['pesanan'].delete(pesanan_id)
            flash('Pesanan dihapus.', 'success')
            return redirect(url_for('admin.pesanan_list'))

    return render_template('admin/pesanan_detail.html',
                           pesanan=pesanan,
                           layanan=layanan,
                           status_label=Pesanan.STATUS_LABEL)


@admin_bp.route('/layanan', methods=['GET', 'POST'])
@login_required
def layanan_manage():
    models = get_models()
    if request.method == 'POST':
        nama_jasa = request.form.get('nama_jasa', '').strip()
        kategori = request.form.get('kategori', '')
        harga_kisaran = request.form.get('harga_kisaran', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        aktif = True if request.form.get('aktif') == 'on' else False

        if not nama_jasa or not kategori or not harga_kisaran:
            flash('Nama jasa, kategori, dan harga wajib diisi.', 'error')
        else:
            models['layanan'].create(nama_jasa, kategori, harga_kisaran, deskripsi, aktif)
            flash('Layanan berhasil ditambahkan.', 'success')
            return redirect(url_for('admin.layanan_manage'))

    layanan_list = models['layanan'].all()
    return render_template('admin/layanan.html', layanan=layanan_list)


@admin_bp.route('/layanan/<layanan_id>', methods=['POST'])
@login_required
def layanan_edit(layanan_id):
    models = get_models()
    action = request.form.get('action', '')

    if action == 'update':
        data = {
            'nama_jasa': request.form.get('nama_jasa', '').strip(),
            'kategori': request.form.get('kategori', ''),
            'harga_kisaran': request.form.get('harga_kisaran', '').strip(),
            'deskripsi': request.form.get('deskripsi', '').strip(),
            'aktif': True if request.form.get('aktif') == 'on' else False
        }
        if data['nama_jasa'] and data['kategori'] and data['harga_kisaran']:
            models['layanan'].update(layanan_id, data)
            flash('Layanan berhasil diperbarui.', 'success')
        else:
            flash('Data tidak lengkap.', 'error')
    elif action == 'delete':
        models['layanan'].delete(layanan_id)
        flash('Layanan dihapus.', 'success')

    return redirect(url_for('admin.layanan_manage'))


@admin_bp.route('/galeri', methods=['GET', 'POST'])
@login_required
def galeri_manage():
    models = get_models()

    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'upload':
            file = request.files.get('foto')
            keterangan = request.form.get('keterangan', '').strip()
            if not file or file.filename == '':
                flash('Silakan pilih file foto.', 'error')
            else:
                try:
                    init_cloudinary()
                    result = cloudinary.uploader.upload(
                        file,
                        folder='toko-jahit-galeri',
                        public_id=None
                    )
                    url = result.get('secure_url')
                    if not url:
                        raise Exception('Upload gagal')
                    models['galeri'].create(url, keterangan, current_user.id)
                    flash('Foto berhasil diupload.', 'success')
                except Exception as e:
                    flash(f'Gagal upload foto: {str(e)}', 'error')
            return redirect(url_for('admin.galeri_manage'))
        elif action == 'delete':
            foto_id = request.form.get('foto_id', '')
            try:
                init_cloudinary()
                galeri_item = models['galeri'].get(foto_id)
                if galeri_item:
                    public_id = None
                    url = galeri_item.get('url_foto', '')
                    if 'cloudinary' in url:
                        parts = url.replace('http://res.cloudinary.com/', '').replace('https://res.cloudinary.com/', '').split('/')
                        try:
                            idx = parts.index('toko-jahit-galeri')
                            public_id = '/'.join(parts[idx:])
                            if '.' in public_id.split('/')[-1]:
                                public_id = public_id.rsplit('.', 1)[0]
                        except ValueError:
                            pass
                    if public_id:
                        cloudinary.uploader.destroy(public_id)
                models['galeri'].delete(foto_id)
                flash('Foto dihapus.', 'success')
            except Exception as e:
                flash(f'Gagal hapus foto: {str(e)}', 'error')
            return redirect(url_for('admin.galeri_manage'))

    galeri_list = models['galeri'].all()
    return render_template('admin/galeri.html', galeri=galeri_list)


@admin_bp.route('/keluhan')
@login_required
def keluhan_list():
    models = get_models()
    if request.method == 'POST':
        action = request.form.get('action', '')
        log_id = request.form.get('log_id', '')
        if action == 'delete' and log_id:
            models['chat_log'].collection.delete_one({'_id': ObjectId(log_id)})
            flash('Keluhan dihapus.', 'success')
            return redirect(url_for('admin.keluhan_list'))

    keluhan = models['chat_log'].all(keluhan_only=True)
    return render_template('admin/keluhan.html', keluhan=keluhan)
