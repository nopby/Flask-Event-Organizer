from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Event, Users, Profiles
from . import db

#INISIAL VIEWS
views = Blueprint("views", __name__, static_folder="static", template_folder="Templates")
flag = False
log = False
#RUTE HOME DAN DASHBOARD
@views.route('/')
def home():
    #READ EVENT
    events = Event.query.all()
    if current_user.is_authenticated:
        user = Users.query.filter_by(id=current_user.id).first()
        user.active = 1
        db.session.commit()
        user_event = Event.query.join(Event.users).filter_by(id=current_user.id).all()
        return render_template("dashboard.html", page='Dashboard', user=current_user, events=events, user_event=user_event)
    else:
        return render_template("index.html", page="Index", user=current_user, events=events)

#=============================================BAGIAN AUTH==============================================================#
@views.route('/auth')
def auth():
    return render_template('auth.html', page='Auth', user=current_user, log=log)

@views.route('/Register', methods=['POST'])
def Register():
    global log
    if request.form:
        #DEBUG
        print(request.form)
        #GET DATA
        log=False
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')
        level = 2
        active = 0
        email_validation = Users.query.filter_by(email=email).first()
        if len(username) < 3:
            flash('Username depan harus lebih dari 3 huruf.', category='error')
        elif email_validation:
            flash('Email sudah digunakan. Silahkan gunakan email lain', category='error')
        elif len(email) < 4:
            flash('Email harus lebih dari 4 huruf.', category='error')
        elif password != password_repeat:
            flash('Password tidak sama.', category='error')
        elif len(password) < 8:
            flash('Password harus lebih dari 8', category='error')
        else:
            new_user = Users(username=username, email=email, password=generate_password_hash(password, method='sha256'), level=level, active=active)
            db.session.add(new_user)
            user_profiles = Profiles(firstname=username, parent=new_user)
            db.session.add(user_profiles)
            db.session.commit()
            flash('Akun anda telah didaftarkan', category='success')
    return redirect(url_for('views.auth'))

@views.route('/Login', methods=['POST'])
def Login():
    global log
    if request.form:
        log=True
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')
        users = Users.query.filter_by(username=username).first()
        if request.form.get('remember-me') == 'on':
            remember=True
        else:
            remember=False
        if len(username) < 3:
            flash('Email harus lebih dari 4 huruf.', category='error')
        elif len(password) < 8:
            flash('Password harus lebih dari 8', category='error')
        else:
            if users:
                if check_password_hash(users.password, password):
                    login_user(users, remember=remember)
                    return redirect(url_for('views.home'))
                else:
                    flash('Password salah', category='error')
            else:
                flash('Email tidak ditemukan', category='error')
        return redirect(url_for('views.auth'))

@views.route('/Logout')
@login_required
def Logout():
    user = Users.query.filter_by(id=current_user.id).first()
    user.active = 0
    db.session.commit()
    logout_user()
    return redirect(url_for('views.auth'))

#==============================================BAGIAN PROFIL============================================================#
#RUTE PROFIL
@views.route('/profil')
@login_required
def profile():
    profile = Profiles.query.filter_by(id=current_user.id).first()
    return render_template('profil.html', page="Profil", user=current_user, flag=flag, profile=profile)

#UPDATE NAME
@views.route('/UpdateProfile', methods=['POST'])
@login_required
def UpdateProfile():
    global flag
    if request.form:
        flag = True

        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        profile = Profiles.query.filter_by(id=current_user.id).first()
        user = Users.query.filter_by(id=current_user.id).first()

        flag1 = flag2 = False
        if len(firstname) < 2:
            flash('Nama depan harus lebih dari 2', category='error')
        elif firstname == profile.firstname and lastname == profile.lastname:
            pass
        else:
            profile.firstname = firstname
            profile.lastname = lastname
            flag1 = True

        if not password:
            pass
        elif len(password) < 8:
            flash('Password harus lebih dari 8 karakter', category='error')
        elif password != password_repeat:
            flash('Ulangi password', category='error')
        elif check_password_hash(user.password, password):
            flash('Password sama dengan sebelumnya', category='error')
        else:
            user.password = generate_password_hash(password, method='sha256')
            flag2 = True

        if flag1 or flag2:
            flash('Profil berhasil diubah', category='success')
            db.session.commit()
    return redirect(url_for('views.profile', flag=flag))

#UPDATE KONTAK
@views.route('/UpdateKontak', methods=['POST'])
@login_required
def UpdateKontak():
    global flag
    if request.form:
        flag=False
        address = request.form.get('address')
        phone = request.form.get('phone')
        profile = Profiles.query.filter_by(id=current_user.id).first()
        flag1 = flag2 = False
        if not address or address == profile.address :
            pass
        else:
            profile.address = address
            flag1 = True
        if not phone or phone == profile.phone:
            pass
        elif len(phone) < 10:
            flash('Nomor harus 10 angka', category='error')
        else:
            profile.phone = phone
            flag2 = True

        if flag1 or flag2:
            db.session.commit()
            flash('Kontak berhasil diubah', category='success')
    return redirect(url_for('views.profile', flag=flag))

