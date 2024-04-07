from flask import session
from sqlalchemy.sql import text
from db import db

def get_threads(topic):
    sql = '''SELECT U.id, U.username, A.title, M.message, M.date,
                (SELECT COUNT(*) FROM subthreads WHERE parent_msg_id=M.id)
             FROM threads A JOIN topics B ON A.topic_id=B.id
                            JOIN messages M on A.message_id=M.id
                            JOIN users U ON M.user_id=U.id
             WHERE B.topic=:topic'''
    result = db.session.execute(text(sql), {'topic':topic})
    threads = result.fetchall()
    return threads

def add_thread(topic_id, message_id, title):
    sql = '''INSERT INTO threads (topic_id, message_id, title)
             VALUES (:topic_id, :message_id, :title)'''
    db.session.execute(text(sql), {'topic_id':topic_id, 'message_id':message_id, 'title':title})
    db.session.commit()
