import json
from datetime import datetime as dt  # datetime conflict? 

import psycopg2 as pg2
from psycopg2.sql import Identifier, SQL
from flask import Blueprint, Flask, redirect, render_template, url_for, request
from jinja2 import Template

from database import Connection
from models import *

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('games', __name__, url_prefix='/games')

# URI requirements
# https://superclass.notion.site/Service-URIs-6339514566164062998c57f690cbcc4c
# https://stackoverflow.com/questions/24892035/how-can-i-get-the-named-parameters-from-a-url-using-flask
# https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query

# /games 첫 페이지.
@bp.route('/')
def game_main():
    # 처음 /games 에 들어가면 보이는 table.
    game_default_sql = (
        'SELECT game_id, name, (SELECT COUNT(*) FROM party WHERE party.game_id = game.game_id) as popular '
        'FROM game ORDER BY name;'
    )
    # sort key 로 name/popular 들어왔을때 ASC order sort.
    game_order_by_sql = (
        'SELECT game_id, name, (SELECT COUNT(*) FROM party WHERE party.game_id = game.game_id) as popular '
        'FROM game ORDER BY {} {};'
    )
    conn = Connection.get_connect()
    cur = conn.cursor()

    sort_key_name = request.args.get('sort')
    order_key = request.args.get('order')

    if sort_key_name == None:
        # ?sort 가 없는 상황.
        cur.execute(game_default_sql, [])
    elif sort_key_name != None:
        cur.execute(game_order_by_sql.format(sort_key_name, order_key))
    else:
        # exception 을 던지지 않기 위한 예외처리.
        cur.execute(game_default_sql, [])

    all_game = cur.fetchall()

    # game table JSON serialize
    # print(all_game)
    all_game_list = []
    for games in all_game:
        all_game_list.append(GameModel(games[0], games[1], games[2]).serialize())

    # TODO: template html 파일 이름, parameter 확인
    return render_template('games.html', games=all_game_list)


# TODO: game/detail 연결하는 링크 없음!
@bp.route('/<int:gameid>/')
def game_detail(gameid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    
    game_sql = (
        'SELECT game_id, name, (SELECT COUNT(*) FROM party WHERE party.game_id = game.game_id) as popular '
        'FROM game WHERE game_id=%s;'
    )

    parties_in_game_sql = 'SELECT * FROM party WHERE game_id=%s;'

    reviews_in_game_sql = (
        'SELECT * FROM review WHERE review.review_id IN '
        '(SELECT game_review.review_id FROM game_review WHERE game_review.game_id=%s);'
    )

    review_avg_star_sql = (
        'SELECT AVG(score) FROM review WHERE review.review_id IN '
        '(SELECT game_review.review_id FROM game_review WHERE game_review.game_id=%s);'
    )

    tags_in_game_sql = (
        'SELECT * FROM tag WHERE tag.tag_id IN '
        '(SELECT game_tag.tag_id FROM game_tag WHERE game_tag.game_id=%s);'
    )

    cur.execute(game_sql, (gameid,))
    game_fetch = cur.fetchone()
    game = GameModel(*game_fetch).serialize()

    cur.execute(parties_in_game_sql, (gameid,))
    parties_in_game_fetch = cur.fetchall()
    parties_in_game = PartyModel.serialize_party_list(parties_in_game_fetch)

    cur.execute(reviews_in_game_sql, (gameid,))
    reviews_in_game_fetch = cur.fetchall()
    review_in_game_objs = [ReviewModel(*each) for each in reviews_in_game_fetch]
    reviews_in_game = ReviewModel.serialize_review_list(review_in_game_objs)

    cur.execute(review_avg_star_sql, (gameid,))
    review_avg_star = cur.fetchone()[0]

    cur.execute(tags_in_game_sql, (gameid,))
    tags_in_game_fetch = cur.fetchall()
    tag_objs = [TagModel(*each) for each in tags_in_game_fetch]
    tags_in_game = TagModel.serialize_tag_list(tag_objs)

    return render_template(
        'gameDetail.html', game=game, parties=parties_in_game, reviews=reviews_in_game, review_avg_star=review_avg_star, tags=tags_in_game
    )


@bp.route('/<int:gameid>/reviews/', methods=['POST'])
def game_review(gameid):
    conn = Connection.get_connect()
    cur = conn.cursor()

    # SQL query for insert to review, each column is id, create_datetime, content, score. After insert we can get review_id by RETURNING
    insert_review_query = 'INSERT INTO review VALUES (DEFAULT, %s, %s, %s) RETURNING review_id'  # create datetime, content, score
    # SQL query for insert to game_review, each column is review_id, game_id (game_review table is subclass of review table)
    insert_game_link_with_review_query = 'INSERT INTO game_review VALUES (%s, %s)'

    now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    score = request.form.get('score')
    content = request.form.get('content')

    cur.execute(insert_review_query, (now, content, score))
    review_id = cur.fetchone()[0]

    cur.execute(insert_game_link_with_review_query, (review_id, gameid))
    conn.commit()

    return redirect(url_for('games.game_detail', gameid=gameid))