#==========================================END OF BAGIAN PROFILE=================================================================#

#==========================================BAGIAN USER========================================================================#
#RUTE USER MANAGEMENT
@views.route('/user')
@login_required
def ManageUser():
    users = Users.query.all()
    return render_template('user.html', page="User Management", user=current_user, users=users)

@views.route('/CreateUser', methods=['POST'])
@login_required
def CreateUser():
    if request.form:
        print(request.form)
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')
        level = request.form.get('level')
        username_validation = Users.query.filter_by(username=username).first()
        email_validation = Users.query.filter_by(email=email).first()
        if len(username) < 3:
            flash('Username depan harus lebih dari 3 huruf.', category='error')
        elif email_validation:
            flash('Email sudah digunakan. Silahkan gunakan email lain', category='error')
        elif username_validation:
            flash('Username sudah digunakan. Silahkan gunakan username lain', category='error')
        elif len(email) < 4:
            flash('Email harus lebih dari 4 huruf.', category='error')
        elif password != password_repeat:
            flash('Password tidak sama.', category='error')
        elif len(password) < 8:
            flash('Password harus lebih dari 8', category='error')
        else:
            new_user = Users(username=username, email=email, password=generate_password_hash(password, method='sha256'), level=level)
            db.session.add(new_user)
            user_profiles = Profiles(firstname=username, parent=new_user)
            db.session.add(user_profiles)
            db.session.commit()
            flash('Akun anda telah didaftarkan', category='success')
    return redirect(url_for('views.ManageUser'))

@views.route('/UpdateUser', methods=['POST'])
@login_required
def UpdateUser():
    if request.form:
        print(request.form)
        id = request.form.get('id')
        level = request.form.get('level')
        user = Users.query.filter_by(id=id).first()
        user.level = level
        db.session.commit()
        flash('Data user berhasil diubah', category='success')
    return redirect(url_for('views.ManageUser'))

@views.route('/DeleteUser', methods=['POST'])
@login_required
def DeleteUser():
    if request.form:
        print(request.form)
        id = request.form.get('id')
        user = Users.query.filter_by(id=id).first()
        if user.active == 1:
            flash('User sedang online tidak dapat dihapus', category='error')
        else:
            profile = Profiles.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.delete(profile)
            db.session.commit()
    return redirect(url_for('views.ManageUser'))

#==========================================END OF BAGIAN USER=================================================================#

#===========================================BAGIAN EVENT=======================================================================#
#TAMBAH EVENT
@views.route('/CreateEvent', methods=['POST'])
@login_required
def CreateEvent():
    if current_user.level == 1:
        print(request.form)
        if request.form:
            title = request.form.get('event')
            datestart = request.form.get('dibuka')
            dateclose = request.form.get('ditutup')
            detail = request.form.get('detail')
            event = Event.query.filter_by(title=title).first()
            if event:
                flash('Event sudah terdaftar', category='error')
            else:
                new_event = Event(title=title, datestart=datestart, dateclose=dateclose, detail=detail)
                db.session.add(new_event)
                db.session.commit()
                flash('Event telah didaftar', category='success')
    return redirect(url_for('views.home'))

#UPDATE EVENT
@views.route('/UpdateEvent', methods=['POST'])
@login_required
def UpdateEvent():
    if request.form:
        print(request.form)
        id = request.form.get('id')
        data = Event.query.filter_by(id=id).first()
        data.title = request.form.get('event')
        data.datestart = request.form.get('dibuka')
        data.dateclose = request.form.get('ditutup')
        data.detail = request.form.get('detail')
        db.session.commit()
        flash('Event telah diubah', category='success')
    return redirect(url_for('views.home'))
    
#DELETE EVENT
@views.route('/DeleteEvent', methods=['POST'])
@login_required
def DeleteEvent():
    if request.form:
        print(request.form)
        id = request.form.get('id')
        data = Event.query.filter_by(id=id).first()
        db.session.delete(data)
        db.session.commit()
        flash('Event berhasil dihapus', category='success')

    return redirect(url_for('views.home'))

#GABUNG EVENT RELASI MANY TO MANY
@views.route('/GabungEvent', methods=['POST'])
@login_required
def GabungEvent():
    if request.form:
        print(request.form)
        user_id = request.form.get('user_id')
        event_id = request.form.get('event_id')
        event = Event.query.filter_by(id=event_id).first()
        user = Users.query.filter_by(id=user_id).first()
        event.users.append(user)
        db.session.commit()
        flash('Anda berhasil mengikuti event', category='success')
    return redirect(url_for('views.home'))