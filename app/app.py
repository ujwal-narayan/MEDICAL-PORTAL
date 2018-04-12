

from flask import Flask, flash, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify

import bcrypt
import os
import datetime

from app import app, model, db
from app.model import User

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get(
#     'SECRET_KEY') or 'you-will-never-guess'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)




@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
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
            print(data)
            if data is not None:
                if bcrypt.checkpw(passw.encode('utf8'),
                                  data.password):
                    session['logged_in'] = True
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
    days = ['Weekdays', 'Sat', 'Sun', 'Mon-Thu']
    if request.method == 'GET':
        return render_template('register_doctor.html', days=days)
    elif request.method == 'POST':
        try:
            day_avail_list = request.form.getlist('docavail')
            day_not_avail = [1 for x in range(7)]
            for day in day_avail_list:
                print(day)
                if day == days[0]:
                    i = 1
                    while i <= 5:
                        day_not_avail[i] = 0
                        i += 1
                print(day_not_avail)
                if day == days[1]:
                    day_not_avail[6] =0
                if day == days[2]:
                    day_not_avail[0] =0
                if day == days[3]:
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

            print(avails);
            # avails = ",".join(day_avail_list)
            new_user = User(
                username=request.form['username'],
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
            return render_template('register_doctor.html', error=error, days=days)
    return render_template('register_doctor.html',days=days)


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))


@app.route("/finddoctor")
def finddoctor():
    return render_template('finddoctor.html')


@app.route("/bookapt", methods=['GET', 'POST'])
def bookapt():
    if request.method == 'GET':
        docs = ['Doctor1', 'Doctor2', 'Doctor3']
        tlist = {
                 'Doctor1':['8:15', '10:15', '13:15'],
                 'Doctor2':['8:30', '10:40', '13:40'],
                 'Doctor3':['14:15', '15:15', '16:15']
        }
        # start_time = '8:00'
        # end_time = '17:00'
        # slot_time = 15
        # time = datetime.datetime.strptime(start_time, '%H:%M')
        # end = datetime.datetime.strptime(end_time, '%H:%M')
        # slots = []
        # while time <= end:
        #     print(time)
        #     slots.append(time.strftime("%H:%M"))
        #     time += datetime.timedelta(minutes=slot_time)
        # print(slots)
        return render_template('bookapt.html',  docs=docs, slots=tlist['Doctor3'])
        # return render_template('bookapt.html')
    else:
        aptdate = request.form['aptdate']
        apttime = request.form['aptslot']
        aptdoc = request.form['aptdoc']
        print(aptdate)
        print(apttime)
        print(aptdoc)
        flash('Your appointment is added, you will get confiramtion email shortly')
        return redirect(url_for('bookapt'))

@app.route('/_get_slots/')
def _get_slots():
    doc = request.args.get('date1', '01', type=str)
    print(doc)
    dates = ['04/20/2018', '04/12/2018', '04/16/2018']
    tlist = {
             '06/20/2018':['8:15', '10:15', '13:15'],
             '04/12/2018':['8:30', '10:40', '13:40'],
             '05/16/2018':['14:15', '15:15', '16:15'],
             '07/20/2018':['9:15', '14:15', '18:15']
    }
    # counties = [(row.ID, row.Name) for row in County.query.filter_by(state=state).all()]
    try:
        list1 = tlist[doc]
    except:
        # print("beforeflash")
        # flash('Not available please select different day')
        return jsonify([])

    return jsonify(list1)
@app.route('/_get_dates/')
def _get_dates():
    doc = request.args.get('doctor', '01', type=str)
    print(doc)
    docs = ['Doctor1', 'Doctor2', 'Doctor3']
    tlist = {
             'Doctor1':['4/20/2018', '4/19/2018', '4/18/2018'],
                        
             'Doctor2':['5/21/2018', '5/23/2018', '5/22/2018'],
                        
             'Doctor3':['6/20/2018', '6/22/2018', '6/23/2018'],
                        
    }
    dlist = {
             'Doctor1':[0,6],
                        
             'Doctor2':[0,5,6],
                        
             'Doctor3':[1,2,3,4],
    }
    # counties = [(row.ID, row.Name) for row in County.query.filter_by(state=state).all()]
    try:
        list1 = tlist[doc]
        dlist1 = dlist[doc]
    except:
         flash('Not available please select different doctor')
         return jsonify({"dates":list1}, {"days":dlist1})


    return jsonify({"dates":list1}, {"days":dlist1})

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run()
