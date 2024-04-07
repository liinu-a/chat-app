from app import app
from flask import render_template, request, session, redirect
import users, topics, messages, threads

@app.route('/')
def index():
    tpcs = topics.get_topics()[0:5]
    return render_template('index.html', topics=tpcs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not users.login(username, password):
            error = 'Wrong username or password.'
            return render_template('error.html', error=error)
        return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password_1 = request.form['password_1']
        password_2 = request.form['password_2']

        error = None
        if len(username) < 1 or 20 < len(username):
            error = 'Username must be 1-20 characters.'
        elif len(password_1) < 6:
            error = 'Password must be at least 6 characters.'
        elif password_1 != password_2:
            error = 'Passwords do not match.'
        elif not users.register(username, password_1):
            error = 'Registration unsuccessful, username may be unavailable.'

        if error:
            return render_template('error.html', error=error)
        return redirect('/')
    
@app.route('/user_settings')
def user_settings():
    user_data = users.get_user_data()
    return render_template('user_settings.html', user_data=user_data)

@app.route('/change_username', methods=['GET', 'POST'])
def change_username():
    if request.method == 'GET':
        return render_template('change_username.html')
    
    if request.method == 'POST':
        users.check_csrf()
        username = request.form['username']

        error = None
        if len(username) < 1 or 20 < len(username):
            error = 'Username must be 1-20 characters.'
        elif not users.change_username(username):
            error = 'Error, username may be unavailable.'

    if error:
        return render_template('error.html', error=error)
    return redirect('/')

@app.route('/confirmation/<action>')
def confirmation(action):
    match action:
        case 'delete_account':
            message = 'Are you sure you want to delete your account? The deletion will be permanent.'
    
    return render_template('confirmation.html', message=message, action=action)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    users.check_csrf()
    users.delete_account()
    return redirect('/')

@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')

@app.route('/all_topics')
def all_topics():
    tpcs = topics.get_topics()
    try:
        is_admin = users.get_role()
    except:
        is_admin = False
    return render_template('all_topics.html', topics=tpcs, is_admin=is_admin)
    
@app.route('/<action>_topic', methods=['GET', 'POST'])
def update_topics(action):
    if request.method == 'GET':
        tpcs = topics.get_topics()
        return render_template('update_topics.html', action=action, topics=tpcs)
    
    if request.method == 'POST':
        users.check_csrf()

        if action == 'add':
            topic = request.form['topic'].capitalize()

            if not topics.add_topic(topic):
                error = 'Topic already exists.'
                return render_template('error.html', error=error)
        
        elif action == 'remove':
            remove = request.form['topic']
            topics.remove_topic(remove)

        return redirect('/all_topics')

@app.route('/start_thread', methods=['GET', 'POST'])
def start_thread():
    if request.method == 'GET':
        tpcs = topics.get_topics()
        return render_template('start_thread.html', topics=tpcs)
    
    if request.method == 'POST':
        users.check_csrf()
        title = request.form['title']
        message = request.form['message']

        error = None
        if 1 > len(title) or 20 < len(title):
            error = 'Title must be 1-20 characters.'
        elif len(message) > 10000:
            error = 'Message exceeds the length limit.'
        elif 'topic' not in request.form:
            error = "You haven't chosen a topic."

        if error:
            return render_template('error.html', error=error)
        
        topic_id = request.form['topic']
        message_id = messages.add_message(message)
        threads.add_thread(topic_id, message_id, title)

        return redirect('/')
        
@app.route('/topic/<topic>')
def topic_threads(topic):
    thrds = threads.get_threads(topic)
    return render_template('threads.html', topic=topic, threads=thrds)