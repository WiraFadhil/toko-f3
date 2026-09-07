import re
from datetime import datetime

KATA_KELUHAN = (
    'keluhan', 'komplain', 'kecewa', 'kecewwa', 'rusak', 'jelek', 'buruk',
    'lambat', 'telat', 'lama banget', 'salah', 'tidak sesuai', 'nggak sesuai',
    'gagal', 'batal', 'merepotkan', 'jebol', 'robek', 'cacat', 'tidak puas',
    'nggak puas', 'mau refund', 'ganti rugi', 'balikin', 'masalah', 'error',
    'tolong dibantu', 'kok bisa', 'kenapa belum', 'mana pesanan', 'saya komplain',
)


def is_keluhan_message(text):
    t = (text or '').lower()
    return any(k in t for k in KATA_KELUHAN)


def extract_no_wa(text):
    t = (text or '').replace('-', '').replace(' ', '').replace('.', '').replace(',', '').replace('+', '')
    m = re.search(r'(?<!\d)(?:08\d{7,12}|8\d{8,12}|62\d{8,13})(?!\d)', t)
    if not m:
        return ''
    n = m.group(0)
    if n.startswith('08'):
        return '62' + n[1:]
    if n.startswith('8'):
        return '62' + n
    return n


def extract_nama(text):
    t = (text or '').strip()
    m = re.match(r'^(?:nama|saya|aku)\s+(?:saya|aku|namaku|nama saya)?\s*:?\s*([A-Za-z ]{2,40})$', t, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ''


class ChatLog:
    def __init__(self, db):
        self.collection = db['chat_logs']

    def create(self, message, reply, gambar, provider, is_keluhan, error=None, nama=None, no_wa=None):
        return self.collection.insert_one({
            'message': message,
            'reply': reply,
            'gambar': gambar or [],
            'provider': provider,
            'is_keluhan': bool(is_keluhan),
            'error': error,
            'nama': nama or '',
            'no_wa': no_wa or '',
            'ip': '',
            'created_at': datetime.utcnow(),
        })

    def all(self, keluhan_only=False, limit=200):
        query = {'is_keluhan': True} if keluhan_only else {}
        return list(self.collection.find(query).sort('created_at', -1).limit(limit))

    def count_keluhan(self):
        return self.collection.count_documents({'is_keluhan': True})