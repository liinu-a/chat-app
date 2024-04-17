from flask import session
from sqlalchemy.sql import text
from db import db

def add_message(message):
    sql = '''INSERT INTO messages (user_id, message)
                 VALUES (:user_id, :message) RETURNING id'''
    result = db.session.execute(text(sql), {'user_id':session['user_id'], 'message':message})
    id = result.fetchone()[0]
    db.session.commit()
    return id

def get_replies(thread_id, order_by, limit):
    sql = '''SELECT comments.*
             FROM
               (SELECT B.id, B.username, A.id, A.message, A.date sent,
                 (SELECT COUNT(*) FROM replies WHERE A.id=reply_to) reply_count,
                 D.username, C.message, C.date, C.id
               FROM replies R JOIN messages A ON R.message_id=A.id
                              JOIN users B ON B.id=A.user_id
                              LEFT JOIN messages C ON C.id=R.reply_to
                              LEFT JOIN users D ON D.id=C.user_id
               WHERE R.thread_id=:thread_id) comments
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN comments.sent END DESC,
               CASE WHEN :order_by = 'oldest' THEN comments.sent END,
               CASE WHEN :order_by = 'most_replies' THEN comments.reply_count END DESC,
               comments.sent DESC
             LIMIT :limit'''
    result = db.session.execute(text(sql), {'thread_id':thread_id, 'order_by':order_by, 'limit':limit})
    comments = result.fetchall()
    return comments

def get_message(message_id):
    sql = '''SELECT U.username, M.message, M.date 
             FROM messages M JOIN users U ON M.user_id=U.id 
             WHERE M.id=:message_id'''
    result = db.session.execute(text(sql), {'message_id':message_id})
    message = result.fetchone()
    return message

def get_init_message(thread_id):
    sql = '''SELECT U.username, M.message, M.date, T.title
             FROM threads T JOIN messages M ON T.message_id=M.id
                            JOIN users U ON U.id=M.user_id
             WHERE T.id=:thread_id'''
    result = db.session.execute(text(sql), {'thread_id':thread_id})
    init_message = result.fetchone()
    return init_message

def add_reply(thread_id, message_id, reply_to):
    sql = '''INSERT INTO replies (thread_id, message_id, reply_to)
                 VALUES (:thread_id, :message_id, :reply_to)'''
    db.session.execute(text(sql), {'thread_id':thread_id, 'message_id':message_id, 'reply_to':reply_to})
    db.session.commit()