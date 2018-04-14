

from flask import Flask, flash, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask import jsonify

import bcrypt
import os
import datetime

from app import app, model, db
from app.model import User, Appointments

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get(
#     'SECRET_KEY') or 'you-will-never-guess'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)




@app.route('/', methods=['GET'])
def home():
    """ Session control"""
    if 'logged_in' in session:
        if not session['logged_in']:
            return render_template('index.html')
        else:
            if 'usertype' in session:
                if session['usertype'] == User.Doctor:
                    return render_template('doctor_index.html')
            else:
                return render_template('index.html')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        try:
            data = User.query.filter_by(username=name).first()
            print(User.Doctor)
            print(User.days)
            if data is not None:
                if bcrypt.checkpw(passw.encode('utf8'),
                                  data.password):
                    session['logged_in'] = True
                    session['username'] = name
                    session['usertype'] = data.usertype
                    return redirect(url_for('home'))
                else:

                    error = "Incorrect password.Please Try Again."
                    # return redirect(url_for('login'))
                    return render_template('login.html', error=error)

            else:
                error = 'User was not found. Please register \
                before trying again'
                # return redirect(url_for('login'))
                return render_template('login.html', error=error)

        except Exception as e:
            print(str(e))
            error = "An Error was encountered please try again"
            # return redirect(url_for('login'))
            return render_template('login.html', error=error)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        try:
            new_user = User(
                username=request.form['username'],
                usertype=User.Patient,
                email=request.form['email'],
                password=request.form['password'],
                dayavail='None',
                starttime='None',
                endtime='None',
                hospital='None')
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
        except Exception as e:
            print(str(e))
            error = "Error.Username unavailable.Please try again \
            with a different username"
            return render_template('register.html', error=error)
    return render_template('register.html')


@app.route('/register_doctor/', methods=['GET', 'POST'])
def register_doctor():
    """Register Form"""
    
    if request.method == 'GET':
        return render_template('register_doctor.html', days=User.days)
    elif request.method == 'POST':
        try:
            day_avail_list = request.form.getlist('docavail')
            avails = User.get_not_avail_days(day_avail_list)
            print(avails);
            # avails = ",".join(day_avail_list)
            new_user = User(
                username=request.form['username'],
                usertype=User.Doctor,
                email=request.form['email'],
                password=request.form['password'],
                dayavail=avails,
                starttime=request.form['timestart'],
                endtime=request.form['timeend'],
                hospital=request.form['hospitalname'])
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
        except Exception as e:
            print(str(e))
            error = "Error.Username unavailable.Please try again \
            with a different username"
            return render_template('register_doctor.html', error=error, days=User.days)
    return render_template('register_doctor.html',days=User.days)


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    session.pop('username', None)
    session.pop('usertype', 0)
    return redirect(url_for('home'))


@app.route("/finddoctor")
def finddoctor():
    return render_template('finddoctor.html')


@app.route("/bookapt", methods=['GET', 'POST'])
def bookapt():
    if request.method == 'GET':
        doclist = User.query.with_entities(User.id, User.username, User.dayavail, User.starttime, User.endtime).filter_by(usertype=User.Doctor).all()
        docid = doclist[-1].id
        # print("docid")
        # print(docid)
        # print("dayavail")
        daylist = doclist[-1].dayavail
        print(daylist)
        
        return render_template('bookapt.html',  docs=doclist,  daylist=daylist)
    else:
        print("POST")
        aptdate = request.form['aptdate']
        apttime = request.form['aptslot']
        aptdoc = request.form['aptdoc']
        username = session['username']
        patient = User.query.with_entities(User.id).filter_by(username=username).first()
        doc = User.query.with_entities(User.id).filter_by(username=aptdoc).first()
        print(patient.id)
        print(doc.id)
        print(aptdate)
        print(apttime)
        print(aptdoc)
        new_apt = Appointments(
                date=aptdate,
                slot=apttime,
                patient_id=patient.id,
                doctor_id=doc.id)
        db.session.add(new_apt)
        db.session.commit()
 
        flash('Your appointment is added, you will get confiramtion email shortly')
        return redirect(url_for('bookapt'))

@app.route('/_get_slots/')
def _get_slots():
    try:
        doc = request.args.get('doctor', '01', type=str)
        # print("get_slots")
        # print(doc)
        doclist = User.query.with_entities(User.id, User.starttime, User.endtime).filter_by(username=doc).all()
        docid = doclist[-1].id
        date = request.args.get('date1', '01', type=str)
        # print(doc)
        # print(date)
        slotlist =  Appointments.query.with_entities(Appointments.slot).filter_by(doctor_id=docid).filter_by(date=date).all()
        # print(slotlist)
        slist = Appointments.get_slots_avail(doclist[-1].starttime, doclist[-1].endtime, slotlist, 15)
        print(slist)
   
    except Exception as e:
        print(str(e))
        # print("beforeflash")
        # flash('Not available please select different day')
        return jsonify([])

    return jsonify(slist)
@app.route('/_get_dates/')
def _get_dates():
    try:
        datelist = []
        daylist = []
        doc = request.args.get('doctor', '01', type=str)
        # print("get_dates")
        # print(doc)
        dlist = User.query.with_entities(User.id, User.dayavail, User.starttime, User.endtime).filter_by(username=doc).all()
        docid = dlist[-1].id
        daylist = dlist[-1].dayavail.split()
        datelist =  Appointments.query.with_entities(func.count(Appointments.date), Appointments.date).filter_by(doctor_id=docid).all()
        max_slots = Appointments.get_max_slots(dlist[-1].starttime, dlist[-1].endtime)
        print("max_slots")
        print(max_slots)
        # print(datelist)
        final_list = []
        for date1 in datelist:
            print(date1[0])
            if date1[0] >= 10:
                final_list.append(date1.date)
        print(daylist)
        print(final_list)
       
    except Exception as e:
         print(str(e))
         flash('Not available please select different doctor')
         return jsonify({"dates":[]}, {"days":[]})
    

    return jsonify({"dates":final_list}, {"days":daylist})

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run()
