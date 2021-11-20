import json
import os
import time
import sys

import numpy as np
import requests
from bs4 import BeautifulSoup

http_headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    ), # Chrome UA
}

# parser = 'lxml'  # or html.parser

def get_tags(session):
    global http_headers
    tag_resp = session.get('https://club.steam250.com/tags', headers=http_headers)
    tag_soup = BeautifulSoup(tag_resp.text, 'lxml')
    tags = [
        {
            'id': int(each.a['href'].split('/')[-1]),  # Extract tag id fram URI
            'name': ' '.join([chunk for chunk in each.a.text.split(' ')[:-1]]), # Remove trailing number (=number of games which in that category)
        }
        for each in tag_soup.find('ol', class_='tags').find_all('li')
    ]
    return tags


def get_game_rank_list(session):
    global http_headers
    game_resp = session.get('https://steam250.com/top250', headers=http_headers)
    game_soup = BeautifulSoup(game_resp.text, 'lxml')
    games = []
    for i in range(1, 251):  # game rank from 1 to 250
        game_div = game_soup.find('div', id=str(i))
        img_src = game_div.find('div').a.img['data-src']
        games.append({
            'name': game_div.find(class_='title').a.text,
            'link': game_div.find('div').a['href'],
            'id': int(game_div.find('div').a['href'].split('/')[-1]),
            'img': (
                f'https:{img_src}' if img_src.startswith('//') else img_src  # add uri scheme
            ).replace('capsule_sm_120.jpg', 'capsule_184x69.jpg'),  # replace big size image
        })
    return games


def get_game_tag_list(session, link):
    global http_headers
    game_resp = session.get(link, headers=http_headers)
    game_soup = BeautifulSoup(game_resp.text, 'lxml')
    tags = [
        int(each.a['href'].split('/')[-1])
        for each in game_soup.find('ol', class_='tags').find_all('li')
    ]
    return {
        'id': int(link.split('/')[-1]),
        'tags': tags
    }


if __name__ == '__main__':
    # set dataset directory, create directory if not exist
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(BASE_DIR, 'datasets')
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # create session
    session = requests.Session()

    # ********** Download from server **********
    # Download tags
    # tags = get_tags(session)
    # with open(os.path.join(dataset_path, 'tags.json'), 'w') as f:
    #     json.dump(tags, f, ensure_ascii=False, indent=4)
    
    # Download game rank list
    # game_rank_list = get_game_rank_list(session)
    # with open(os.path.join(dataset_path, 'game_rank_list.json'), 'w', encoding='utf-8') as f:
    #     json.dump(game_rank_list, f, ensure_ascii=False, indent=4)
    
    # Download game-tag list
    # with open(os.path.join(dataset_path, 'game_rank_list.json'), encoding='utf-8') as f:
    #     game_rank_list = json.load(f)
    # game_tag_list = []
    # for idx, game_rank in enumerate(game_rank_list):
    #     sleep_time = np.random.normal(1.5, 0.2)
    #     print(f'{idx + 1} / {len(game_rank_list)} download...', end=' ')
    #     sys.stdout.flush()  # print msg in stdout
    #     game_tag_list.append(get_game_tag_list(session, game_rank['link']))
    #     print(f'end. (sleep={sleep_time:.2f}sec.)')
    #     time.sleep(sleep_time)  # random sleep for prevent ban
    # with open(os.path.join(dataset_path, 'game_tag_list.json'), 'w') as f:
    #     json.dump(game_tag_list, f, ensure_ascii=False, indent=4)

    # ********** Load from local **********
    # load tags from local file
    # with open(os.path.join(dataset_path, 'tags.json')) as f:
    #     tags = json.load(f)

    # load from 250 rank games from local file
    # with open(os.path.join(dataset_path, 'game_rank_list.json'), encoding='utf-8') as f:
    #     game_rank_list = json.load(f)

    # load from game-tag list from local file
    with open(os.path.join(dataset_path, 'game_tag_list.json'), encoding='utf-8') as f:
        game_tag_list = json.load(f)
    
    print(game_tag_list)
