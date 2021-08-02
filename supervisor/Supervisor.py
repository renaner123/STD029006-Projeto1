# coding: utf-8
import json
import zmq, time, ast, sys, socket
from Comandos import Commands
from Comandos import Message 
from Exploracao import Exploracao

class Supervisor:

    
    def __init__(self, port):
        self.port = int(port)
        # cria os sockets
        self._context = zmq.Context()
        self._subscribe_socket = self._context.socket(zmq.SUB)
        self._dealer_socket = self._context.socket(zmq.DEALER)
        self._pair_socket = self._context.socket(zmq.PAIR)
        self.message = Message()
        self.commands = Commands()
        self.hostAuditor = "auditor"
        self.host = "supervisor"
        self.mapaExploracao = []
        self.posBandeiras = []
        self.meuId = 0
        self.bandeirasCapturadas = 0
        self.idOK = False

        self._subscribe_socket.setsockopt_string(zmq.IDENTITY, 'A')
        self._subscribe_socket.connect("tcp://" + socket.gethostbyname(self.hostAuditor) + ":" + str(self.port))  # apenas para o broadcast
        self._dealer_socket.connect("tcp://" + socket.gethostbyname(self.hostAuditor) + ":" + str(self.port + 1))  # apenas para solicitacoes individuais
        self._pair_socket.bind("tcp://" + socket.gethostbyname(self.host) + ":" + str(self.port + 2))

        # poller
        self._poller = zmq.Poller()
        self._poller.register(self._subscribe_socket, zmq.POLLIN)  # notifica cada mensagem recebida
        self._poller.register(self._dealer_socket, zmq.POLLIN)
        self._poller.register(self._pair_socket, zmq.POLLIN)

        # imprime o ip do servidor para facilitar a vida
        self.jogo_started = False        
        self.thread_run_flag = True

    def findPosicao(self,valorProcurado, matriz):
        posicoes = []
        for i in range(0,len(matriz)):
            for y in range(0,len(matriz)):
                if(matriz[i][y]==valorProcurado):
                    posicoes.append((i,y))
       
        return posicoes

    def start(self):
        self._subscribe_socket.subscribe("")
        #self._dealer_socket.send_json(self.message.sendMessage(self.commands.READY,"ok"))   
        i = 0 
        while True:
            #print("Starting receiver loop ...")
            polled = dict(self._poller.poll())
            if self._subscribe_socket in polled:
                msg = self.message.recvMessage(self._subscribe_socket.recv_json())
                print("Mensagem do servidor: " , msg)
                if(self.commands.MAP in msg):
                    self.mapaExploracao = msg[self.commands.MAP]
                    self.posBandeiras = self.findPosicao(Exploracao.BANDEIRA,self.mapaExploracao)
                elif(self.commands.START in msg):
                    time.sleep(2)
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.MOVE_TO,min(self.posBandeiras)))  
                elif(self.commands.UPDATE_FLAGS in msg):
                    self.bandeirasCapturadas = self.bandeirasCapturadas +1
                    posExcluir = msg[self.commands.UPDATE_FLAGS]
                    del (self.posBandeiras[self.posBandeiras.index(tuple(posExcluir))])
                    if(len(self.posBandeiras)>=1):
                        self._pair_socket.send_json(self.message.sendMessage(self.commands.MOVE_TO,min(self.posBandeiras)))    
                elif(self.commands.WIN in msg):
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.STOP,"stop"))
            
            elif self._pair_socket in polled:
                msg = self._pair_socket.recv_json()
                print("Mensagem do Robo: ",msg)
                if(self.commands.READY in msg):
                    self._dealer_socket.send_json(self.message.sendMessage(self.commands.READY,"ok"))
                elif(self.commands.CONFIRM in msg):
                    self._dealer_socket.send_json(self.message.sendMessage(self.commands.CONFIRM,"ok"))
                elif(self.commands.GET_FLAG in msg):
                    posDict = ast.literal_eval(self.message.sendMessage(self.commands.UPDATE_FLAGS,min(self.posBandeiras)))
                    posDict[self.commands.ID] = self.meuId
                    self._dealer_socket.send_json(self.message.toJson(posDict))

            elif self._dealer_socket in polled:
                msg = self._dealer_socket.recv() # Para pegar o número o supervisor terá... 1, 2 ...
                self.meuId = int(msg.decode())  
                print(self.meuId)    
                dict_pos = self.message.sendMessage(self.commands.POS_INICIAL,min(self.findPosicao(self.meuId,self.mapaExploracao)))
                self._pair_socket.send_json(dict_pos)
            time.sleep(1)

            i = i +1
if __name__ == "__main__":

    if (len(sys.argv) <= 1):
            print("Uso: python3 supervisor.py port ");
    else:    
        port = sys.argv[1]

        supervisor = Supervisor(port)
        supervisor.start()


