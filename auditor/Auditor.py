# coding: utf-8
import zmq, time, sys, ast, socket
import random as roll

from Comandos import Commands
from Comandos import Message 
from Exploracao import Exploracao

class Auditor:
    
    NUMEROSUPERVISORES = 0
    NUMEROROBOSPRONTOS = 0
    
    def __init__(self, port, supervisores):
        self.port = int(port)
        self.host = "auditor"
        self.exploracao = Exploracao(3,3)
        self.matrizExploracao = self.exploracao.gerarCampoDeExploracao()
        self.message = Message()
        self.commands = Commands()
        self.nSupervidores = int(supervisores)
        self.placar = dict()
        self.bandeirasCapturadas = 0
        # cria os sockets
        self._context = zmq.Context()
        self._publish_socket = self._context.socket(zmq.PUB)
        self._router_socket = self._context.socket(zmq.ROUTER)

        # bind nos sockets
        self._publish_socket.bind("tcp://" + socket.gethostbyname(self.host) + ":" + str(self.port))  # apenas para o broadcast
        self._router_socket.bind("tcp://"+ socket.gethostbyname(self.host) + ":" +str(self.port + 1))  # apenas para solicitacoes individuais

        # poller
        self._poller = zmq.Poller()
        self._poller.register(self._router_socket, zmq.POLLIN)  # notifica cada mensagem recebida

        # imprime o ip do servidor para facilitar a vida
        print("O endereço do servidor PUB eh ", self.host + ":"+ str(self.port))
        print("O endereço do servidor ROUTER eh ", self.host + ":"+ str(self.port +1) + "\n")
        self.jogo_started = False        
        self.thread_run_flag = True        

    
    def start(self):
        i = 1
        while True:            
            polled = dict(self._poller.poll())
            if self._router_socket in polled:
                id_, msg = self._router_socket.recv_multipart()
                #process_id, val = json.loads(msg)                
                msgDecode = ast.literal_eval(self.message.recvMessage(msg))   
                print(msgDecode)      
                if(self.commands.READY in msgDecode):
                    self.NUMEROSUPERVISORES = self.NUMEROSUPERVISORES + 1
                    self.placar[self.NUMEROSUPERVISORES] = 0
                    self._router_socket.send_multipart([id_, str(self.NUMEROSUPERVISORES).encode("UTF-8")])  
                    self._publish_socket.send_json(self.message.sendMessage(self.commands.MAP,self.matrizExploracao))  
                elif((self.commands.CONFIRM in msgDecode)):
                    if(self.NUMEROSUPERVISORES == self.nSupervidores):
                        self._publish_socket.send_json(self.message.sendMessage(self.commands.START,"OK"))
                elif(self.commands.UPDATE_FLAGS in msgDecode):
                    if(self.bandeirasCapturadas<self.exploracao.nBandeiras):
                        self.bandeirasCapturadas = self.bandeirasCapturadas + 1
                        self.placar[msgDecode[self.commands.ID]] = self.placar[msgDecode[self.commands.ID]] +1
                        if(self.bandeirasCapturadas < self.exploracao.nBandeiras):
                            posDict = ast.literal_eval(self.message.sendMessage(self.commands.UPDATE_FLAGS,msgDecode[self.commands.UPDATE_FLAGS]))
                            posDict['robo'] = msgDecode[self.commands.ID]
                            self._publish_socket.send_json(self.message.toJson(posDict)) 
                        elif(self.bandeirasCapturadas == self.exploracao.nBandeiras):
                            self._publish_socket.send_json(self.message.sendMessage(self.commands.WIN,self.placar))
                            print("Vendecor é o Supervisor ",max(self.placar, key=self.placar.get)," que capturou ", self.placar[max(self.placar, key=self.placar.get)], " bandeiras")
                    

            time.sleep(1)

if __name__ == "__main__":

    if (len(sys.argv) <= 2):
            print("Uso: python3 auditor.py port nsupervisores");
    else:    
        port = sys.argv[1]
        nsupervisor = sys.argv[2]

        auditor = Auditor(port, nsupervisor)
        auditor.start()
