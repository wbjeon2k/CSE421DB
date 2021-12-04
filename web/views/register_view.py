import json
import sys
from . import *
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

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('register', __name__, url_prefix='/register')

@bp.route('/', methods=['GET', 'POST'])
def register_main_get():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('main'))
        else:
            return render_template('register.html')
    
    elif request.method == 'POST':
        if 'user' in session:
            return redirect(url_for('/main'))
        else:
            register_email = request.form.get('email')
            register_nickname = request.form.get('nickname')
            find_duplicate_sql = "SELECT COUNT(*) FROM {} WHERE (service_user.email = {} OR service_user.nickname = {});"
            conn = Connection.get_connect()
            cur = conn.cursor()
            print(register_email, register_nickname)
            register_email = add_single_quote(register_email)
            register_nickname = add_single_quote(register_nickname)
            #!!! @ 가 문자 그대로 들어가면 postgres 지정 연산자와 충돌 !!!
            register_email = register_email.replace("@", "at")
            cur.execute(find_duplicate_sql.format("service_user",register_email,register_nickname))
            duplicate_cnt = cur.fetchone()[0]
            if(duplicate_cnt != 0):
                return render_template('register.html', error = "User with the email or the nickname exists")
            elif(duplicate_cnt == 0):
                raw_pw = request.form['rawPassword']
                #TODO: salt 값 user 별로 random
                hash_pw = hashlib.pbkdf2_hmac('sha256', raw_pw.encode(), b'saltkeywordrandom', 150000)
                enc_pw = hash_pw.hex()
                enc_pw = add_single_quote(enc_pw)
                insert_user_sql = "INSERT INTO service_user VALUES (DEFAULT,{},{},{},DEFAULT,NULL);"
                
                #TODO: session 과 연결을 해야하는가? 자동 로그인 하는걸로 
                try:
                    cur.execute(insert_user_sql.format(register_email, enc_pw, register_nickname))
                    conn.commit()
                    sys.stdout.write(str(register_email)+str(enc_pw))
                    sys.stdout.flush()
                except Exception as e:
                    conn.rollback()
                    return render_template('register.html', error = "User register failed. Try again.")
                #session 을 하면 main page로 redirect
                return redirect(url_for('login.login_main'))
            else:
                return render_template('register.html', error = "Unknown register error. Try again.")
    