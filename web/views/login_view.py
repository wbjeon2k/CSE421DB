import json
from base64 import b64encode

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from flask import session, request
from psycopg2 import sql
from psycopg2.sql import SQL
from database import Connection
from models import *
from datetime import datetime, timezone
from database import Connection
from models import *
import hashlib
import sys

# /login blueprint
bp = Blueprint('login', __name__, url_prefix='/login')

# method 나누는게 아니라, 안에서 구분.
# /login with GET method
@bp.route('/', methods=['GET', 'POST'])
def login_main():
    # TODO: if request.method == 'GET'
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('main'))
        else:
            return render_template('login.html')

    elif request.method == 'POST':
        if 'user' in session:
            # 만약 로그인 되어있다면 main page redirect
            # TODO: 이렇게 redirect 하는게 맞는것인가? main page 로 redirect 되는지 check 필요.
            return redirect(url_for('main'))
        """
        session.get('user') and session['user'].get('user_id')
        """
        # email 을 통해 service_user table 에서 찾는 sql form.
        find_user_sql = 'SELECT COUNT(*) FROM service_user WHERE (service_user.email = %s); '
        conn = Connection.get_connect()
        cur = conn.cursor()

        login_email = request.form.get('email')
        login_email = login_email.replace('@', 'at')

        cur.execute(find_user_sql, (login_email,))

        tmp = cur.fetchone()
        # print(tmp)
        user_count = tmp[0]
        all_user_cnt_sql = 'SELECT COUNT(*) FROM service_user;'
        cur.execute(all_user_cnt_sql)
        all_user_cnt = cur.fetchone()
        sys.stdout.write(str(login_email) + str(tmp) + str(all_user_cnt))
        sys.stdout.flush()

        if user_count != 0:
            fetch_user_pw_sql = (
                'SELECT salt, encrypted_password FROM service_user WHERE (email = %s);'
            )
            cur.execute(fetch_user_pw_sql, (login_email,))
            fetched_salt, fetched_hash_pw = cur.fetchone()

            # 해당 email 을 가진 user 있는 경우.
            request_pw = request.form.get('rawPassword')
            # TODO: salt 값 user 별로 random
            h_pw = hashlib.pbkdf2_hmac(
                'sha3-256', request_pw.encode(), fetched_salt.encode(), 150000
            )
            enc_input_pw = b64encode(h_pw).decode()

            # sys.stdout.write(str(fetched_hash_pw) + ' ' + str(hashed_pw))
            # sys.stdout.flush()

            if fetched_hash_pw == enc_input_pw:
                # https://blog.d0ngd0nge.xyz/python-flask-session/
                # https://pythonise.com/series/learning-flask/flask-session-object

                fetch_user_sql = 'SELECT * FROM service_user WHERE (email = %s);'
                cur.execute(fetch_user_sql, (login_email,))
                fetched_user = cur.fetchone()

                # user_dict = ServiceUserModel(
                #     fetched_user[0],
                #     fetched_user[1],
                #     fetched_user[3],
                #     fetched_user[4],
                #     fetched_user[5],
                # ).serialize()
                user_dict = ServiceUserModel(*fetched_user[:6]).serialize()
                session['user'] = user_dict
                return redirect(url_for('main'))
            else:
                # TODO: login_template 이름, parameter 설정.
                return render_template('login.html', error='Wrong email or password')
        elif user_count == 0:
            return render_template('login.html', error='Wrong email or password')
        else:
            return render_template('login.html', error='Wrong email or password')
