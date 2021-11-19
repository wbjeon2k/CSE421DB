import json
import os

import requests
from bs4 import BeautifulSoup


http_headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    ), # Chrome UA
}

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


if __name__ == '__main__':
    # set dataset directory, create directory if not exist
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(BASE_DIR, 'datasets')
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # create session
    session = requests.Session()

    tags = get_tags(session)
    with open(os.path.join(dataset_path, 'tags.json'), 'w') as f:
        json.dump(tags, f, ensure_ascii=False, indent=4)
