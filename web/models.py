import flask
import datetime

#sql query 의 fetchall() 통해 불러온 list 를
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

'''
cursor.fetchall() 을 통해서 가져온 데이터들을

return_list = []
for f in fetchall():
    return_list.append(f.serialize())
    
와 같은 방식으로 JSON serialize 하기 위한 인터페이스 입니다.
이런 방식으로 다른 테이블에 대한 인터페이스를 만들어도 되는지 의견 받고싶어요!
'''

class TestModel:
    """Model for the test table"""
    __tablename__ = 'test'
    
    def __init__(self,id,msg,content):
        self.id = id
        self.msg = msg
        self.content = content
        
    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    """for JSON type"""
    def serialize(self):
        return {
            'id': self.id, 
            'msg': self.msg,
            'content': self.content
        }

class PartyModel:
    """Model for the party table"""
    __tablename__ = 'party'
    
    # 자동으로 parameter 들을 넣어주는 방법은 찾지 못했습니다.
    # PartyModel(x[0], x[1], ....) 형태로 넣는 수 밖에 없습니다.
    def __init__(self,partyID,name,playStartDatetime,leaderID, joinLink, gameID):
        self.partyID = partyID 
        self.name = name 
        self.playStartDatetime = playStartDatetime 
        self.leaderID = leaderID 
        self.joinLink = joinLink 
        self.gameID = gameID
        
    def serialize(self):
        return {
            'partyID' : self.partyID,
            'name' : self.name,
            'playStartDatetime' : self.playStartDatetime,
            'leaderID' : self.leaderID,
            'joinLink' : self.joinLink,
            'gameID' : self.gameID
        }
    
    #cursor.fetchall() 을 통해 받아온 리스트 전체를
    #JSON 형태로 serialize 하는 메서드 입니다.
    def serialize_party_list(list_of_party):
        ret = []
        for party in list_of_party:
                ret.append(party.serialize())
            
        
        return ret