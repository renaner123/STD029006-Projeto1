# coding: utf-8
import json
import zmq, time, ast, sys, socket
from Comandos import Commands
from Comandos import Message 
from Exploracao import Exploracao

'''
    Classe responsável pelo sistema supervisor. Recebe comando do auditor e envia novos comandos para o robo
'''
class Supervisor:

    '''
        self._subscribe_socket: responsável por se "inscrever" no socker publish do auditor
        self._dealer_socket: responsável por enviar mensagens para socket router do servidor
        self._pair_socket: responsável pela troca de mensagens do pair do robo
    '''
    def __init__(self, port, hostSupervisor, portSupervisor):
        self.port = int(port)
        self.portSupervisor = int(portSupervisor)
        # cria os sockets
        self._context = zmq.Context()        
        self._subscribe_socket = self._context.socket(zmq.SUB)          # Gera o contexto subscribe para conectar no publish do auditor e receber mensagens broadcast
        self._dealer_socket = self._context.socket(zmq.DEALER)          # Gera o contexto DEALER para enviar mensagens para o auditor
        self._pair_socket = self._context.socket(zmq.PAIR)              # Gera contexto PAIR para ter socket bidirecional com o robo
        self.message = Message()                                        # Usa para formatar as mensagens a serem enviadas pelo socket
        self.commands = Commands()                                      # gera um objeto "ENUM" para usar como comandos
        self.hostAuditor = "auditor"                                    # Nome da rede do auditor
        self.host = hostSupervisor                                      # Nome que o supervisor irá usar como host
        self.mapaExploracao = []                                        # Recebe mapa de exploração
        self.posBandeiras = []                                          # Armazena as posições de bandeira a serem capturadas
        self.posInicialRobo = []                                        # Armazena posiçõa inical do robo
        self.posRobo = []                                               # Auxiliar para atualizar posição atual do robo
        self.meuId = 0                                                  # Recebe ID fornecido pelo auditor
        self.bandeirasCapturadas = 0                                    
        self.idOK = False

        self._subscribe_socket.setsockopt_string(zmq.IDENTITY, 'A')
        self._subscribe_socket.connect("tcp://" + socket.gethostbyname(self.hostAuditor) + ":" + str(self.port))  # apenas para o broadcast
        self._dealer_socket.connect("tcp://" + socket.gethostbyname(self.hostAuditor) + ":" + str(self.port + 1))  # apenas para solicitacoes individuais
        self._pair_socket.bind("tcp://" + socket.gethostbyname(self.host) + ":" + str(self.portSupervisor))

        # cadatra os sockets no poller
        self._poller = zmq.Poller()
        self._poller.register(self._subscribe_socket, zmq.POLLIN)  # notifica cada mensagem recebida
        self._poller.register(self._dealer_socket, zmq.POLLIN)
        self._poller.register(self._pair_socket, zmq.POLLIN)

        self.jogo_started = False        
        self.thread_run_flag = True

    '''
        Retorna a posição de uma tupla da matriz
    '''
    def findPosicao(self,valorProcurado, matriz):
        posicoes = []
        for i in range(0,len(matriz)):
            for y in range(0,len(matriz)):
                if(matriz[i][y]==valorProcurado):
                    posicoes.append((i,y))
       
        return posicoes
    
    '''
        Retorna posição mais próxima da coordenada destino
    '''
    def findPosicaoMaisProxima(self,valorProcurado, matriz):
        auxPos = []
        auxValor = list(valorProcurado)

        auxCont = sum(max(matriz)) + sum(auxValor)

        for i in matriz:
            aux = (abs((i[0]+i[1]) - sum(auxValor)))
            if(aux < auxCont):
                auxCont = aux
                auxPos = i

        return tuple(auxPos)
    '''
        Responsável por iniciar a comunicação entre os sockets atráves do Poller
    '''
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

                # MAP recebe mapa a ser explorado e armazena as posições de bandeira no posBandeiras
                if(self.commands.MAP in msg):
                    self.mapaExploracao = msg[self.commands.MAP]
                    self.posBandeiras = self.findPosicao(Exploracao.BANDEIRA,self.mapaExploracao)

                # START informa que os robos podem começar a explorar o mapa. Supervisor envia a posição de destino e remove da lista posBandeiras
                elif(self.commands.START in msg):
                    time.sleep(2)
                    print(self.posBandeiras)
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.MOVE_TO,self.findPosicaoMaisProxima(tuple(self.posInicialRobo),self.posBandeiras))) 
                    posExcluir = min(self.posBandeiras)
                    del (self.posBandeiras[self.posBandeiras.index(tuple(posExcluir))])    

                # UPDATE_FLAGS recebe bandeira que já foi capturada e envia nova coordenada para o robo                
                elif(self.commands.UPDATE_FLAGS in msg):
                    self.bandeirasCapturadas = self.bandeirasCapturadas +1
                    if(msg['robo']!=self.meuId):
                        self._pair_socket.send_json(self.message.sendMessage(self.commands.STOP,self.commands.STOP))
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.MOVE_TO,min(self.posBandeiras))) 
                
                # WIN informa que a partida encerrou e contem o placar
                elif(self.commands.WIN in msg):
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.STOP,"stop"))
                    self._pair_socket.close()
                    self._subscribe_socket.close()
                    self._dealer_socket.close()   
     
            elif self._pair_socket in polled:
                msg = self._pair_socket.recv_json()
                print("Mensagem do Robo: ",msg)
                # READY informa que o robo subiu e está conectado. Notifica o auditor
                if(self.commands.READY in msg):
                    self._dealer_socket.send_json(self.message.sendMessage(self.commands.READY,"ok"))
                
                # CONFIRM informa que o robo já está na posição inicial e pronto para explorar e notifica o auditor
                elif(self.commands.CONFIRM in msg):
                    self._dealer_socket.send_json(self.message.sendMessage(self.commands.CONFIRM,"ok"))
                
                # GET_FLAG informa que o robo capturou uma bandeira. Envia a informação para o auditor
                elif(self.commands.GET_FLAG in msg):                
                    auxDic = ast.literal_eval(msg)
                    posDict = ast.literal_eval(self.message.sendMessage(self.commands.UPDATE_FLAGS,auxDic[self.commands.GET_FLAG]))
                    posDict[self.commands.ID] = self.meuId
                    self._dealer_socket.send_json(self.message.toJson(posDict))
                    posExcluir = tuple(auxDic[self.commands.GET_FLAG])
                    if(posExcluir in self.posBandeiras):
                        del (self.posBandeiras[self.posBandeiras.index((posExcluir))])

                # Atualiza posição atual do robo  
                elif(self.commands.POS in msg):
                    auxDic = ast.literal_eval(msg)
                    self.posRobo = tuple(auxDic[self.commands.POS])

            elif self._dealer_socket in polled:
                # Para pegar a ID que o auditor forneceu para o supervisor
                msg = self._dealer_socket.recv() 
                self.meuId = int(msg.decode())  
                print("Recebeu o ID ",self.meuId)
                self.posInicialRobo = min(self.findPosicao(self.meuId,self.mapaExploracao))
                dict_pos = self.message.sendMessage(self.commands.POS_INICIAL,self.posInicialRobo)
                self._pair_socket.send_json(dict_pos)
            time.sleep(1)

            i = i +1
if __name__ == "__main__":

    if (len(sys.argv) <= 3):
            print("Uso: python3 supervisor.py portAuditor IP_Supervisor port_Supervidor");
    else:    
        portAuditor = sys.argv[1]
        host = sys.argv[2]
        portSupervisor = sys.argv[3]

        supervisor = Supervisor(portAuditor, host, portSupervisor)
        supervisor.start()


