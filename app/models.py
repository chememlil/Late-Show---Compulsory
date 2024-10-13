from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

appearances_tables = db.Table(
    'appearances_tables',
    db.Column('episode_id', db.ForeignKey('episodes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('guest_id', db.ForeignKey('guests.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class Episodes(db.Model, SerializerMixin):
    __tablename__ = 'episodes'

    serialize_rules = ('-guests.episodes',)
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    appearances = db.relationship('Appearances', backref=db.backref('episode'), cascade='all, delete-orphan')
    guests = db.relationship('Guests', secondary=appearances_tables, back_populates='episodes', cascade='all, delete')


class Appearances(db.Model, SerializerMixin):
    __tablename__ = 'appearances'

    serialize_rules=('-episode.appearances', '-guest.appearances',)

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    episode_id = db.Column(db.Integer, db.ForeignKey('episodes.id', ondelete="CASCADE"))
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'))

    @validates('rating')
    def validate_rating(self, key, value):
        if value > 5 or value < 0:
            raise ValueError('Rating must be between 5 and 0')
        return value


class Guests(db.Model, SerializerMixin):
    __tablename__ = 'guests'

    serialize_rules = ('-appearances.guest', '-episodes.guests')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    occupation =db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    appearances = db.relationship('Appearances', backref='guest')
    episodes = db.relationship('Episodes', secondary=appearances_tables, back_populates='guests')
