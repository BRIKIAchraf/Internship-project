from datetime import datetime
from app import db

class Device(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    mac = db.Column(db.String(255), unique=True, nullable=False)
    inet = db.Column(db.String(255), nullable=False)
    lastCheckedAt = db.Column(db.DateTime, default=datetime.utcnow)
    lastActiveAt = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(255), nullable=True)

    def __init__(self, mac, id, name=None):
        self.id = id
        self.mac = mac
        self.name = name

    def serialize(self):
        return {
            'mac': self.mac,
            'id': self.id,
            'inet': self.inet,
            'lastCheckedAt': self.lastCheckedAt,
            'lastActiveAt': self.lastActiveAt,
            'name': self.name
        }
