# app/models/department.py
from app import db

# Association table for the many-to-many relationship between users and departments
user_departments = db.Table('user_departments',
    db.Column('user_id', db.String, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('departments.id'), primary_key=True)
)

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    users = db.relationship('User', secondary=user_departments, backref=db.backref('departments', lazy=True))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_ids': [user.user_id for user in self.users]
        }
