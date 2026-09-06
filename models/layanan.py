from bson import ObjectId


class Layanan:
    def __init__(self, db):
        self.collection = db['layanan']

    def all_aktif(self):
        return list(self.collection.find({'aktif': True}).sort('nama_jasa', 1))

    def all(self):
        return list(self.collection.find().sort('nama_jasa', 1))

    def get(self, layanan_id):
        try:
            return self.collection.find_one({'_id': ObjectId(layanan_id)})
        except Exception:
            return None

    def create(self, nama_jasa, kategori, harga_kisaran, deskripsi, aktif=True):
        return self.collection.insert_one({
            'nama_jasa': nama_jasa,
            'kategori': kategori,
            'harga_kisaran': harga_kisaran,
            'deskripsi': deskripsi,
            'aktif': aktif
        })

    def update(self, layanan_id, data):
        return self.collection.update_one(
            {'_id': ObjectId(layanan_id)},
            {'$set': data}
        )

    def delete(self, layanan_id):
        return self.collection.delete_one({'_id': ObjectId(layanan_id)})
