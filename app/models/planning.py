# app/models/planning.py
from app import db
from datetime import datetime

class DayTimeBlock(db.Model):
    __tablename__ = 'day_time_blocks'

    id = db.Column(db.Integer, primary_key=True)
    planning_id = db.Column(db.Integer, db.ForeignKey('plannings.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # E.g., 'Monday', 'Tuesday', etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class Planning(db.Model):
    __tablename__ = 'plannings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'), nullable=True)
    time_blocks = db.relationship('DayTimeBlock', backref='planning', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'user_id': self.user_id,
            'time_blocks': [block.serialize() for block in self.time_blocks]
        }

class DayTimeBlock(db.Model):
    __tablename__ = 'day_time_blocks'

    id = db.Column(db.Integer, primary_key=True)
    planning_id = db.Column(db.Integer, db.ForeignKey('plannings.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # E.g., 'Monday', 'Tuesday', etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def serialize(self):
        return {
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M')
        }
