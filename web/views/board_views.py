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
    # Get clan board using clan_id of loggedin user
    retrieve_board_query = 'SELECT * FROM board WHERE clan_id=%s'
    # Get recent 10 posts which match with board id
    retrieve_post_query = 'SELECT * FROM post WHERE board_id=%s ORDER BY create_datetime DESC LIMIT 10'

    # Get my clan board and posts
    my_clan_board = None
    my_clan_post_recent = None
    if 'user' in session and session['user'].get('clan_id'):  # If logged in and user has clan
        cur.execute(retrieve_board_query, (session['user'].get('clan_id'),))
        my_clan_board_fetch = cur.fetchone()
        my_clan_board = BoardModel(*my_clan_board_fetch, related_fetch=True).serialize()

        cur.execute(retrieve_post_query, (my_clan_board['board_id'],))
        clan_post_recent_fetch = cur.fetchall()
        clan_post_recent_objs = [PostModel(*each, related_fetch=True) for each in clan_post_recent_fetch]
        my_clan_post_recent = PostModel.serialize_post_list(clan_post_recent_objs)
    
    # Get free board and posts
    cur.execute(retrieve_board_query, (None,))
    free_board_fetch = cur.fetchone()
    free_board = BoardModel(*free_board_fetch, related_fetch=True).serialize()

    cur.execute(retrieve_post_query, (free_clan_board['board_id'],))
    free_post_recent_fetch = cur.fetchall()
    free_post_recent_objs = [PostModel(*each, related_fetch=True) for each in free_post_recent_fetch]
    free_post_recent = PostModel.serialize_post_list(free_post_recent_objs)

    return render_template(
        'boards.html', my_clan_board=my_clan_board, my_clan_post_recent=my_clan_post_recent, free_board=free_board, free_post_recent=free_post_recent
    )