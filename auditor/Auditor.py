# coding: utf-8
import zmq, time, sys, ast, socket
import random as roll

from Comandos import Commands
from Comandos import Message 
from Exploracao import Exploracao

'''
    Classe responsável pelo sistema auditor. serve de bind para os supervisores.
'''
class Auditor:

    '''
        self._publish_socket: socket resonsável por enviar mensagens broadcast
        self._router_socket: socket responsável por receber mensagens individuais de cada supervisor
    '''
    
    NUMEROSUPERVISORES = 0
    NUMEROROBOSPRONTOS = 0
    
    def __init__(self, port, bandeiras, supervisores):

        self.port = int(port)                                               # porta que socket estará ouvindo
        self.host = "auditor"                                               # nome que o container irá usar na rede
        self.exploracao = Exploracao(int(bandeiras),int(supervisores))      # gera uma objeto de Exploracao
        self.matrizExploracao = self.exploracao.gerarCampoDeExploracao()    # gera o mapa a ser explorado
        self.message = Message()                                            # Usa para formatar as mensagens a serem enviadas pelo socket
        self.commands = Commands()                                          # gerar um objeto "ENUM" para usar como comandos
        self.nSupervidores = int(supervisores)                              # Recebe quantidade de supervisores que auditor ficará esperando conectar
        self.placar = dict()                                                # Placar a ser exibido ao fim da exploracao
        self.confirmCheck = 0                                               # Checar a quantidade de supervisores com robo pronto
        self.bandeirasCapturadas = 0                                        # Salvar quantidade de bandeiras já capturadas
        self.bandeiras = []                                                 # Gera uma lista com as bandeiras capturadas para auxiliar
        self._context = zmq.Context()                                       

        self._publish_socket = self._context.socket(zmq.PUB)                # Gera contexto publish do ZMQ
        self._router_socket = self._context.socket(zmq.ROUTER)              # Gera contexto router do ZMQ
        self.bandeira = False

        # bind nos sockets para supervisor se conectar
        self._publish_socket.bind("tcp://" + socket.gethostbyname(self.host) + ":" + str(self.port))  # apenas para o broadcast
        self._router_socket.bind("tcp://"+ socket.gethostbyname(self.host) + ":" +str(self.port + 1))  # apenas para solicitacoes individuais

        # cadatra os sockets no poller
        self._poller = zmq.Poller()
        self._poller.register(self._router_socket, zmq.POLLIN)  # notifica cada mensagem recebida

        # imprime o ip do servidor
        print("O endereço do servidor PUB eh ", self.host + ":"+ str(self.port))
        print("O endereço do servidor ROUTER eh ", self.host + ":"+ str(self.port +1) + "\n")
        self.jogo_started = False        
        self.thread_run_flag = True        

    '''
        Responsável por iniciar a comunicação entre os sockets atráves do Poller
    '''   
    def start(self):
        i = 1
        while True:            
            ## verifica se algum socket receber alguma mensagem
            polled = dict(self._poller.poll())
            if self._router_socket in polled:
                id_, msg = self._router_socket.recv_multipart()
                self.bandeira = False
                #process_id, val = json.loads(msg)                
                msgDecode = ast.literal_eval(self.message.recvMessage(msg))   
                # Se receber READY do supervisor, implica que o container subiu. Assim que NUMEROSUPERVISORES for igual ao número de supervisores, envia o mapa para todos.    
                if(self.commands.READY in msgDecode):
                    self.NUMEROSUPERVISORES = self.NUMEROSUPERVISORES + 1
                    self.placar[self.NUMEROSUPERVISORES] = 0
                    self._router_socket.send_multipart([id_, str(self.NUMEROSUPERVISORES).encode("UTF-8")])  
                    self._publish_socket.send_json(self.message.sendMessage(self.commands.MAP,self.matrizExploracao))

                # CONFIRM igual ao número de supervisores implica que os robos já estão na posição inicial, prontos para iniciar, então auditor envia o comando START  
                elif((self.commands.CONFIRM in msgDecode)):
                    self.confirmCheck = self.confirmCheck + 1
                    if(self.confirmCheck == self.nSupervidores):
                        self._publish_socket.send_json(self.message.sendMessage(self.commands.START,"OK"))

                # UPDATE_FLAGS representa a captura de uma bandeira pelo robo. Auditor envia mensagem para todos informando a captura e quem capturou. 
                # Após capturar todas, envia o placar e printa no console o vencedor
                elif(self.commands.UPDATE_FLAGS in msgDecode):                                    
                    if((msgDecode[self.commands.UPDATE_FLAGS] not in self.bandeiras)):
                        self.bandeiras.append(msgDecode[self.commands.UPDATE_FLAGS])    
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
                                self._publish_socket.close()
                                self._router_socket.close()

            time.sleep(1)

if __name__ == "__main__":

    if (len(sys.argv) <= 3):
            print("Uso: python3 auditor.py port nbandeiras nsupervisores");
    else:    
        port = sys.argv[1]
        nbandeiras = sys.argv[2]
        nsupervisor = sys.argv[3]

        auditor = Auditor(port, nbandeiras, nsupervisor)
        auditor.start()

#docker rm -f $(docker ps -a -q)