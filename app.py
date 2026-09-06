import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from pymongo import MongoClient
from jinja2 import DictLoader

import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from embedded_templates import TEMPLATES
from embedded_static import STATIC

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.jinja_loader = DictLoader(TEMPLATES)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MONGODB_URI'] = config.MONGODB_URI
app.config['CLOUDINARY_CLOUD_NAME'] = config.CLOUDINARY_CLOUD_NAME
app.config['CLOUDINARY_API_KEY'] = config.CLOUDINARY_API_KEY
app.config['CLOUDINARY_API_SECRET'] = config.CLOUDINARY_API_SECRET

mongo_client = None
_db = None


def get_db():
    global mongo_client, _db
    if _db is not None:
        return _db
    if mongo_client is None:
        mongo_client = MongoClient(app.config['MONGODB_URI'])
    uri = app.config['MONGODB_URI']
    db_name = uri.rsplit('/', 1)[-1].split('?')[0]
    if not db_name:
        db_name = 'toko_jahit'
    _db = mongo_client[db_name]
    return _db


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Silakan login sebagai admin terlebih dahulu.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from bson import ObjectId
    from models.user import User
    from flask_login import UserMixin

    try:
        db = get_db()
        user = User(db).get(user_id)
        if user:
            class AdminUser(UserMixin):
                def __init__(self, uid, uname):
                    self.id = str(uid)
                    self.username = uname
                def get_id(self):
                    return self.id
            return AdminUser(user['_id'], user['username'])
    except Exception:
        return None
    return None


from routes.public import public_bp
from routes.admin import admin_bp

app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)


@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import Response, send_from_directory
    if filename in STATIC:
        content_type = 'text/css' if filename.endswith('.css') else 'application/javascript'
        return Response(STATIC[filename], mimetype=content_type)
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)


def init_admin_user():
    import bcrypt
    from models.user import User
    db = get_db()
    user_model = User(db)
    username = 'admin'
    if not user_model.find_by_username(username):
        password = 'admin123'
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_model.create(username, password_hash)
        print('Admin user created. Username: admin, Password: admin123')


def init_database():
    """Buat akun admin + collection/index, lalu seed data awal bila masih kosong."""
    try:
        init_admin_user()
        from seed import init_data
        seeded = init_data(get_db())
        created = [name for name, ok in seeded.items() if ok]
        if created:
            print('Database di-seed:', ', '.join(created))
        else:
            print('Database sudah berisi data (seed dilewati).')
    except Exception as e:
        print(f'WARNING: init database dilewati ({e})')


_db_initialized = False


@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        _db_initialized = True
        try:
            init_database()
        except Exception as e:
            print(f'WARNING: init database dilewati ({e})')


@app.route('/health')
def health():
    return 'OK'


@app.route('/debug')
def debug_info():
    import os as _os
    lines = []
    lines.append(f'<b>MONGODB_URI set:</b> {bool(app.config["MONGODB_URI"])}')
    lines.append(f'<b>MONGODB_URI value:</b> {app.config["MONGODB_URI"]}')
    lines.append(f'<b>SECRET_KEY set:</b> {bool(app.config["SECRET_KEY"])}')
    lines.append(f'<b>CLOUD_NAME set:</b> {bool(app.config["CLOUDINARY_CLOUD_NAME"])}')
    try:
        db = get_db()
        count_layanan = db["layanan"].count_documents({})
        count_galeri = db["galeri"].count_documents({})
        lines.append(f'<b>DB connect:</b> OK')
        lines.append(f'<b>layanan count:</b> {count_layanan}')
        lines.append(f'<b>galeri count:</b> {count_galeri}')
    except Exception as e:
        lines.append(f'<b>DB connect:</b> FAIL -> {e}')
    return '<br>'.join(lines)


if __name__ == '__main__':
    app.run(debug=True)