import json
from datetime import datetime as dt  # datetime conflict? 

import psycopg2 as pg2
from psycopg2.sql import Identifier, SQL
from flask import Blueprint, Flask, redirect, render_template, url_for, request, session
from jinja2 import Template

from database import Connection
from models import *

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('boards', __name__, url_prefix='/boards')


@bp.route('/')
def board_main():
    conn = Connection.get_connect()
    cur = conn.cursor()
    # Get clan board using clan_id of loggedin user
    retrieve_board_query = 'SELECT * FROM board WHERE clan_id=%s'
    retrieve_free_board_query = 'SELECT * FROM board WHERE clan_id IS NULL'
    # Get recent 10 posts which match with board id
    retrieve_post_query = 'SELECT * FROM post WHERE board_id=%s ORDER BY create_datetime DESC LIMIT 10'

    # Get my clan board and posts
    my_clan_board = []
    my_clan_post_recent = []
    if 'user' in session and session['user'].get('clan_id'):  # If logged in and user has clan
        cur.execute(retrieve_board_query, (session['user'].get('clan_id'),))
        my_clan_board_fetch = cur.fetchone()
        my_clan_board = BoardModel(*my_clan_board_fetch, related_fetch=True).serialize()

        cur.execute(retrieve_post_query, (my_clan_board['board_id'],))
        clan_post_recent_fetch = cur.fetchall()
        clan_post_recent_objs = [PostModel(*each, related_fetch=True) for each in clan_post_recent_fetch]
        my_clan_post_recent = PostModel.serialize_post_list(clan_post_recent_objs)
    
    # Get free board and posts
    cur.execute(retrieve_free_board_query)
    free_board_fetch = cur.fetchone()
    free_board = BoardModel(*free_board_fetch, related_fetch=True).serialize()

    cur.execute(retrieve_post_query, (free_board['board_id'],))
    free_post_recent_fetch = cur.fetchall()
    free_post_recent_objs = [PostModel(*each, related_fetch=True) for each in free_post_recent_fetch]
    free_post_recent = PostModel.serialize_post_list(free_post_recent_objs)

    return render_template(
        'boards.html', my_clan_board=my_clan_board, my_clan_post_recent=my_clan_post_recent, free_board=free_board, free_post_recent=free_post_recent
    )

@bp.route('/<boardtype>/')
def board_detail(boardtype):
    conn = Connection.get_connect()
    cur = conn.cursor()

    # If user exist, set user and if that user has clan, set clan_id variable
    user = None
    clan_id = None
    if 'user' in session:
        user = session['user']
        if 'clanID' in user:
            clan_id = user['clanID']
        elif boardtype == 'clan':  # User has not clan but try to access clan board -> redirect
            return redirect(url_for('boards.board_main'))
    elif boardtype == 'clan':  # Not logged in but try to access clan boadrd -> redirect to login
            return redirect(url_for('login.login_main'))

    retrieve_notice_post = 'SELECT * FROM post WHERE board_id=%s'
    
    if boardtype == 'free':  # Set variable for free board
        retrieve_board_query = 'SELECT board_id FROM board WHERE clan_id is NULL'
        cur.execute(retrieve_board_query)
        board_id = cur.fetchone()[0]
    elif boardtype == 'clan':  # Ser variable for clan board
        retrieve_board_query = 'SELECT board_id FROM board WHERE clan_id=%s'
        cur.execute(retrieve_board_query, (clan_id,))
        board_id = cur.fetchone()[0]
    
    # Get notice post in this board -> if isNotice flag set to true, that post is notice.
    retrieve_notice_query = 'SELECT * FROM post WHERE board_id=%s WHERE isNotice=true ORDER BY create_datetime DESC'
    # Get all post which in this board
    retrieve_post_query = 'SELECT * FROM post WHERE board_id=%s ORDER BY create_datetime DESC'

    cur.execute(retrieve_notice_post, (board_id,))
    notice_fetch = cur.fetchall()
    notice_objs = [PostModel(*each, related_fetch=True) for each in notice_fetch]
    notice_posts = PostModel.serialize_post_list(notice_objs)

    cur.execute(retrieve_post_query, (board_id,))
    post_fetch = cur.fetchall()
    post_objs = [PostModel(*each, related_fetch=True) for each in post_fetch]
    post = PostModel.serialize_post_list(post_objs)

    return render_template(
        'boardDetail.html', boardtype=boardtype, notice_posts=notice_posts, post=post
    )