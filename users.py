from flask import session
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
        sql = '''INSERT INTO users (username, password, is_admin)
                 VALUES (:username, :password, False)'''
        db.session.execute(text(sql), {'username':username, 'password':hash_value})
        db.session.commit()
    except:
        return False
    return login(username, password_1)

def logout():
    del session['user_id']
    del session['username']
