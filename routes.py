from app import app
from flask import render_template, request, session, redirect, url_for
import users

@app.route('/')
def index():
    return render_template('login.html', login_tried=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', error=None)
    
    if request.method == 'POST':
        username = request.form['username']
        password_1 = request.form['password_1']
        password_2 = request.form['password_2']

        if len(username) < 1 or len(username) > 20:
            return render_template('register.html', error='username_length')
        if len(password_1) < 8 or len(password_1) > 100:
            return render_template('register.html', error='password_length')
        if password_1 != password_2:
            return render_template('register.html', error='password_match')
        if not users.register(username, password_1):
            return render_template('register.html', error='not_successful')
        
        return redirect(url_for('user', username=username))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if not users.login(username, password):
        return render_template('/login.html', login_tried=True)
    
    return redirect(url_for('user', username=username))

@app.route('/user/<username>')
def user(username):
    if session['username'] == username:
        return render_template('user.html', user=username)
    
    return render_template('error.html')

@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')