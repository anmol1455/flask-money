from flask import Flask, render_template, request, Blueprint, flash, g, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import db
import jwt
import config
import hashlib
import datetime;
  
# ct stores current time
ct = datetime.datetime.now()
print("current time:-", ct)
app = Flask(__name__)

cursor, conn = db.connection(app)


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('home'))
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        cursor.execute('SELECT * FROM auth WHERE email=%s', (email))
        user = cursor.fetchone()
        app.logger.debug(user)
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[3], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        flash(error)
        return render_template('login.html', title='Login')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        if 'user_id' in session:
            app.logger.debug(session['user_id'])
            return redirect(url_for('home'))
        return render_template('register.html', title='Register')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        error = None
        if password != confirm:
            error = 'password and confirm password does not match'
        else:
            cursor.execute('SELECT * FROM auth WHERE email=%s', (email))
            user = cursor.fetchone()
            app.logger.debug(user)
            if user:
                error = 'Sorry, email already exist!'

        if error is None:
            password = generate_password_hash(password)
            cursor.execute('INSERT into auth (name, email, password) VALUES (%s,%s,%s)', (name, email, password))
            user = cursor.fetchone()
            conn.commit()
            if cursor.lastrowid:
                flash('Registration successfull!, login now!')
                return redirect(url_for('login'))
            else:
                flash('Something went wrong, try again!')
                return render_template('register.html', title='Register')
        flash(error)
        return render_template('register.html', title='Register')

@app.route('/')
def index():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE id=%s', (session['user_id']))
    user = cursor.fetchone()
    name = user[2]
    cursor.execute('SELECT * FROM request where reciever_email=%s',(name))
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM money where sender_email=%s',(name))
    data1 = cursor.fetchall()
    return render_template('home.html', title=name, name=name, data = data, data1=data1)

@app.route('/sendMoney', methods=('GET', 'POST'))
def send():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE id=%s', (session['user_id']))
    user = cursor.fetchone()
    name = user[2]
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('send.html', title='Send Money')
    if request.method == 'POST':
        to_mail = request.form['rec_mail']
        money = request.form['money']
        currency = request.form['currency']
        error = None
        params = [to_mail]
    # cursor return affected rows
        count = cursor.execute('select * from auth where email=%s', params)  # prevent SqlInject
        if (count != 0 and to_mail!=name):
            cursor.execute('INSERT into money (sender_email, reciever_email, money, time) VALUES (%s,%s,%s,%s)', (name, to_mail, money+currency, ct))
            user = cursor.fetchone()
            conn.commit()
            flash("successfull")
        else:
            flash("user does not exist or You can't send or request money from yourself")
        return redirect('/sendMoney')

@app.route('/moneyInfo')
def sendInfo():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
    cursor.execute('SELECT * FROM auth WHERE id=%s', (session['user_id']))
    user = cursor.fetchone()
    name = user[2]
    cursor.execute('SELECT * FROM money where sender_email=%s',(name))
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM money where reciever_email=%s',(name))
    data1= cursor.fetchall()
    return render_template('sendtable.html', title=name, data=data, data1=data1)

@app.route('/sendRequest', methods=('GET', 'POST'))
def request1():
    if request.method == 'GET':
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('request.html', title='request Money')
    if request.method == 'POST':
        to_mail = request.form['req_mail']
        money = request.form['money']
        currency = request.form['currency']
        error = None
        cursor.execute('SELECT * FROM auth WHERE id=%s', (session['user_id']))
        user = cursor.fetchone()
        name = user[2]
        params = [to_mail]
    # cursor return affected rows
        count = cursor.execute('select * from auth where email=%s', params)  # prevent SqlInject
        if (count != 0 and to_mail!=name):
            cursor.execute('INSERT into request (sender_email, reciever_email, money, time) VALUES (%s,%s,%s,%s)', (name, to_mail, money+currency, ct))
            user = cursor.fetchone()
            conn.commit()
            flash("successfull")
        else:
            flash("user does not exist or You can't send or request money from yourself")
        return redirect('/sendRequest')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have successfully logged out.')
    return redirect('/login')


if __name__ == '__main__':
    app.debug = config.debug
    app.config['SECRET_KEY'] = config.secret
    app.run(port=config.port)
