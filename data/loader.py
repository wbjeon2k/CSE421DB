import json

import psycopg2 as pg2

if __name__ == '__main__':
    conn=pg2.connect(database="party_finder",user="postgres",password="ideal-entropy-fanfold-synopsis-grazier",host="localhost",port="55432")
    cur = conn.cursor()

    with open('./datasets/tags.json') as f:
        tags = json.load(f)
    for tag in tags:
        cur.execute('INSERT INTO Tag (tagID, name) VALUES (%s, %s)', (tag['id'], tag['name']))
    conn.commit()

    with open('./datasets/game_rank_list.json', encoding='utf-8') as f:
        games = json.load(f)
    for game in games:
        cur.execute('INSERT INTO Game (gameID, name) VALUES (%s, %s)', (game['id'], game['name']))
    conn.commit()

    with open('./datasets/game_tag_list.json') as f:
        game_tags = json.load(f)
    for game_tag in game_tags:
        for tag_id in game_tag['tags']:
            cur.execute('INSERT INTO Game_Tag (gameID, tagID) VALUES (%s, %s)', (game_tag['id'], tag_id))
    conn.commit()
