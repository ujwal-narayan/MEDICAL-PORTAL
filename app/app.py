

from flask import Flask, flash, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask import jsonify
from werkzeug import secure_filename
from flask_mail import Mail, Message
from threading import Thread



import bcrypt
import os
import datetime
import pdfkit

from app import app, model, db, mail
from app.model import User, Appointments, BankInfo, Reimbdata, PatintHealthRecord

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(' Reset Your Password',
               sender=app.config['MAIL_USERNAME'][0],
               recipients=[user.email],
               text_body=render_template('reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('reset_password_e.html',
                                         user=user, token=token))




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
                    events = []
                    docid = session['userid']
                    today = datetime.date.today()
                    week_after = today + datetime.timedelta(days=7)
                    date1 = today.strftime("%m/%d/%Y")
                    date2 = week_after.strftime("%m/%d/%Y")
                    docInfo =User.query.with_entities(User.starttime, User.endtime).filter_by(id=docid).first()
                    starttime = Appointments.AMPM_to_24(docInfo.starttime)+":00"
                    endtime = Appointments.AMPM_to_24(docInfo.endtime)+":00"
                    evlist =  Appointments.query.with_entities(Appointments.patient_id, Appointments.date, Appointments.slot).filter_by(doctor_id=docid).filter(Appointments.date.between(date1, date2)).all()
                    print(evlist)
                    for ev in evlist:
                        dt = ev.date.replace("/", "-")
                        sdt = dt + " " + ev.slot + ":00"
                        edt = datetime.datetime.strptime(sdt, "%m-%d-%Y %H:%M:%S")      
                        edt = edt + datetime.timedelta(minutes=15)
                        sdt = edt - datetime.timedelta(minutes=15)   
                        sdt =sdt.strftime("%Y-%m-%dT%H:%M:%S")
                        edt =edt.strftime("%Y-%m-%dT%H:%M:%S")
                        events.append(dict(title=('Patient'+str(ev.patient_id)), start=sdt, end=edt))
                    return render_template('doctor_index.html', eventlist=events, mintime=starttime, maxtime=endtime)
                if session['usertype'] == User.Admin:
                    print("Admin")
                    return redirect(url_for('admin_reimb'))
                if session['usertype'] == User.Patient:
                    print("Patient")
                    return redirect(url_for('finddoctor'))
            else:
                return render_template('index.html')
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


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
            if request.form['username'] == "admin":
                usertype = User.Admin
            else:
                usertype = User.Patient

            new_user = User(
                username=request.form['username'],
                usertype=usertype,
                email=request.form['email'],
                password=request.form['password'],
                dayavail='None',
                day_avail_s='None',
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
            avails1 = ",".join(day_avail_list)
            new_user = User(
                username=request.form['username'],
                usertype=User.Doctor,
                email=request.form['email'],
                password=request.form['password'],
                dayavail=avails,
                day_avail_s=avails1,
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


@app.route("/reset",methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        if  session.get('logged_in') is True :
            return redirect(url_for('home'))
        else:
            email=request.form['email']
            user = User.query.filter_by(email=email).first()
            if user:
                send_password_reset_email(user)
                flash("Reset email has been sent. Please check your email for further instructions")
            else:
                flash("User email not found . Try Again")
                return redirect(url_for('reset'))
            return redirect(url_for('login'))

    return render_template('reset_password_req.html',title="Password Reset")
    


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if session.get('logged_in'):
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    if user : 
        if request.method == 'POST':
            password=request.form['password']
            user.password=bcrypt.hashpw(
                password.encode('utf8'), bcrypt.gensalt())
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('login'))
    return render_template('reset_password.html',token=token)



@app.route("/finddoctor", methods=['GET', 'POST'])
def finddoctor():

    if request.method == 'GET':

        doctors = User.query.with_entities(User.id, User.username, User.hospital, User.email,User.dayavail, User.day_avail_s, User.starttime, User.endtime).filter_by(usertype=User.Doctor).all()
        print(doctors)
        # for doc in doctors:
        #     print(doc.day_avail_s)
        #     # print(doc)
        #     # print(doc.id)
        #     # print(doc.username)
        #     days =User.get_not_avail_days(doc.day_avail_s.split(","))
        #     print("update")
        #     id1 = doc.id
        #     print(id1)
        #     print(doc)
        #     User.query.filter_by(id=id1).update(dict(dayavail=days))
        #     db.session.commit()

        return render_template('finddoctor.html', doctors=doctors)



@app.route("/bookapt/<doctorname>", methods=['GET', 'POST'])
def bookapt(doctorname):
    try:
        if request.method == 'GET':
            print(doctorname)
            if doctorname != "none":
                print("doctorname")              
                doclist = User.query.with_entities(User.id, User.username, User.dayavail, User.starttime, User.endtime).filter_by(username=doctorname).all()
                docid = doclist[-1].id
                # print("docid")
                # print(docid)
                # print("dayavail")
                daylist = doclist[-1].dayavail.split(",")
                daylist = list(map(int, daylist))
                print("daylist")
                print(daylist)
            else:
                doclist = User.query.with_entities(User.id, User.username, User.dayavail, User.starttime, User.endtime).filter_by(usertype=User.Doctor).all()
                print(doclist)
                docid = doclist[-1].id
                doctorname=doclist[-1].username
                # print("docid")
                # print(docid)
                # print("dayavail")
                daylist = doclist[-1].dayavail.split(",")
                daylist = list(map(int, daylist))
                print("daylist")
                print(daylist)
            return render_template('bookapt.html',  docs=doclist,  daylist=daylist)
        else:
            print("POST")
            aptdate = request.form['aptdate']
            apttime = request.form['aptslot']
            aptdoc = request.form['aptdoc']
            username = session['username']
            patient = User.query.with_entities(User.id, User.email).filter_by(username=username).first()
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
            message = "Your appointment with " + aptdoc + " on " + aptdate + " at " + apttime + " is confirmed.\n" 
            msg = Message('Hello '+ username, sender = 'medicalportalprojecta@gmail.com', recipients = [patient.email])
            msg.body = message
            mail.send(msg)
            flash(message)
            return redirect(url_for('bookapt', doctorname="none"))
    except Exception as e:
        print(str(e))
        return render_template('bookapt.html',  docs=[],  daylist=[])



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
        # daylist = dlist[-1].dayavail.split()
        daylist = dlist[-1].dayavail.split(",")
        daylist = list(map(int, daylist))
        print("daylist")
        print(daylist)
        datelist =  Appointments.query.with_entities(func.count(Appointments.date), Appointments.date).filter_by(doctor_id=docid).all()
        max_slots = Appointments.get_max_slots(dlist[-1].starttime, dlist[-1].endtime)
        print("max_slots")
        print(max_slots)
        # print(datelist)
        final_list = []
        for date1 in datelist:
            print(date1[0])
            if date1[0] >= max_slots:
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
         username = session['username']
         userid = session['userid']
         dbinfo = BankInfo.query.with_entities(BankInfo.bankname, BankInfo.ifsc, BankInfo.acctname, BankInfo.acctnum).filter_by(user_id=userid).first()
         print(dbinfo)
         return render_template('reimbursemtform.html', dbinfo=dbinfo)
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
            if dbinfo:
                BankInfo.query.filter_by(user_id=userid).update(dict(bankname=bname, ifsc=bifsc, acctname=bactname, acctnum=bactnum))
                db.session.commit()
            else:
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
    binfo = BankInfo.query.with_entities(BankInfo.bankname, BankInfo.ifsc, BankInfo.acctname, BankInfo.acctnum).filter_by(user_id=userid).first()
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

@app.route("/admin_reimb", methods=['GET', 'POST'])
def admin_reimb():
    if request.method == 'GET':    
        try:
            userid = session['userid']
            session['currentdropdownpage'] = 'admin_reimb'
            # binfo = BankInfo.query.with_entities(BankInfo.bankname, BankInfo.ifsc, BankInfo.acctname, BankInfo.acctnum).filter_by(user_id=userid).all()
            # print(binfo)
            reimbs = Reimbdata.query.filter_by(status=Reimbdata.Pending).all()

            print("admin_index")
            # print(reimbs.user.username)
            # print(reimbs)
            print(reimbs)
            return render_template('admin_index.html', reimbs=reimbs)
        except Exception as e:
            print(str(e))
            return render_template('admin_index.html')
    else:
        print("POST")
        statusv = Reimbdata.Pending
        selected_rows = request.form.getlist("rowcheck")
        btnVal1 = request.form.get('Approve')
        print(btnVal1)
        if btnVal1:
            statusv = Reimbdata.Approved
        else:
            btnVal1 = request.form.get('Reject')
            if btnVal1:
                statusv = Reimbdata.Rejected

      
        # print(btnVal1)
        print(selected_rows)
        for id1 in selected_rows:
            print(id1)
            Reimbdata.query.with_entities(Reimbdata.id).filter_by(id=id1).update(dict(status=statusv))
            db.session.commit()
        return redirect(url_for('admin_reimb'))

@app.route("/admin_user_search", methods=['POST'])
def admin_user_search():    
    print("admin_user_search")
    
    username = session['username']
    userid = session['userid']
    if username != "admin":
        flash("not allowed")
    search_string = "%" + request.form["patientname"] +"%"
    print(search_string)
    session['search_string'] = search_string

    users = User.query.filter(User.username.like(search_string)).filter_by(usertype=User.Patient).all()
    print(users)
    if session['currentdropdownpage'] == 'admin_reimb':
        reimbs = []
        for user in users:
            data = user.receipts.all()
            reimbs.append(dict(user=user.username, receipts=data))

        print(reimbs)
        print("end_admin_user_search")
        return render_template('admin_search.html', reimbs=reimbs)
    else:
        hrecords = []
        for user in users:
            data = user.hrecords.all()
            # print(data)
            hrecords.append(dict(user=user.username, hrecords=data))

        # print(hrecords)
        print("end_admin_user_search")
        return render_template('admin_search_health.html', hrecords=hrecords)

@app.route("/admin_user_search_update", methods=['POST'])
def admin_user_search_update():    
    print("admin_user_search_update")
    print("POST")
    statusv = Reimbdata.Pending
    selected_rows = request.form.getlist("rowcheck")
    btnVal1 = request.form.get('Approve')
    print(btnVal1)
    if btnVal1:
        statusv = Reimbdata.Approved
    else:
        btnVal1 = request.form.get('Reject')
        if btnVal1:
            statusv = Reimbdata.Rejected
    # print(btnVal1)
    print(selected_rows)
    for id1 in selected_rows:
        print(id1)
        Reimbdata.query.with_entities(Reimbdata.id).filter_by(user_id=id1).update(dict(status=statusv))
        db.session.commit()

    search_string = session['search_string']
    users = User.query.filter(User.username.like(search_string)).all()
    print(users)
    reimbs = []
    for user in users:
        data = user.receipts.all()
        reimbs.append(dict(user=user.username, receipts=data))

    print(reimbs)
    print("end_admin_user_search_udate")
    return render_template('admin_search.html', reimbs=reimbs)
@app.route("/admin_user_health_search_update", methods=['POST'])
def admin_user_health_search_update():    
    print("admin_user_health_search_update")
    print("POST")
    selected_rows = request.form.getlist("rowcheck")
    print(selected_rows)
    for id1 in selected_rows:
        print(id1)
        users = User.query.filter_by(id=id1).first()
        record = PatintHealthRecord.query.order_by(PatintHealthRecord.date).filter_by(user_id=id1).first()
        print(users.username)
        rendered= render_template('admin_search_health_pdf.html', user=users.username, record=record)
        file = users.username + "_" + record.date.replace("/","_")+".pdf"
        pdfkit.from_string(rendered, file)

    search_string = session['search_string']

    users = User.query.filter(User.username.like(search_string)).all()
    print(users)
    hrecords = []
    for user in users:
        data = user.hrecords.all()
        hrecords.append(dict(user=user.username, hrecords=data))

    rendered = render_template('admin_search_health.html', hrecords=hrecords)
   

    print(hrecords)
    print("end_admin_user_health_search_update")
    return render_template('admin_search_health.html', hrecords=hrecords)
@app.route("/record_patient_vitals", methods=['GET', 'POST'])
def record_patient_vitals(): 
    if request.method == 'GET':    
        return render_template('record_patient_vitals.html')
    else:
        print("record_patient_vitals POST")
        patientname = request.form['patientname']
        user = User.query.with_entities(User.id).filter_by(username=patientname).first()
        print(user)
        # print(user.id)
        if user == None:
            flash("Patient Not found in Database.Please Register")
            return redirect(url_for('register'))

        bps = request.form['bpsystolic']
        bpd = request.form['bpdiastolic']
        hb = request.form['heartbeat']
        height = request.form['height']
        weight = request.form['weight']
        mallergic = request.form['AllergicMed']
        date1 = datetime.datetime.today().strftime("%m/%d/%Y")
        new_patient_hr = PatintHealthRecord(
                    user_id=user.id,
                    date=date1,
                    allergym=mallergic,
                    bpsys=bps,
                    bpdia=bpd,
                    heartbeat=hb,
                    height=height,
                    weight=weight)
        db.session.add(new_patient_hr)
        db.session.commit()
        listp = [patientname, bps, bpd, hb, height, weight, mallergic]
        print(listp)
        session['search_string']= patientname
        print( session['search_string'])
        return redirect(url_for('admin_health'))

@app.route("/admin_health", methods=['GET', 'POST'])
def admin_health(): 
    if request.method == 'GET':    
        try:
            # userid = session['userid']
            session['currentdropdownpage'] = 'admin_health'
            date1 = datetime.datetime.today().strftime("%m/%d/%Y")
            hrecords = PatintHealthRecord.query.filter_by(date=date1).all()

            print("admin_health")
            # print(reimbs.user.username)
            # print(reimbs)
            print(hrecords)
            return render_template('admin_health.html', hrecords=hrecords)
        except Exception as e:
            print(str(e))
            return render_template('admin_health.html')
    else:
        print("POST")
        selected_rows = request.form.getlist("rowcheck")
        print(selected_rows)
        for id1 in selected_rows:
            print(id1)
            date1 = datetime.datetime.today().strftime("%m/%d/%Y")
            userrep = PatintHealthRecord.query.filter_by(date=date1).filter_by(user_id=id1).all()
            print(userrep)
        return redirect(url_for('admin_health'))
   

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run()
