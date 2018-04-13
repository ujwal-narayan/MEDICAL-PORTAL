from datetime import datetime
from app import db
import bcrypt
import os


class User(db.Model):
    """ Create user table"""
    Doctor =1
    Admin = 2
    Patient = 3
    days = ['Weekdays', 'Sat', 'Sun', 'Mon-Thu']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    usertype = db.Column(db.Integer)
    password = db.Column(db.String(80))
    email    = db.Column(db.String(128))
    dayavail = db.Column(db.String(128))
    starttime = db.Column(db.String(80))
    endtime = db.Column(db.String(80))
    hospital = db.Column(db.String(255))

    def __init__(self, username, usertype, email, password, dayavail, starttime, endtime, hospital):
        print(usertype)
        self.username = username
        self.usertype = usertype
        self.email = email
        self.password = bcrypt.hashpw(
            password.encode('utf8'), bcrypt.gensalt())
        self.dayavail = dayavail
        self.starttime = starttime
        self.endtime = endtime
        self.hospital = hospital

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)

    def __repr__(self):  return "<User(username ='%s', usertype='%s', email='%s', password='%s',dayavail='%s', starttime='%s', endtime='%s', hospital='%s',)>" % (
            self.username, self.usertype, self.email, self.password, self.dayavail, self.starttime,
            self.endtime, self.hospital)

    def get_not_avail_days(day_avail_list):
        day_not_avail = [1 for x in range(7)]
        for day in day_avail_list:
            print(day)
            if day == User.days[0]:
                i = 1
                while i <= 5:
                    day_not_avail[i] = 0
                    i += 1
            print(day_not_avail)
            if day == User.days[1]:
                day_not_avail[6] =0
            if day == User.days[2]:
                day_not_avail[0] =0
            if day == User.days[3]:
                i = 1
                while i<=4:
                    day_not_avail[i] = 0
                    i +=1
        i =0
        avails = ""
        while i<=6:
            if day_not_avail[i] == 1:
                 avails += str(i)
            i += 1
        return avails

class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(140))
    slot = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, date, slot, userid, doctorid):
        self.date = date
        self.slot = slot
        self.patient_id = patient_id
        self.doctor_id = doctor_id

    def __repr__(self):  return "<Appointments(date ='%s', slot='%s' )>" % (self.date, self.slot)
