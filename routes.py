from app import app
from flask import render_template, request, session, redirect, abort, flash
import users, topics, messages, threads

@app.route('/')
def index():
    tpcs = topics.get_topics()
    is_admin = users.check_role()
    
    shown_tpcs = tpcs[0:4]
    listed_tpcs = None
    if len(tpcs) > 4:
        listed_tpcs = tpcs[4: ]

    return render_template('index.html', shown_tpcs=shown_tpcs, listed_tpcs=listed_tpcs, is_admin=is_admin)

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        flash("You are alreagy logged in.", 'info')
        return redirect('/')

    if request.method == 'GET':
        return render_template('login.html', username='')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == '' or password == '':
            flash("Please make sure you've filled in both your username and password.", 'error')
            return render_template('/login.html', username=username)

        if not users.login(username, password):
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('login.html', username=username)
        
        return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        flash(f"You've alreagy signed up and are logged in as user {session['username']}.", 'info')
        return redirect('/')

    if request.method == 'GET':
        return render_template('register.html', username='')
    
    if request.method == 'POST':
        username = request.form['username']
        is_admin = username == 'testAdmin'
        password_1 = request.form['password_1']
        password_2 = request.form['password_2']

        errors = False
        if username == '' or 25 < len(username):
            flash('Username must be 1-25 characters.', 'error')
            errors = True
        if len(password_1) < 6:
            flash('Password must be at least 6 characters.', 'error')
            errors = True
        if password_1 != password_2:
            flash('The passwords do not match. Please try again.', 'error')
            errors = True
        if errors:
            return render_template('register.html', username=username)
        
        if not users.register(username, password_1, is_admin):
            flash('Registration unsuccessful, username may be unavailable. Please try again.', 'error')
            return render_template('register.html', username=username)

        return redirect('/')
    
@app.route('/user_settings')
def user_settings():
    if not session.get('user_id'):
        flash('You have to be logged in to view your account.', 'error')
        return redirect('/login')

    user_data = users.get_user_data()
    return render_template('user_settings.html', user_data=user_data)

@app.route('/change_username', methods=['GET', 'POST'])
def change_username():
    if not session.get('user_id'):
        flash("Log in to change your account's username.", 'error')
        return redirect('/login')

    if request.method == 'GET':
        return render_template('change_username.html', new_username='')
    
    if request.method == 'POST':
        users.check_csrf()
        username = request.form['username']

        if username == '' or 25 < len(username):
            flash('Username must be 1-25 characters.', 'error')
            return render_template('change_username.html', new_username=username)
        if username == session['username']:
            flash(f'{username} is already set as your username.', 'error')
            return render_template('change_username.html', new_username=username)
        if not users.change_username(username):
            flash('Username change unsuccessfull. Username may be unavailable, please try again.', 'error')
            return render_template('change_username.html', new_username=username)
        
    flash(f'Username changed successfully. Your new username is {session["username"]}.', 'info')
    return redirect('/user_settings')

@app.route('/delete/<target>', methods=['GET', 'POST'])
@app.route('/delete/<target>/<message_id>/<return_to>', methods=['GET', 'POST'])
def delete(target, message_id=None, return_to=None):
    if not session.get('user_id'):
        flash("The page you are trying to access requires you to be logged in.", 'error')
        return redirect('/login')
    
    if request.method == 'GET':
        match target:
            case 'thread':
                if messages.check_writer(message_id) or users.check_role():
                    session['delete_message_id'] = message_id
                    session['return_to'] = return_to
                else:
                    abort(403)
            case 'reply':
                if (messages.check_writer(message_id) or users.check_role() or
                    threads.check_reply_thread_owner(message_id)):
                        session['delete_message_id'] = message_id
                        session['return_to'] = return_to
                else:
                    abort(403)

        confirm = 'Are you sure? The deletion will be permanent!'
        return render_template('confirmation.html', confirm=confirm, target=target)
    
    if request.method == 'POST':
        users.check_csrf()

        if target == 'account':
            users.delete_account()
            flash('Your account has been deleted.', 'info')
            return redirect('/')
        
        messages.delete_message(session['delete_message_id'])
        if target == 'thread':
            flash('The thread has been deleted.', 'info')
            return redirect(session['threads_url'])
        else:
            flash('Reply deleted.', 'info')
            return redirect(session['thread_url'])
        
@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')

@app.route('/<action>_topic', methods=['GET', 'POST'])
def update_topics(action):
    if not users.check_role():
        abort(403)

    if request.method == 'GET':
        if action == 'remove':
            tpcs = [list(t) for t in topics.get_topics()]
            if tpcs == []:
                flash('No existing topics to remove.', 'error')
                return redirect('/')
            session['topics'] = [list(t) for t in topics.get_topics()]

        return render_template('update_topics.html', action=action, value='')
    
    if request.method == 'POST':
        users.check_csrf()

        if action == 'add':
            topic = request.form['topic'].lower()
            if len(topic) < 1:
                flash("Please write the topic you'd like to add.", 'error')
                return render_template('update_topics.html', action=action, value='')
            if len(topic) > 20:
                flash("The length of the topic should not exceed 20 characters.", 'error')
                return render_template('update_topics.html', action=action, value='')
            if not topics.add_topic(topic):
                flash('The topic you tried to add already exists. Please try again.', 'error')
                return render_template('update_topics.html', action=action, value=topic)
        
        elif action == 'remove':
            removables = request.form.getlist('topic')
            if len(removables) == 0:
                flash("You haven't chosen any topics to remove.", 'error')
                return render_template('update_topics.html', action=action)

            for remove in removables:
                topics.remove_topic(remove)

        flash('Topics updated successfully.', 'info')
        return redirect('/')
    
