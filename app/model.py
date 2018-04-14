from datetime import datetime, timedelta
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

    def __repr__(self):  return "<User(username ='%s', usertype='%s',,dayavail='%s', starttime='%s', endtime='%s', hospital='%s',)>" % (
            self.username, self.usertype,  self.dayavail, self.starttime,
            self.endtime, self.hospital)

    def get_not_avail_days(day_avail_list):
        day_not_avail = [1 for x in range(7)]
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

    def __init__(self, date, slot, patient_id, doctor_id):
        self.date = date
        self.slot = slot
        self.patient_id = patient_id
        self.doctor_id = doctor_id

    def get_slots_avail(starttime, endtime, slotlist, slot_time=15):
        eh = endtime.split(":")
        ehi = int(eh[0])+12 
        etime = str(ehi) + ":" + eh[1][0:-3]
        time = datetime.strptime(starttime[0:-3], '%H:%M')
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
        if time[-2] == "P":
            eh =  time.split(":")
            ehi = int(eh[0])+12 
            return str(ehi) + ":" + eh[1][0:-3]
        else:
            return time[0:-3]

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
        return (em-sm)/15
        
    def __repr__(self):  return "<Appointments(date ='%s', slot='%s' )>" % (self.date, self.slot)
