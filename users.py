from flask import session, abort, request
from sqlalchemy.sql import text
from db import db
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

def login(username, password):
    sql = 'SELECT id, password, is_admin FROM users WHERE username=:username'
    result = db.session.execute(text(sql), {'username':username})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user[1], password):
        return False
    session['user_id'] = user[0]
    session['username'] = username
    session["csrf_token"] = secrets.token_hex(16)
    return True

def register(username, password_1):
    hash_value = generate_password_hash(password_1)
    try:
        sql = '''INSERT INTO users (username, password, created_at, is_admin)
                 VALUES (:username, :password, NOW(), False)'''
        db.session.execute(text(sql), {'username':username, 'password':hash_value})
        db.session.commit()
    except:
        return False
    return login(username, password_1)

def change_username(username):
    try:
        sql = 'UPDATE users SET username=:username WHERE id=:user_id'
        db.session.execute(text(sql), {'username':username, 'user_id':session['user_id']})
        db.session.commit()
    except:
        return False
    session['username'] = username
    return True

def logout():
    del session['user_id']
    del session['username']
    del session['csrf_token']

def get_user_data():
    sql = 'SELECT username, created_at FROM users WHERE id=:user_id'
    result = db.session.execute(text(sql), {'user_id':session['user_id']})
    user_data = result.fetchone()
    return user_data

def delete_account():
    sql = 'DELETE FROM users WHERE id=:user_id'
    db.session.execute(text(sql), {'user_id':session['user_id']})
    db.session.commit()
    logout()

def get_role():
    sql = 'SELECT is_admin FROM users WHERE id=:user_id'
    result = db.session.execute(text(sql), {'user_id':session['user_id']})
    is_admin = result.fetchone()[0]
    return is_admin

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

