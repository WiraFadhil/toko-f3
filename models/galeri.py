from bson import ObjectId
from datetime import datetime


class Galeri:
    def __init__(self, db):
        self.collection = db['galeri']

    def all(self):
        return list(self.collection.find().sort('created_at', -1))

    def get(self, foto_id):
        try:
            return self.collection.find_one({'_id': ObjectId(foto_id)})
        except Exception:
            return None

    def create(self, url_foto, keterangan, uploaded_by):
        return self.collection.insert_one({
            'url_foto': url_foto,
            'keterangan': keterangan,
            'uploaded_by': uploaded_by,
            'created_at': datetime.utcnow()
        })

    def delete(self, foto_id):
        return self.collection.delete_one({'_id': ObjectId(foto_id)})
