from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

UserEvent = db.Table('UserEvent',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class Event(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(10000), unique=True)
	datestart = db.Column(db.String(10000))
	dateclose = db.Column(db.String(10000))
	detail = db.Column(db.String(10000))

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), unique=True)
	email = db.Column(db.String(150), unique=True)
	password = db.Column(db.String(150), nullable=False)
	level = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
	active = db.Column(db.Integer, default=0, nullable=False)
	child = db.relationship('Profiles', backref='parent', uselist=False)
	UserEvent = db.relationship('Event', secondary=UserEvent, lazy='subquery', backref=db.backref('users', lazy=True))

class Profiles(db.Model):
	id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	firstname = db.Column(db.String(150), nullable=False)
	lastname  = db.Column(db.String(150))
	image = db.Column(db.String(10000))
	gender = db.Column(db.Enum("Pria", "Wanita"))
	address = db.Column(db.String(10000))
	phone = db.Column(db.Integer)
	


