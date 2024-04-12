from flask import session
from sqlalchemy.sql import text
from db import db

def get_threads(topic, order_by, limit):
    sql = '''SELECT threads.*
             FROM
               (SELECT U.id, U.username, A.title, A.id, M.message, M.date date,
                 (SELECT COUNT(*) FROM replies WHERE A.id=thread_id) replies,
                 COUNT(*) OVER()
               FROM threads A JOIN topics B ON A.topic_id=B.id
                              JOIN messages M on A.message_id=M.id
                              JOIN users U ON M.user_id=U.id
               WHERE B.topic=:topic) threads
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN threads.date END DESC,
               CASE WHEN :order_by = 'oldest' THEN threads.date END,
               CASE WHEN :order_by = 'most_replies' THEN threads.replies END DESC,
               threads.date DESC
             LIMIT :limit'''
    result = db.session.execute(text(sql), {'topic':topic, 'order_by':order_by, 'limit':limit})
    threads = result.fetchall()
    return threads

def get_thread(thread_id):
    sql = '''SELECT U.id, U.username, T.title, M.message, M.date,
               (SELECT COUNT(*) FROM replies WHERE thread_id=T.id)
             FROM threads T JOIN messages M ON T.message_id=M.id
                            JOIN users U ON M.user_id=U.id
             WHERE T.id=:thread_id'''
    result = db.session.execute(text(sql), {'thread_id':thread_id})
    thread = result.fetchone()
    return thread

def add_thread(topic_id, message_id, title):
    sql = '''INSERT INTO threads (topic_id, message_id, title)
             VALUES (:topic_id, :message_id, :title)'''
    db.session.execute(text(sql), {'topic_id':topic_id, 'message_id':message_id, 'title':title})
    db.session.commit()
