from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, RegisterStartupForm, EditStartupForm, InvestForm
from flask_login import current_user, login_user
from app.models import User, Startup
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from datetime import datetime
import base64
import os
import stripe
import decimal

blacklisted = ["Funnel", "Test Startup", "Random Startup"]

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

class Startup_HTML_REP:
    def __init__(self, logo, capital_raised, name, description):
        self.logo = logo
        self.capital_raised = capital_raised
        self.name = name
        self.description = description

@app.route('/')
@app.route('/index')
@login_required
def index():
    startups = Startup.query.all()
    STARTUPS = []
    for s in startups:
        #if (s.name in blacklisted):
         #   db.session.delete(s)
          #  db.session.commit()
           # continue
        #if (s.name == 'INSOLAR'):
         #   s.capital_raised=0
          #  db.session.commit()
        STARTUPS.append(Startup_HTML_REP(base64.b64encode(s.logo).decode('ascii'), s.capital_raised, s.name, s.description))
    return render_template('index.html', STARTUPS=STARTUPS, len=len(STARTUPS), data=list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        #flash('Login requested for user {}, remember_me={}'.format(
           # form.username.data, form.remember_me.data))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    STARTUPS = []
    startups = user.startups
    for s in startups:
        if (s.name in blacklisted):
            continue
        STARTUPS.append(Startup_HTML_REP(base64.b64encode(s.logo).decode('ascii'), s.capital_raised, s.name, s.description))
    return render_template('user.html', user=user, STARTUPS=STARTUPS, len=len(STARTUPS), data=list)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           form=form)
@app.route('/edit_startup/<startup_name>', methods=['GET', 'POST'])
@login_required
def edit_startup(startup_name):
    startup = Startup.query.filter_by(name=startup_name).first_or_404()
    form = EditStartupForm(startup.name)
    if form.validate_on_submit():
        startup.name = form.name.data
        startup.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_startup', startup_name=startup.name))
    elif request.method == 'GET':
        form.name.data = startup.name
        form.description.data = startup.description
    return render_template('edit_startup.html',
                           form=form)

@app.route('/register_startup', methods=['GET', 'POST'])
@login_required
def register_startup():
    form = RegisterStartupForm()
    if form.validate_on_submit():
        s = Startup(name=form.name.data, founder=current_user, capital_raised=0, description=form.description.data)
        f = form.logo.data
        #filename = secure_filename(f.filename)
        #app.config['UPLOAD_FOLDER'] = '/var/uploads'
        #f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        s.logo = f.read()
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_startup.html', form=form)

@app.route('/image')
def image():
    file_data = Startup.query.filter_by(name="INSOLAR").first()
    image = base64.b64encode(file_data.logo).decode('ascii')
    return render_template('image.html', data=list, image=image)

@login_required
@app.route('/invest', methods=['GET', 'POST'])
def invest():
    form = InvestForm()
    if form.validate_on_submit():
        return redirect(url_for('investnext', amount = int(form.amount.data * 100), startup=form.name.data))
    return render_template('invest.html', form=form)

@login_required
@app.route('/investnext/<amount>/<startup>')
def investnext(amount, startup):
    return render_template('investnext.html', key=stripe_keys['publishable_key'], amount=amount, startup=startup)

@app.route('/charge/<amount>/<startup>', methods=['POST'])
def charge(amount, startup):
    customer = stripe.Customer.create(email='sample@customer.com', source=request.form['stripeToken'])
    stripe.Charge.create(customer=customer.id, amount=amount, currency='usd', description='Flask Charge')
    s = Startup.query.filter_by(name=startup).first()
    s.capital_raised += float(amount) / 100
    db.session.commit()

    return render_template('charge.html', amount= (float(amount) / 100))
