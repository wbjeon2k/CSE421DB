# user profile
# 닉네임, admin 여부, 속한 클랜, 유저에 대한 리뷰, 유저가 남긴 리뷰
# style 통일: https://pypi.org/project/oitnb/
import json
from datetime import datetime as dt  # datetime conflict? 

import psycopg2 as pg2
from psycopg2.sql import Identifier, SQL
from flask import Blueprint, Flask, redirect, render_template, url_for, request, session
from jinja2 import Template

from database import Connection
from models import *

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/<int:userid>/')
def user_detail(userid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    
    user_sql = 'SELECT * FROM service_user WHERE service_user_id=%s'

    reviews_in_user_sql = (
        'SELECT * FROM review WHERE review.review_id IN '
        '(SELECT service_user_review.review_id FROM service_user_review WHERE service_user_review.service_user_id=%s);'
    )

    review_avg_star_sql = (
        'SELECT AVG(score) FROM review WHERE review.review_id IN '
        '(SELECT service_user_review.review_id FROM service_user_review WHERE service_user_review.service_user_id=%s);'
    )

    cur.execute(user_sql, (userid,))
    user_fetch = list(cur.fetchone())
    # Remove password and salt value from dict
    del user_fetch[3]
    del user_fetch[2]
    user = ServiceUserModel(*user_fetch).serialize()

    cur.execute(reviews_in_user_sql, (userid,))
    reviews_in_user_fetch = cur.fetchall()
    review_in_user_objs = [ReviewModel(*each, related_fetch=True) for each in reviews_in_user_fetch]
    reviews_in_user = ReviewModel.serialize_review_list(review_in_user_objs)

    cur.execute(review_avg_star_sql, (userid,))
    review_avg_star = cur.fetchone()[0]

    return render_template(
        'userDetail.html', user=user, reviews=reviews_in_user, review_avg_star=review_avg_star
    )


@bp.route('/<int:userid>/reviews/', methods=['POST'])
def user_review(userid):
    if 'user' not in session:
        return redirect(url_for('login.login_main'))
    
    if session['user']['service_user_id'] == userid:  # self rating is not available
        return redirect(url_for('users.user_detail', userid=userid))

    conn = Connection.get_connect()
    cur = conn.cursor()

    # SQL query for insert to review, each column is id, service_user_id, create_datetime, content, score. After insert we can get review_id by RETURNING
    insert_review_query = 'INSERT INTO review VALUES (DEFAULT, %s, %s, %s, %s) RETURNING review_id'  # create datetime, content, score
    # SQL query for insert to service_user_review, each column is review_id, service_user_id (service_user_review table is subclass of review table)
    insert_user_link_with_review_query = 'INSERT INTO service_user_review VALUES (%s, %s)'

    now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    score = request.form.get('score')
    content = request.form.get('content')
    service_user_id = session['user']['service_user_id']

    cur.execute(insert_review_query, (service_user_id, now, content, score))
    review_id = cur.fetchone()[0]

    cur.execute(insert_user_link_with_review_query, (review_id, userid))
    conn.commit()

    return redirect(url_for('users.user_detail', userid=userid))
