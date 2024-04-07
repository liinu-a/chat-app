from flask import session
from sqlalchemy.sql import text
from db import db

def get_topics():
    sql = 'SELECT * FROM topics'
    result = db.session.execute(text(sql)).fetchall()
    return result

def add_topic(topic):
    try:
        sql = 'INSERT INTO topics (topic) VALUES (:topic)'
        db.session.execute(text(sql), {'topic':topic})
        db.session.commit()
    except:
        return False
    return True

def remove_topic(topic):
    sql = 'DELETE FROM topics WHERE topic=:topic'
    db.session.execute(text(sql), {'topic':topic})
    db.session.commit()
    