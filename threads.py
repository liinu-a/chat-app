from flask import session
from sqlalchemy.sql import text
from db import db

def get_threads(topic, order_by, limit):
    sql = '''SELECT threads.*
             FROM
               (SELECT U.id, U.username, A.title, A.id, M.message, M.date created,
                 (SELECT COUNT(*) FROM replies WHERE A.id=thread_id) replies,
                 COUNT(*) OVER(),
                 :user_id IN (SELECT user_id FROM pinned_threads WHERE thread_id=A.id)
               FROM threads A JOIN topics B ON A.topic_id=B.id
                              JOIN messages M on A.message_id=M.id
                              JOIN users U ON M.user_id=U.id
               WHERE B.topic=:topic) threads
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN threads.created END DESC,
               CASE WHEN :order_by = 'oldest' THEN threads.created END,
               CASE WHEN :order_by = 'most_replies' THEN threads.replies END DESC,
               threads.created DESC
             LIMIT :limit'''
    result = db.session.execute(text(sql), {'user_id':session['user_id'], 'topic':topic, 'order_by':order_by, 'limit':limit})
    threads = result.fetchall()
    return threads

def get_thread(thread_id):
    sql = '''SELECT U.id, U.username, T.title, M.id, M.message, M.date,
               (SELECT COUNT(*) FROM replies WHERE thread_id=T.id)
             FROM threads T JOIN messages M ON T.message_id=M.id
                            JOIN users U ON M.user_id=U.id
             WHERE T.id=:thread_id'''
    result = db.session.execute(text(sql), {'thread_id':thread_id})
    thread = result.fetchone()
    return thread

def add_thread(topic_id, message_id, title):
    sql = '''INSERT INTO threads (topic_id, message_id, title)
             VALUES (:topic_id, :message_id, :title) RETURNING id'''
    result = db.session.execute(text(sql), {'topic_id':topic_id, 'message_id':message_id, 'title':title})
    id = result.fetchone()[0]
    db.session.commit()
    return id
