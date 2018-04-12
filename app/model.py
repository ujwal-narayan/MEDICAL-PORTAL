from datetime import datetime
from app import db
import bcrypt
import os


class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    dayavail = db.Column(db.String(128))
    starttime = db.Column(db.String(80))
    endtime = db.Column(db.String(80))
    hospital = db.Column(db.String(255))

    def __init__(self, username, password, dayavail, starttime, endtime, hospital):
        self.username = username
        self.password = bcrypt.hashpw(
            password.encode('utf8'), bcrypt.gensalt())
        self.dayavail = dayavail
        self.starttime = starttime
        self.endtime = endtime
        self.hospital = hospital

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)

    def __repr__(self): return "<User(username ='%s', password='%s',\
    dayavail='%s', starttime='%s', endtime='%s', hospital='%s',)>" % (
        self.username, self.password, self.dayavail, self.starttime,
        self.endtime, self.hospital)
