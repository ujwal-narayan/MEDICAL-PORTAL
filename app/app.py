

from flask import Flask, flash, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask import jsonify
from werkzeug import secure_filename


import bcrypt
import os
import datetime

from app import app, model, db
from app.model import User, Appointments, BankInfo, Reimbdata

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
        print("login in session")
        if not session['logged_in']:

            print("not session logged in")
            return render_template('index.html')
        else:
            if 'usertype' in session:
                print("usertype in sessiom")
                if session['usertype'] == User.Doctor:
                    print("doctor")
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
                    session['userid']  = data.id
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
    session.pop('userid', 0)
    return redirect(url_for('home'))


@app.route("/finddoctor")
def finddoctor():
    return render_template('finddoctor.html')


@app.route("/calendar")
def calendar():
    return render_template('calendar.html')


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

@app.route("/reimbursemtform", methods=['GET', 'POST'])
def reimbursemtform():
    if request.method == 'GET':
        
        return render_template('reimbursemtform.html')
    else:
        print("POST")
        try:
            username = session['username']
            userid = session['userid']
            brno = request.form["brno"]
            brsdate = request.form["brsdate"]
            bramt = request.form["bramt"]
            date1 = brsdate.replace("/", "_")
            filename = username + "_" + brno +"_" + date1
            print(filename)
            dreimb = Reimbdata.query.with_entities(Reimbdata.user_id).filter_by(user_id=userid).filter_by(brno=brno).first()
            if dreimb:
                flash("This Bill Receipt is already submitted.Check status and enter new one")
                return redirect(url_for('reimbursemtform'))

            errmsg = validate_file(request, filename)
            if errmsg != "valid":
                flash(errmsg)
                return redirect(url_for('reimbursemtform'))

            file = request.files['file']
            filename = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_reimb_data = Reimbdata(
                    user_id=userid,
                    brno=brno,
                    date=brsdate,
                    amount=bramt,
                    status=Reimbdata.Pending)
            db.session.add(new_reimb_data)
            db.session.commit()


            userid = session['userid']
            bname = request.form["bname"]
            bifsc =request.form["bifsc"]
            print(bifsc)
            bactname =request.form["bactname"]
            bactnum = request.form["bactnum"]
            dbinfo = BankInfo.query.with_entities(BankInfo.bankname, BankInfo.ifsc, BankInfo.acctname, BankInfo.acctnum).filter_by(user_id=userid).first()
            insert = True
            if dbinfo and dbinfo.bankname == bname and dbinfo.ifsc == bifsc and dbinfo.acctname == bactname and dbinfo.acctnum == bactnum:
                insert = False
            if insert == True:
                new_bank_info = BankInfo(
                    user_id=userid,
                    bankname=bname,
                    ifsc=bifsc,
                    acctname=bactname,
                    acctnum=bactnum)
                db.session.add(new_bank_info)
                db.session.commit()


        except Exception as e:
            print(str(e))
    
        return redirect(url_for('home'))

@app.route("/checkreimbursemntstatus", methods=['GET'])
def checkreimbursemntstatus():
    userid = session['userid']
    binfo = BankInfo.query.with_entities(BankInfo.bankname, BankInfo.ifsc, BankInfo.acctname, BankInfo.acctnum).filter_by(user_id=userid).all()
    print(binfo)
    reimbs = Reimbdata.query.with_entities(Reimbdata.brno, Reimbdata.date, Reimbdata.amount, Reimbdata.status).filter_by(user_id=userid).all()
    print(reimbs)
    return render_template('checkreimbstatus.html', binfo=binfo, reimbs=reimbs)
    

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(request, filename):
    errmsg =""
    try:
       
        print(request.url)
        # check if the post request has the file part
        if 'file' not in request.files:
            errmsg = "No file part"
            # flash('No file part')
            # return redirect(request.url)
        file = request.files['file']
        print(file)
        

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            errmsg = "No selected file"
            # flash('No selected file')
            # return redirect(request.url)
        fwext = file.filename.split(".")
        print(fwext[0])
        if fwext[0] != filename:
            errmsg = "please rename file to " + filename + "submit"
            return errmsg

        if file and allowed_file(file.filename):
            return "valid"
    except Exception as e:
        print(str(e))
        return str(e)
    return "supported extensions are gif, txt, pdf, png, jpg"

def upload(request, filename):
    errmsg =""
    try:
        if request.method == 'POST':
            print("post")
            print(request.url)
            # check if the post request has the file part
            if 'file' not in request.files:
                errmsg = "No file part"
                # flash('No file part')
                # return redirect(request.url)
            file = request.files['file']
            print(file)
            if file != filename:
                errmsg = "please rename file to " + filename + "submit"
                return errmsg

            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                errmsg = "o selected file"
                # flash('No selected file')
                # return redirect(request.url)
            if file and allowed_file(file.filename):
                print("allowed")
                filename = secure_filename(file.filename)
                print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return errmsg
    except Exception as e:
        print(str(e))
    return  errmsg

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run()
