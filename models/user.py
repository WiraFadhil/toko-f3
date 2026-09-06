from datetime import datetime


class User:
    def __init__(self, db):
        self.collection = db['users']

    def find_by_username(self, username):
        return self.collection.find_one({'username': username})

    def get(self, user_id):
        from bson import ObjectId
        try:
            return self.collection.find_one({'_id': ObjectId(user_id)})
        except Exception:
            return None

    def create(self, username, password_hash, role='admin'):
        return self.collection.insert_one({
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow()
        })
