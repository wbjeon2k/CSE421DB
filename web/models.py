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
        
    def serialize_party_list(list_of_party):
        ret = []
        for party in list_of_party:
                ret.append(party.serialize())
            
        
        return ret