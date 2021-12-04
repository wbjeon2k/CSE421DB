import datetime

import flask

from database import Connection

# sql query 의 fetchall() 통해 불러온 list 를
# 각 모델의 serialize() method 를 통해 json 형식으로 변환 가능.
"""
#example usage

select_all = cur.fetchall() # get list of all cursor contents
ret = [] # make an empty list

#convert into json object
for t in select_all:
    ret.append(TestModel(t[0], t[1]).serialize())

# dump as a json object
to_json = json.dumps(ret)

#return json object
return to_json
"""

"""
cursor.fetchall() 을 통해서 가져온 데이터들을

return_list = []
for f in fetchall():
    return_list.append(f.serialize())

와 같은 방식으로 JSON serialize 하기 위한 인터페이스 입니다.
이런 방식으로 다른 테이블에 대한 인터페이스를 만들어도 되는지 의견 받고싶어요!
"""


def add_single_quote(string_input):
    return "'" + string_input + "'"


class TestModel:
    """Model for the test table"""

    __tablename__ = 'test'

    def __init__(self, id, msg, content):
        self.id = id
        self.msg = msg
        self.content = content

    def __repr__(self):
        return '<id {}>'.format(self.id)

    """for JSON type"""

    def serialize(self):
        return {'id': self.id, 'msg': self.msg, 'content': self.content}


class GameModel:
    """Model for the game table"""

    __tablename__ = 'test'

    def __init__(self, gameID, name, popular):
        self.gameID = gameID
        self.name = name
        self.popular = popular

    """for JSON type"""

    def serialize(self):
        # attributes in a same sequence as sql file!
        return dict(gameID=self.gameID, name=self.name, popular=self.popular)

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_game_list(list_of_games):
        ret = []
        for game in list_of_games:
            ret.append(GameModel(game[0], game[1], game[2]).serialize())
        return ret


class GameTagModel:
    """Model for the test table"""

    __tablename__ = 'test'

    def __init__(self, gameID, tagID):
        self.gameID = gameID
        self.tagID = tagID

    """for JSON type"""

    def serialize(self):
        return {
            'gameID': self.gameID,
            'tagID': self.tagID,
        }

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_game_list(list_of_gameTags):
        ret = []
        for tag in list_of_gameTags:
            ret.append(tag.serialize())
        return ret


class TagModel:
    """Model for the Tag table"""

    __tablename__ = 'Tag'

    def __init__(self, tagID, name):
        self.name = name
        self.tagID = tagID

    """for JSON type"""

    def serialize(self):
        return dict(tagID=self.tagID, name=self.name)

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_tag_list(list_of_tags):
        ret = []
        for tag in list_of_tags:
            ret.append(tag.serialize())
        return ret


class PartyModel:
    """Model for the party table"""

    __tablename__ = 'party'

    # gameName 필요하지 않은 경우.
    def __init__(self, partyID, name, playStartDatetime, leaderID, joinLink, gameID, popular=None, related_fetch=False):
        self.partyID = partyID
        self.name = name
        self.playStartDatetime = playStartDatetime
        self.leaderID = leaderID
        self.joinLink = joinLink
        self.gameID = gameID

        self.game = None
        self.leader = None
        self.popular = popular

        if related_fetch:
            conn = Connection.get_connect()
            cur = conn.cursor()

            game_retrieve_query = (
                'SELECT game_id, name, (SELECT COUNT(*) FROM party WHERE party.game_id = game.game_id) '
                'FROM game WHERE game_id=%s;'
            )
            cur.execute(game_retrieve_query, (gameID,))
            fetched_game = cur.fetchone()
            self.game = GameModel(*fetched_game).serialize()

            # Load leader(service_user) and assign to instance variable
            user_retrieve_query = 'SELECT * FROM service_user WHERE service_user_id=%s;'
            cur.execute(user_retrieve_query, (leaderID,))
            fetched_user = cur.fetchone()
            fetched_user = list(fetched_user)  # Convert to list type to delete item
            del fetched_user[3]
            del fetched_user[2]
            self.leader = ServiceUserModel(*fetched_user).serialize()

    def serialize(self):
        return dict(
            partyID=self.partyID,
            name=self.name,
            playStartDatetime=self.playStartDatetime,
            leaderID=self.leaderID,
            joinLink=self.joinLink,
            gameID=self.gameID,
            game=self.game,
            leader=self.leader,
            popular=self.popular
        )

    def set_game_name(self, game_name):
        self.gameName = str(game_name)

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_party_list(parties, related_fetch=True):
        return [PartyModel(*party, related_fetch=related_fetch).serialize() for party in parties]

    # parties 안에서 필요한 game list api.
    def serialize_game_list(list_of_games):
        ret = []
        for game in list_of_games:
            ret.append(dict(gameID=game[0], name=game[1]))
        return ret


class PostModel:
    """Model for the post table"""

    __tablename__ = 'post'

    # 자동으로 parameter 들을 넣어주는 방법은 찾지 못했습니다.
    # PartyModel(x[0], x[1], ....) 형태로 넣는 수 밖에 없습니다.
    def __init__(
        self,
        postID,
        title,
        content,
        createDatetime,
        isNotice,
        thumbsUp,
        thumbsDown,
        viewCount,
        service_user_id,
        boardID,
    ):
        self.postID = postID
        self.title = title
        self.content = content
        self.createDatetime = createDatetime
        self.isNotice = isNotice
        self.thumbsUp = thumbsUp
        self.thumbsDown = thumbsDown
        self.viewCount = viewCount
        self.service_user_id = service_user_id
        self.boardID = boardID

    def serialize(self):
        return {
            'postID': self.postID,
            'title': self.title,
            'content': self.content,
            'createDatetime': self.createDatetime,
            'isNotice': self.isNotice,
            'thumbsUp': self.thumbsUp,
            'thumbsDown': self.thumbsDown,
            'viewCount': self.viewCount,
            'service_user_id ': self.service_user_id,
            'boardID': self.boardID,
        }

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_post_list(list_of_post):
        ret = []
        for post in list_of_post:
            ret.append(post.serialize())
        return ret


class ReviewModel:
    """Model for the review table"""

    __tablename__ = 'review'

    # 자동으로 parameter 들을 넣어주는 방법은 찾지 못했습니다.
    # PartyModel(x[0], x[1], ....) 형태로 넣는 수 밖에 없습니다.
    def __init__(self, reviewID, createDatetime, content, score):
        self.reviewID = reviewID
        self.createDatetime = createDatetime
        self.content = content
        self.score = score

    def serialize(self):
        return {
            'reviewID': self.reviewID,
            'createDatetime': self.createDatetime,
            'content': self.content,
            'score': self.score,
        }

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_review_list(list_of_reviews):
        ret = []
        for rev in list_of_reviews:
            ret.append(rev.serialize())
        return ret


class ServiceUserModel:
    """Model for the ServiceUser table"""

    __tablename__ = 'ServiceUser'

    # encrypted pw skip!
    def __init__(self, service_user_id, email, nickname, isAdmin, clanID):
        self.service_user_id = service_user_id
        self.email = email
        self.nickname = nickname
        self.isAdmin = isAdmin
        self.clanID = clanID

    def serialize(self):
        return dict(
            service_user_id=self.service_user_id,
            email=self.email,
            # encryptedPassword=self.encryptedPassword,
            nickname=self.nickname,
            isAdmin=self.isAdmin,
            clanID=self.clanID,
        )

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_service_user_list(list_of_service_user):
        ret = []
        for usr in list_of_service_user:
            ret.append(usr.serialize())
        return ret
