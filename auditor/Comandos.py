import json

class Commands:

    MOVE_TO = "move_to"
    START = "start"
    STOP = "stop"
    POS_INICIAL = "pos_inicial"
    UPDATE_FLAGS = "update"
    READY = "ready"
    POS = "pos"
    CONFIRM = "confirm"
    MAP = "map"
    GET_FLAG = "get_fag"
    ID = "id"
    WIN = "win"
    
class Message:

    command = ""
    value = ""

    def __init__(self):
        pass

    def toJson(self,valueToJson):
        return json.dumps(valueToJson)

    def jsonTO(self,valueJson):
        return json.loads(valueJson)

    def toDict(self,comando, valor):
        return ({comando: valor})
    
    def sendMessage(self,comando, valor):
        return self.toJson(self.toDict(comando,valor))        

    def recvMessage(self, message):
        return self.jsonTO(message)
