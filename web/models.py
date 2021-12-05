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
    def __init__(self, reviewID, service_user_id, createDatetime, content, score, related_fetch=False):
        self.service_user_id = service_user_id
        self.reviewID = reviewID
        self.createDatetime = createDatetime
        self.content = content
        self.score = score

        if related_fetch:
            conn = Connection.get_connect()
            cur = conn.cursor()
            
            # Load leader(service_user) and assign to instance variable
            user_retrieve_query = 'SELECT * FROM service_user WHERE service_user_id=%s;'
            cur.execute(user_retrieve_query, (service_user_id,))
            fetched_user = cur.fetchone()
            fetched_user = list(fetched_user)  # Convert to list type to delete item
            del fetched_user[3]
            del fetched_user[2]
            self.service_user = ServiceUserModel(*fetched_user).serialize()

    def serialize(self):
        return {
            'reviewID': self.reviewID,
            'service_user_id': self.service_user_id,
            'createDatetime': self.createDatetime,
            'content': self.content,
            'score': self.score,
            'service_user': self.service_user,
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


class ClanModel:
    """Model for the Clan table"""

    __tablename__ = 'Clan'

    def __init__(self, clan_id, name, leader_id, popular=None, related_fetch=False):
        self.clan_id = clan_id
        self.name = name
        self.leader_id = leader_id
        self.popular = popular

        self.leader = None
        
        if related_fetch:
            conn = Connection.get_connect()
            cur = conn.cursor()
            
            # Load leader(service_user) and assign to instance variable
            user_retrieve_query = 'SELECT * FROM service_user WHERE service_user_id=%s;'
            cur.execute(user_retrieve_query, (leader_id,))
            fetched_user = cur.fetchone()
            fetched_user = list(fetched_user)  # Convert to list type to delete item
            del fetched_user[3]
            del fetched_user[2]
            self.leader = ServiceUserModel(*fetched_user).serialize()

    def serialize(self):
        return dict(
            clan_id=self.clan_id,
            name=self.name,
            leader_id=self.leader_id,
            leader=self.leader,
            popular=self.popular
        )

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_clan_list(clans):
        ret = []
        for clan in clans:
            ret.append(clan.serialize())
        return ret


class BoardModel:
    """Model for the Clan table"""

    __tablename__ = 'Board'

    def __init__(self, board_id, clan_id, related_fetch=False):
        self.board_id = board_id
        self.clan_id = clan_id

        self.clan = None
        
        if related_fetch and clan_id is not None:
            conn = Connection.get_connect()
            cur = conn.cursor()
            
            # Load clan and assign to instance variable
            clan_retrieve_query = 'SELECT * FROM clan WHERE clan_id=%s;'
            cur.execute(clan_retrieve_query, (clan_id,))
            fetched_clan = cur.fetchone()
            self.clan = ClanModel(*fetched_clan).serialize()

    def serialize(self):
        return dict(
            board_id=self.board_id,
            clan_id=self.clan_id,
            clan=self.clan,
        )

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_board_list(clans):
        ret = []
        for clan in clans:
            ret.append(clan.serialize())
        return ret


class PostModel:
    """Model for the Clan table"""

    __tablename__ = 'Post'

    """
	post_id               SERIAL,
	title                VARCHAR(128) NOT NULL,
	content              TEXT NOT NULL,
	create_datetime      TIMESTAMP NOT NULL,
	isNotice            BOOLEAN NOT NULL DEFAULT false,
	thumbsUp            INTEGER NOT NULL DEFAULT 0,
	thumbsDown          INTEGER NOT NULL DEFAULT 0,
	viewCount           INTEGER NOT NULL DEFAULT 0,
	service_user_id               INTEGER NOT NULL,
	board_id              INTEGER NULL
    """

    def __init__(
        self, post_id, title, content, create_datetime, isNotice, thumbsUp, thumbsDown,
        viewCount, service_user_id, board_id, related_fetch=False):
        self.post_id = post_id
        self.title = title
        self.create_datetime = create_datetime
        self.isNotice = isNotice
        self.thumbsUp = thumbsUp
        self.thumbsDown = thumbsDown
        self.viewCount = viewCount
        self.service_user_id = service_user_id
        self.board_id = board_id

        self.service_user = None
        self.board = None
        
        if related_fetch:
            conn = Connection.get_connect()
            cur = conn.cursor()
            
            # Load writer(service_user) and assign to instance variable
            service_user_retrieve_query = 'SELECT * FROM service_user WHERE service_user_id=%s;'
            cur.execute(service_user_retrieve_query, (service_user_id,))
            fetched_user = cur.fetchone()
            fetched_user = list(fetched_user)  # Convert to list type to delete item
            del fetched_user[3]
            del fetched_user[2]
            self.service_user = ServiceUserModel(*fetched_user).serialize()
            
            # Load writer(service_user) and assign to instance variable
            board_retrieve_query = 'SELECT * FROM board WHERE board_id=%s;'
            cur.execute(board_retrieve_query, (board_id,))
            fetched_board = cur.fetchone()
            self.board = BoardModel(*fetched_board).serialize()

    def serialize(self):
        return dict(
            post_id=self.post_id,
            title=self.title,
            create_datetime=self.create_datetime,
            isNotice=self.isNotice,
            thumbsUp=self.thumbsUp,
            thumbsDown=self.thumbsDown,
            viewCount=self.viewCount,
            service_user_id=self.service_user_id,
            board_id=self.board_id,
            service_user=self.service_user,
            board=self.board,
        )

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_post_list(posts):
        ret = []
        for post in posts:
            ret.append(post.serialize())
        return ret


class CommentModel:
    """Model for the Comment table"""

    __tablename__ = 'Comment'

    def __init__(self, comment_id, content, create_datetime, service_user_id, post_id, related_fetch=False):
        self.comment_id = comment_id
        self.content = content
        self.create_datetime = create_datetime
        self.service_user_id = service_user_id
        self.post_id = post_id

        self.service_user = None
        
        if related_fetch:
            conn = Connection.get_connect()
            cur = conn.cursor()
            
            # Load leader(service_user) and assign to instance variable
            user_retrieve_query = 'SELECT * FROM service_user WHERE service_user_id=%s;'
            cur.execute(user_retrieve_query, (leader_id,))
            fetched_user = cur.fetchone()
            fetched_user = list(fetched_user)  # Convert to list type to delete item
            del fetched_user[3]
            del fetched_user[2]
            self.leader = ServiceUserModel(*fetched_user).serialize()
            
            # Load post and assign to instance variable
            post_retrieve_query = 'SELECT * FROM post WHERE post_id=%s;'
            cur.execute(post_retrieve_query, (post_id,))
            fetched_post = cur.fetchone()
            self.post = ServiceUserModel(*fetched_post).serialize()

    def serialize(self):
        return dict(
            comment_id=self.comment_id,
            content=self.content,
            create_datetime=self.create_datetime,
            service_user_id=self.service_user_id,
            post_id=self.post_id,
            service_user=self.service_user,
            post=self.post,
        )

    # cursor.fetchall() 을 통해 받아온 리스트 전체를
    # JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_comment_list(comments):
        ret = []
        for comment in comments:
            ret.append(comment.serialize())
        return ret
