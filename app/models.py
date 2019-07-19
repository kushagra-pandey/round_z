from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime
from hashlib import md5
'''
StartupInvestor = db.Table('StartupInvestor', db.Model.metadata,
                       db.Column('startup_id', db.Integer, db.ForeignKey('startup.id')),
                       db.Column('investor_id', db.Integer, db.ForeignKey'''

class StartupInvestor(db.Model):
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    investment_amount = db.Column(db.Float)
    investor = db.relationship('User', backref=db.backref('investments'))

class Startup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    capital_raised = db.Column(db.Float, default=0)
    #investors = db.relationship('User', secondary=StartupInvestor, backref='Investment')
    investors = db.relationship('StartupInvestor', backref=db.backref('startup'))
    founder_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    logo = db.Column(db.BLOB)
    description = db.Column(db.String(140))
    def __repr__(self):
        return '<Company {}>'.format(self.name)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    startups = db.relationship('Startup', backref='founder', lazy='dynamic')
    #investments = db.relationship('Startup', secondary=StartupInvestor, backref='Investor')
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
