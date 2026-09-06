from bson import ObjectId
from datetime import datetime


class Pesanan:
    def __init__(self, db):
        self.collection = db['pesanan']

    STATUS_LABEL = {
        'baru': 'Baru',
        'dikerjakan': 'Sedang Dikerjakan',
        'selesai': 'Selesai',
        'dibatalkan': 'Dibatalkan'
    }

    def all(self):
        return list(self.collection.find().sort('created_at', -1))

    def filter_status(self, status):
        return list(self.collection.find({'status': status}).sort('created_at', -1))

    def get(self, pesanan_id):
        try:
            return self.collection.find_one({'_id': ObjectId(pesanan_id)})
        except Exception:
            return None

    def create(self, data):
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        data['status'] = 'baru'
        return self.collection.insert_one(data)

    def update_status(self, pesanan_id, status):
        return self.collection.update_one(
            {'_id': ObjectId(pesanan_id)},
            {'$set': {
                'status': status,
                'updated_at': datetime.utcnow()
            }}
        )

    def count_by_status(self, status):
        return self.collection.count_documents({'status': status})

    def delete(self, pesanan_id):
        return self.collection.delete_one({'_id': ObjectId(pesanan_id)})
