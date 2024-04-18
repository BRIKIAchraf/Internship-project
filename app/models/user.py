from enum import Enum
from app import db

class LoginMethod(Enum):
    PassOrFingerOrCard = "PassOrFingerOrCard"
    Card = "Card"
    FingerAndPass = "FingerAndPass"
    # ... add other methods as needed

class User(db.Model):
    __tablename__ = 'users'

    uid = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, unique=True, nullable=False)
    template = db.Column(db.String, nullable=True)
    login_method = db.Column(db.Enum(LoginMethod), nullable=False)
    
    # Additional fields can be added as needed

    def serialize(self):
        return {
            'uid': self.uid,
            'user_id': self.user_id,
            'template': self.template,
            'login_method': self.login_method.value
        }

    def __init__(self, uid, user_id, template, login_method):
        self.uid = uid
        self.user_id = user_id
        self.template = template
        self.login_method = LoginMethod(login_method)

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def create(data):
        user = User(
            uid=data.get('uid'),
            user_id=data.get('user_id'),
            template=data.get('template'),
            login_method=LoginMethod(data.get('login_method'))
        )
        return user
