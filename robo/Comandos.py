import json

'''
    Classe utilizada como enum para troca de mensagens entre os sitemas. No caso, comandos utilizados. 
'''
class Commands:

    MOVE_TO = "move_to"           # Utilizada pra indicar a nova movimentação do robo
    START = "start"               # Utilizada para dar inicio a caça as bandeiras
    STOP = "stop"                 # Utilizada para parar o supervisor e Robo quando todas as bandeiras forem capturadas
    POS_INICIAL = "pos_inicial"   # Define a posição inicial do Robo
    UPDATE_FLAGS = "update"       # Utilizada sempre que uma bandeira é capturada por algum robo
    READY = "ready"               # Supervisor envia assim que estiver conectado
    POS = "pos"                   # Usada para robo informar o supervisor a sua posição atual
    CONFIRM = "confirm"           # Assim que o robo estiver pronto, supervisor confirma para o auditor
    MAP = "map"                   # Utilizada para enviar o mapa a ser explorado
    GET_FLAG = "get_fag"          # Utilzada pelo robo ao capturar uma bandeira
    ID = "id"                     # Informa que a mensagem possui ID do supervisor
    WIN = "win"                   # Informa que o jogo chegou ao fim
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
