from flask import session
from sqlalchemy.sql import text
from db import db

def get_topic_threads(topic, order_by, limit):
    sql = '''SELECT threads.*
             FROM
               (SELECT U.id, U.username, A.title, A.id, M.message, M.date created,
                 (SELECT COUNT(*) FROM replies WHERE A.id=thread_id) replies, COUNT(*) OVER(),
                 :user_id IN (SELECT user_id FROM pinned_threads WHERE thread_id=A.id), M.id
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
    try:
        user_id = session['user_id']
    except:
        user_id = 0

    result = db.session.execute(text(sql), {'user_id':user_id, 'topic':topic, 'order_by':order_by, 
                                            'limit':limit})
    threads = result.fetchall()
    return threads


def get_all_threads(order_by, limit):
    sql = '''SELECT threads.*
             FROM
               (SELECT U.id, U.username, T.title, T.id, M.message, M.date created,
                 (SELECT COUNT(*) FROM replies WHERE T.id=thread_id) replies, COUNT(*) OVER(),
                 :user_id IN (SELECT user_id FROM pinned_threads WHERE thread_id=T.id), M.id
                FROM threads T JOIN messages M on T.message_id=M.id
                               JOIN users U ON M.user_id=U.id) threads
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN threads.created END DESC,
               CASE WHEN :order_by = 'oldest' THEN threads.created END,
               CASE WHEN :order_by = 'most_replies' THEN threads.replies END DESC,
               threads.created DESC
             LIMIT :limit'''
    try:
        user_id = session['user_id']
    except:
        user_id = 0

    result = db.session.execute(text(sql), {'user_id':user_id, 'order_by':order_by, 'limit':limit})
    threads = result.fetchall()
    return threads

def pinned(order_by, limit):
    sql = '''SELECT threads.*
             FROM
               (SELECT U.id, U.username, T.title, T.id, M.message, M.date created,
                 (SELECT COUNT(*) FROM replies WHERE T.id=thread_id) replies,
                 COUNT(*) OVER(), True, M.id, P.id pinned
               FROM pinned_threads P JOIN threads T ON P.thread_id=T.id
                                   JOIN Messages M on M.id=T.message_id
                                   JOIN users U ON U.id=M.user_id
               WHERE P.user_id=:user_id) threads
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN threads.created END DESC,
               CASE WHEN :order_by = 'oldest' THEN threads.created END,
               CASE WHEN :order_by = 'most_replies' THEN threads.replies END DESC,
               CASE WHEN :order_by = 'newest_pin' THEN threads.pinned END DESC,
               CASE WHEN :order_by = 'oldest_pin' THEN threads.pinned END,
               threads.pinned DESC
             LIMIT :limit'''
    result = db.session.execute(text(sql), {'user_id':session['user_id'], 'order_by':order_by, 'limit':limit})
    threads = result.fetchall()
    return threads


def search(order_by, limit):
    sql = '''SELECT threads.*
             FROM
               (SELECT U.id, U.username, T.title, T.id, M.message, M.date created,
                 (SELECT COUNT(*) FROM replies WHERE T.id=thread_id) replies, COUNT(*) OVER(),
                 :user_id IN (SELECT user_id FROM pinned_threads WHERE thread_id=T.id), M.id
                FROM threads T JOIN messages M on T.message_id=M.id
                               JOIN users U ON M.user_id=U.id
                WHERE T.title LIKE :query OR M.message LIKE :query) threads
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN threads.created END DESC,
               CASE WHEN :order_by = 'oldest' THEN threads.created END,
               CASE WHEN :order_by = 'most_replies' THEN threads.replies END DESC,
               threads.created DESC
             LIMIT :limit'''
    try:
        user_id = session['user_id']
    except:
        user_id = 0

    result = db.session.execute(text(sql), {'user_id':user_id, 'query':"%"+session['query']+"%", 
                                            'order_by':order_by, 'limit':limit})
    threads = result.fetchall()
    return threads


def get_thread(thread_id):
    sql = '''SELECT U.id, U.username, T.title, M.id, M.message, M.date,
               (SELECT COUNT(*) FROM replies WHERE thread_id=T.id),
               :user_id IN (SELECT user_id FROM pinned_threads WHERE thread_id=T.id)
             FROM threads T JOIN messages M ON T.message_id=M.id
                            JOIN users U ON M.user_id=U.id
             WHERE T.id=:thread_id'''
    try:
        user_id = session['user_id']
    except:
        user_id = 0

    result = db.session.execute(text(sql), {'thread_id':thread_id, 'user_id':user_id})
    thread = result.fetchone()
    return thread

def add_thread(topic_id, message_id, title):
    sql = '''INSERT INTO threads (topic_id, message_id, title)
             VALUES (:topic_id, :message_id, :title) RETURNING id'''
    result = db.session.execute(text(sql), {'topic_id':topic_id, 'message_id':message_id, 'title':title})
    id = result.fetchone()[0]
    db.session.commit()
    return id

def pin(thread_id):
    sql = 'INSERT INTO pinned_threads (user_id, thread_id) VALUES (:user_id, :thread_id)'
    db.session.execute(text(sql), {'user_id':session['user_id'], 'thread_id':thread_id})
    db.session.commit()

def unpin(thread_id):
    sql = 'DELETE FROM pinned_threads WHERE user_id=:user_id AND thread_id=:thread_id'
    db.session.execute(text(sql), {'user_id':session['user_id'], 'thread_id':thread_id})
    db.session.commit()
