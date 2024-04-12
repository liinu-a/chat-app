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
            errors = ['Wrong username or password.']
            return render_template('error.html', errors=errors)
        return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password_1 = request.form['password_1']
        password_2 = request.form['password_2']

        errors = []
        if len(username) < 1 or 20 < len(username):
            errors.append('Username must be 1-20 characters.')
        if len(password_1) < 6:
            errors.append('Password must be at least 6 characters.')
        if password_1 != password_2:
            errors.append('Passwords do not match.')
        if len(errors) != 0:
            return render_template('error.html', errors=errors)
        
        if not users.register(username, password_1):
            errors.append('Registration unsuccessful, username may be unavailable.')
            return render_template('error.html', errors=errors)

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

        errors = []
        if len(username) < 1 or 20 < len(username):
            errors.append('Username must be 1-20 characters.')
        elif not users.change_username(username):
            errors.append('Error, username may be unavailable.')
        if len(errors) != 0:
            return render_template('error.html', errors=errors)
        
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
                errors = ['Topic already exists.']
                return render_template('error.html', errors=errors)
        
        elif action == 'remove':
            remove = request.form['topic']
            topics.remove_topic(remove)

        return redirect('/all_topics')

@app.route('/start_thread', methods=['GET', 'POST'])
def start_thread():
    try:
        session['user_id']
    except:
        errors = ['You have not logged in.']
        return render_template('error.html', errors=errors)
    
    if request.method == 'GET':
        tpcs = topics.get_topics()
        return render_template('add.html', topics=tpcs, add='thread')
    
    if request.method == 'POST':
        users.check_csrf()
        title = request.form['title']
        message = request.form['message']

        errors = []
        if 1 > len(title) or 20 < len(title):
            errors.append('Title must be 1-20 characters.')
        if len(message) > 10000:
            errors.append('Message exceeds the length limit.')
        if 'topic' not in request.form:
            errors.append("You haven't chosen a topic.")
        if len(errors) != 0:
            return render_template('error.html', errors=errors)
        
        topic_id = request.form['topic']
        message_id = messages.add_message(message)
        threads.add_thread(topic_id, message_id, title)

        return redirect('/')

@app.route('/topic/<topic>/<order_by>/<limit>/<scroll_to>')
def topic_threads(topic, order_by, limit, scroll_to):
    limit = int(limit)
    thrds = threads.get_threads(topic, order_by, limit)
    try:
        is_admin = users.get_role()
    except:
        is_admin = False

    if not thrds or thrds[0][7] <= limit:
        thrds_left = False
    else:
        thrds_left = True

    return render_template('threads.html', topic=topic, threads=thrds, order_by=order_by, limit=limit, 
                           scroll_to=scroll_to, thrds_left=thrds_left, is_admin=is_admin)


@app.route('/topic/<topic>/<thread_id>/<order_by>/<limit>/<scroll_to>')
def thread(topic, thread_id, order_by, limit, scroll_to):
    limit = int(limit)
    thread = threads.get_thread(thread_id)
    replies = messages.get_replies(thread_id)
    try:
        is_admin = users.get_role()
    except:
        is_admin = False

    if thread[5] <= limit:
        replies_left = False
    else:
        replies_left = True

    return render_template('thread.html', topic=topic, thread_id=thread_id, thread=thread, replies=replies, 
                           order_by=order_by, limit=limit, scroll_to=scroll_to, replies_left=replies_left, 
                           is_admin=is_admin)
