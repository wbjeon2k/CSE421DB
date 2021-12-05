import sys
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


@bp.route('/<boardtype>/new/', methods=['GET', 'POST'])
def post_new(boardtype):
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

    # Query for get clan
    retrieve_clan_query = 'SELECT * FROM clan WHERE clan_id=%s'
    cur.execute(retrieve_clan_query, (clan_id,))
    clan_fetch = cur.fetchone()
    clan = ClanModel(*clan_fetch, related_fetch=True).serialize()

    if request.method == 'GET':
        return render_template(
            'newPost.html', boardtype=boardtype, clan=clan
        )
    elif request.method == 'POST':
        isNotice = request.form.get('isNotice', 'false')
        if isNotice == 'on':  # If checkbox checked -> value set 'on'
            isNotice = 'true'
        if session['user']['service_user_id'] != clan['leader_id']:  # logged in user is not leader of clan -> cannot write notice
            isNotice = 'false'
            
        title = request.form.get('title')
        content = request.form.get('content')

        # Create post; parameter of each position is;
        # post_id, *title, *content, *create_datetime, *isNotice, thumbsUp, thumsDown, viewCount, *service_user_id, *board_id
        # After insert, get post_id to using RETURNING
        create_post_query = 'INSERT INTO post VALUES (DEFAULT, %s, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, %s, %s) RETURNING post_id'

        now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(create_post_query, (title, content, now, isNotice, user['service_user_id'], board_id))
        post_id = cur.fetchone()[0]
        return redirect(url_for('boards.post_detail', boardtype=boardtype, postid=post_id))


@bp.route('/<boardtype>/<int:postid>/')
def post_detail(boardtype, postid):
    conn = Connection.get_connect()
    cur = conn.cursor()

    user_clan_id = None
    if 'user' in session:
        user_clan_id = session['user'].get('clanID')

    retrieve_post_query = 'SELECT * FROM post WHERE post_id=%s'
    cur.execute(retrieve_post_query, (postid,))
    post_fetch = cur.fetchone()
    post = PostModel(*post_fetch, related_fetch=True).serialize()

    retrieve_comment_query = 'SELECT * FROM comment WHERE post_id=%s'
    cur.execute(retrieve_comment_query, (post['post_id'],))
    comment_fetch = cur.fetchall()
    comment_objs = [CommentModel(*each, related_fetch=True) for each in comment_fetch]
    comments = CommentModel.serialize_comment_list(comment_objs)

    # boardtype cannot restrict clan board
    # So, we have permission check using post id (post -> board -> clan)
    retrieve_board_query = 'SELECT * FROM board WHERE board_id=%s'
    cur.execute(retrieve_board_query, (post['board_id'],))
    board_fetch = cur.fetchone()
    board = BoardModel(*board_fetch, related_fetch=True).serialize()

    board_clan_id = board['clan_id']

    user_has_permission = False
    if board_clan_id is None:  # free board
        user_has_permission = True
    elif user_clan_id is None:  # If user not logged in or has not clan -> cannot use clan board
        user_has_permission = False
    elif user_clan_id != board_clan_id:  # User is not this clan member
        user_has_permission = False
    else:  # User has permission
        user_has_permission = True

    if user_has_permission:
        return render_template(
            'postDetail.html', post=post, comments=comments
        )
    else:
        return redirect(url_for('boards.board_detail', boardtype=boardtype))
