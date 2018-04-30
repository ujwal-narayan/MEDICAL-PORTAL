from datetime import datetime, timedelta
from app import db,app
import bcrypt
import os
from sqlalchemy.orm import backref
import jwt
import time


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
    day_avail_s = db.Column(db.String(128))
    starttime = db.Column(db.String(80))
    endtime = db.Column(db.String(80))
    hospital = db.Column(db.String(255))
    receipts = db.relationship('Reimbdata', backref='submitter', lazy='dynamic')
    hrecords = db.relationship('PatintHealthRecord', backref='patient', lazy='dynamic')



    def __init__(self, username, usertype, email, password, dayavail, day_avail_s, starttime, endtime, hospital):
        print(usertype)
        self.username = username
        self.usertype = usertype
        self.email = email
        self.password = bcrypt.hashpw(
            password.encode('utf8'), bcrypt.gensalt())
        self.dayavail = dayavail
        self.day_avail_s = day_avail_s
        self.starttime = starttime
        self.endtime = endtime
        self.hospital = hospital

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)

    def __repr__(self):  return "<User(username ='%s', usertype='%s',,dayavail='%s', starttime='%s', endtime='%s', hospital='%s',)>" % (
            self.username, self.usertype,  self.dayavail, self.starttime,
            self.endtime, self.hospital)

    def get_not_avail_days(day_avail_list):
        day_not_avail = [1 for x in range(7)]
        # print(day_not_avail)
        for day in day_avail_list:
            if day == User.days[0]:
                i = 1
                while i <= 5:
                    day_not_avail[i] = 0
                    i += 1
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
        print(day_not_avail)
        avails = []
        while i<=6:
            if day_not_avail[i] == 1:
                 avails.append(str(i))
            i +=1
        # print("get_not_avail_days")
        # print(avails)
        avails2 = ",".join(avails)
        # print(avails2)

        return (avails2)

    def get_reset_password_token(self, expires_in=600):
       return jwt.encode(
           {'reset_password': self.id, 'exp': time.time() + expires_in},
           app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(140))
    slot = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, date, slot, patient_id, doctor_id):
        self.date = date
        self.slot = slot
        self.patient_id = patient_id
        self.doctor_id = doctor_id

    def get_slots_avail(starttime, endtime, slotlist, slot_time=15):
        # eh = endtime.split(":")
        # print(eh[1][-2])
        # if eh[1][-2] == "P":
        #     ehi = int(eh[0])+12 
        # else:
        #     ehi = int(eh[0])
        etime = Appointments.AMPM_to_24(endtime)
        stime = Appointments.AMPM_to_24(starttime)
        time = datetime.strptime(stime, '%H:%M')
        end = datetime.strptime(etime, '%H:%M')
        slots = []
        found = 0
        while time <= end:
            slot = time.strftime("%H:%M")
            for s in slotlist:
                if slot == s[-1]:
                     found = 1
                     print("found")
                     break;
            if found == 0:
                slots.append(slot)
            else:
                found = 0
            time += timedelta(minutes=slot_time)
        print(slots)
        return slots

    def AMPM_to_24(time):
        eh =  time.split(":")
        ehi = int(eh[0])
        if time[-2] == "P":
            if int(eh[0]) != 12:
                ehi += 12 
        else:
            if int(eh[0]) == 12:
                ehi = 0
        return str(ehi) + ":" + eh[1][0:-3]

    def hm_to_mins(t):
        h, m = [int(i) for i in t.split(':')]
        return 60*h + m

    def get_max_slots(starttime, endtime, slot_time=15):
        st = Appointments.AMPM_to_24(starttime)
        et = Appointments.AMPM_to_24(endtime)
        print(st)
        print(et)
        sm = Appointments.hm_to_mins(st)
        em = Appointments.hm_to_mins(et)
        return abs((em-sm))/15
        
    def __repr__(self):  return "<Appointments(date ='%s', slot='%s' )>" % (self.date, self.slot)

class BankInfo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bankname= db.Column(db.String(80))
    ifsc = db.Column(db.String(80))
    acctname = db.Column(db.String(80))
    acctnum    = db.Column(db.String(128))
  

    def __init__(self, user_id, bankname, ifsc, acctname, acctnum):
        self.user_id = user_id
        self.bankname = bankname
        self.ifsc=ifsc
        self.acctname = acctname
        self.acctnum = acctnum

    def __eq__(self, other):
        return self.bankname == other.bankname and self.ifsc == other.ifsc and self.acctname == other.acctname and self.acctnum == other.acctnum
    

    def __repr__(self):  return "<BankInfo(user_id ='%s', bankname='%s',,acctname='%s', acctnum='%s,)>" % (
            self.user_id, self.bankname,  self.acctname, self.acctnum)

class Reimbdata(db.Model):

    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # create_user = db.relationship("User", foreign_keys=user_id)
    brno = db.Column(db.String(80))
    date = db.Column(db.String(80))
    amount = db.Column(db.String(128))
    status = db.Column(db.String(80))

    # brfile = db.Column(db.String(255))
  

    def __init__(self, user_id, brno, date, amount, status):
        self.user_id = user_id
        self.brno = brno
        self.date = date
        self.amount = amount
        self.status = status
    

    def __repr__(self):  return "<Reimbdata(user_id ='%s', brno='%s',,date='%s', amount='%s, status=%s)>" % (
            self.user_id, self.brno,  self.date, self.amount, self.status)

class PatintHealthRecord(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(80))
    allergym = db.Column(db.String(255))
    bpsys = db.Column(db.Integer)
    bpdia = db.Column(db.Integer)
    heartbeat = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)



    def __init__(self, user_id, date, allergym, bpsys, bpdia, heartbeat, height, weight):
        self.user_id = user_id
        self.date = date
        self.allergym = allergym
        self.bpsys = bpsys
        self.bpdia = bpdia
        self.heartbeat = heartbeat
        self.height = height
        self.weight = weight


    def __repr__(self):  return "<PatintHealthRecord(user_id ='%s', date='%s',,allergym='%s', bpsys='%s', bpdia='%s', heartbeat='%s',)>" % (
            self.user_id, self.date,  self.allergym, self.bpsys,
            self.bpdia, self.heartbeat)
