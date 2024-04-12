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
    sql = '''SELECT replies.*
             FROM
               (SELECT B.id, B.username, A.id, A.message, A.date date,
                 (SELECT COUNT(*) FROM replies WHERE R.id=reply_to) reply_count,
                 D.username, C.message, C.date
               FROM replies R JOIN messages A ON R.message_id=A.id
                              JOIN users B ON B.id=A.user_id
                              LEFT JOIN messages C ON C.id=R.reply_to
                              LEFT JOIN users D ON D.id=C.user_id
               WHERE R.thread_id=:thread_id) replies
             ORDER BY
               CASE WHEN :order_by = 'most_recent' THEN replies.date END DESC,
               CASE WHEN :order_by = 'oldest' THEN replies.date END,
               CASE WHEN :order_by = 'most_replies' THEN replies.reply_count END DESC,
               replies.date DESC
             LIMIT :limit'''
    result = db.session.execute(text(sql), {'hread_id':thread_id, 'order_by':order_by, 'limit':limit})
    replies = result.fetchall()
    return replies