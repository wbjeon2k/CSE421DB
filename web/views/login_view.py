import json

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

# /login blueprint
bp = Blueprint('login', __name__, url_prefix='/login')

#/login with GET method
@bp.route('/', methods=['GET'])
def register_main_get():
    if 'user' in session:
        return redirect(url_for('/'))
    else:
        return render_template('login_template.html')
    
#/login with POST method  
@bp.route('/', methods=['POST'])
def register_main_get():
    if 'user' in session:
        #만약 로그인 되어있다면 main page redirect
        #TODO: 이렇게 redirect 하는게 맞는것인가? main page 로 redirect 되는지 check 필요.
        return redirect(url_for('/'))
    else:
        #email 을 통해 SerivceUser table 에서 찾는 sql form.
        find_user_sql = """
            SELECT COUNT(*) FROM SerivceUser WHERE email = %s;
        """
        conn = Connection.get_connect()
        cur = conn.cursor()
        
        login_email = request.form.get('email')
        cur.execute(find_user_sql, (login_email,))
        
        user_count = cur.fetchone()[0]
        
        if(user_count != 0):
            #해당 email 을 가진 user 있는 경우.
            request_pw = request.form.get('rawPassword')
            hashed_pw = hashlib.pbkdf2_hmac('sha256', request_pw, b'saltkeywordrandom', 150000)
            fetch_user_pw_sql = """
                SELECT encryptedPassword FROM SerivceUser WHERE email = %s;
            """
            cur.execute(fetch_user_pw_sql,(login_email,))
            fetched_hash_pw = cur.fetchone()[0]
            if(fetched_hash_pw == hashed_pw):
                #https://blog.d0ngd0nge.xyz/python-flask-session/
                #https://pythonise.com/series/learning-flask/flask-session-object
                #TODO: 각 session 별로 session 생기는건지 /
                #session이 global 이고, 'user' 별로 따로 user_dict 를 생성 하는지?
                user_dict = 
                session['user']=user_dict
            else:
                #TODO: login_template 이름, parameter 설정.
                return render_template('login_template.html', error='Wrong email or password')
        elif(user_count == 0):
            return render_template('login_template.html', error='Wrong email or password')
        else:
            return render_template('login_template.html', error='Wrong email or password')