@app.route('/start_thread/', methods=['GET', 'POST'])
@app.route('/start_thread/<back>', methods=['GET', 'POST'])
def start_thread(back=None):
    if not session.get('user_id'):
        flash("Please log in to start a thread.", 'error')
        return redirect('/login')

    if request.method == 'GET':
        choose_topic = topics.get_topics()
        if not choose_topic:
            flash('Unfortunately, there are no topics to start a thread under.', 'error')
            return redirect('/')
        session['tpcs'] = [list(t) for t in choose_topic]

        if back:
            session['threads_url'] = f"/{back.replace(';', '/')}"
        else:
            session['threads_url'] = '/'
        
        return render_template('add.html', add='thread', title='', text='', back=back)
    
    if request.method == 'POST':
        users.check_csrf()
        title = request.form['title']
        message = request.form['message']
        topic_id = request.form['topic']

        errors = False
        if title == '' or 50 < len(title):
            flash('Make sure the the length of the title is 1-50 characters.', 'error')
            errors = True
        if len(message) > 10000:
            flash('Message exceeds the length limit of 10000 characters.', 'error')
            errors = True
        if topic_id == '':
            flash("Please choose a topic.", 'error')
            errors = True
        if errors:
            return render_template('add.html', add='thread', title=title, text=message, back=back)
        
        message_id = messages.add_message(message)
        thread_id = threads.add_thread(topic_id, message_id, title)

        return redirect(f'/thread/{thread_id}/most_recent/25')

@app.route('/reply/<thread_id>/<reply_to>/<message_id>', methods=['GET', 'POST'])
def reply(thread_id, reply_to, message_id):
    if not session.get('user_id'):
        flash('You must be logged in to write replies.', 'error')
        return redirect('/login')

    if request.method == 'GET':
        message = None
        match reply_to:
            case 'thread':
                message = messages.get_init_message(message_id)
            case 'comment':
                message = messages.get_message(message_id)

        if not message:
            flash("The thread or comment you're trying to reply to does not exist.", 'error')
            return redirect('/')

        session['reply_to_msg'] = [data for data in message]
        return render_template('add.html', add='reply', reply_to=reply_to, thread_id=thread_id, 
                               message_id=message_id, text='')
    
    if request.method == 'POST':
        users.check_csrf()
        message = request.form['message']

        if len(message) > 10000:
            flash('Message exceeds the length limit of 10000 characters.', 'error')
        elif message == '':
            flash("The message field is empty.", 'error')
        else:
            reply_msg_id = messages.add_message(message)
            messages.add_reply(thread_id, reply_msg_id, message_id)

            return redirect(f'/thread/{thread_id}/most_recent/25')
            
        return render_template('add.html', add='reply', reply_to=reply_to, thread_id=thread_id, 
                               message_id=message_id, text=message)

@app.route('/threads/<category>/<order_by>/<limit>')
@app.route('/threads/<category>/<order_by>/<limit>/<scroll_to>')
def thread_list(category, order_by, limit, scroll_to=None):
    limit = int(limit)
    is_admin = users.check_role()

    logged_in = session.get('user_id')
    match category:
        case 'all':
            thrds = threads.get_all_threads(order_by, limit)
        case 'pinned':
            if not logged_in:
                flash('Please log in to view pinned threads.', 'error')
                return redirect('/login')
            thrds = threads.pinned(order_by, limit)
        case 'user':
            if not logged_in:
                flash('Please log in to view your own threads.', 'error')
                return redirect('/login')
            thrds = threads.get_user_threads(order_by, limit)
        case 'commented':
            if not logged_in:
                flash("Please log in to view threads you've commented on.", 'error')
                return redirect('/login')
            thrds = threads.get_commented_threads(order_by, limit)
        case 'search':
            thrds = threads.search(request.args['query'], order_by, limit)
        case _:
            thrds = threads.get_topic_threads(category, order_by, limit)

    if not thrds or thrds[0][7] <= limit:
        thrds_left = False
    else:
        thrds_left = True

    return render_template('threads.html', category=category, threads=thrds, order_by=order_by, limit=limit, 
                           scroll_to=scroll_to, thrds_left=thrds_left, is_admin=is_admin)

@app.route('/thread/<thread_id>/<order_by>/<limit>')
@app.route('/thread/<thread_id>/<order_by>/<limit>/<scroll_to>')
def thread(thread_id, order_by, limit, scroll_to=None):
    limit = int(limit)
    thread = threads.get_thread(thread_id)
    replies = messages.get_replies(thread_id, order_by, limit)
    is_admin = users.check_role()

    if thread[6] <= limit:
        replies_left = False
    else:
        replies_left = True

    return render_template('thread.html', thread_id=thread_id, thread=thread, replies=replies, 
                           order_by=order_by, limit=limit, replies_left=replies_left, is_admin=is_admin, 
                           scroll_to=scroll_to)

@app.route('/pin/<thread_id>', methods=['POST'])
def pin(thread_id):
    pinned = threads.is_pinned(thread_id)
    if pinned:
        threads.unpin(thread_id)
    else:
        threads.pin(thread_id)

    return {'result': 'success'}

@app.route('/threads_url/<category>/<back>', methods=['POST'])
def threads_url(category, back):
    url = f"/{back.replace(';', '/')}"
    if category == 'search':
        url += f'?query={request.args["query"]}'
    session['threads_url'] = url

    return {'result': 'success'}

@app.route('/thread_url/<back>', methods=['POST'])
def thread_url(back):
    url = f"/{back.replace(';', '/')}"
    session['thread_url'] = url

    return {'result': 'success'}
