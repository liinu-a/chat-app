from flask import session
from sqlalchemy.sql import text
from db import db

def add_message(message):
    sql = '''INSERT INTO messages (user_id, message, date)
                 VALUES (:user_id, :message, NOW()) RETURNING id'''
    result = db.session.execute(text(sql), {'user_id':session['user_id'], 'message':message})
    id = result.fetchone()[0]
    db.session.commit()
    return id