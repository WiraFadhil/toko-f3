from flask import Flask, redirect, url_for
from flask_login import LoginManager
from pymongo import MongoClient

import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MONGODB_URI'] = config.MONGODB_URI
app.config['CLOUDINARY_CLOUD_NAME'] = config.CLOUDINARY_CLOUD_NAME
app.config['CLOUDINARY_API_KEY'] = config.CLOUDINARY_API_KEY
app.config['CLOUDINARY_API_SECRET'] = config.CLOUDINARY_API_SECRET

mongo_client = None


def get_db():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(app.config['MONGODB_URI'])
    db_name = app.config['MONGODB_URI'].rsplit('/', 1)[-1]
    if not db_name or '/' in db_name:
        db_name = 'toko_jahit'
    return mongo_client[db_name]


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


init_database()


@app.route('/health')
def health():
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)