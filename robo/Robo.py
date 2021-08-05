import zmq, json, time, sys, socket
from Comandos import Commands
from Comandos import Message 
import zmq, random

'''
    Classe responsável pelo robô. Utilizada para capturar as bandeiras de acordo 
    com os comandos enviados pelo supervisor
'''
class Robo:

    '''
        self._pair_socket: Socket responsável por se conectar no supervisor para troca de mensagens
    '''

    coordRobo = []                              # Atualizar coordenada atual do robo                   
    BANDEIRA = 5                                # Usado para representar uma bandeira no mapa
    ABSCISSA = 0                                # Usado para ver a posição de x da coordenada
    ORDENADA = 1                                # Usado para ver a posição de y da coordenada
    flag = False                                # Informar se a bandeira foi capturada
    stop = False                                # Parar a movimentação do robo

    def __init__(self, port, host):
        self.port = int(port)

        # cria os sockets e gera o contexto PAIR com supervisor
        self._context = zmq.Context()
        self._pair_socket = self._context.socket(zmq.PAIR)
        self.message = Message()                # Gera objeto para formatar mensagens a serem enviadas pelo socket
        self.commands = Commands()              # Gera objeto para enviar comandos
        self.posInicial = []                    # Recebe posição inicial do robo
        self.host = host                        # Endereço onde o socket irá conectar
        self.posDestino = []                    # Informar o destino do robo, recebido pelo supervisor
        self.stop = False                       # Usado para parar movimentação do robo

        self._pair_socket.connect("tcp://" + socket.gethostbyname(self.host) + ":" + str(self.port))

        # cadatra os sockets no poller
        self._poller = zmq.Poller()
        self._poller.register(self._pair_socket, zmq.POLLIN)
        
    '''
        retorna o valor da abscissa da tupla recebida.
    '''
    def getAbscissa(self, coordenada):
        return coordenada[self.ABSCISSA]

    '''
        retornar o valor da ordenada da tupla recebida
    '''
    def getOrdenada(self, coordenada):
        return coordenada[self.ORDENADA]

    '''
        Utilizado para ficar atualizado ao supoervisor a posição atual do robo
    '''
    def sendPosToSupervisor(self, pos):
        self._pair_socket.send_json(self.message.sendMessage(self.commands.POS, pos))

    '''
        Utilizado para iniciar a movimentação do robo para as posições informadas pelo supervisor
    '''
    def startRobo(self,coordInicial, coordBandeira):
        self.stop = False
        auxX = self.getAbscissa(coordBandeira)      # Retorna valor de x da coordenada
        auxY = self.getOrdenada(coordBandeira)      # Retorna valor de y da coordenada
        self.coordRobo = coordInicial               # Passa posição inicial para o robo

        ## Anda primeiro no sentido de x até a posição destino e depois no sentido de y
        while(self.stop == False):
            while ((self.getAbscissa(self.coordRobo) < auxX ) or (self.getAbscissa(self.coordRobo) > auxX )):
                if((self.getAbscissa(self.coordRobo) < auxX)):
                    self.coordRobo = [self.getAbscissa(self.coordRobo)+1,self.getOrdenada(self.coordRobo)]
                    #print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))
                    self.sendPosToSupervisor(self.coordRobo)
                    self.posInicial = self.coordRobo
                    time.sleep(random.randint(1,5))
                elif((self.getAbscissa(self.coordRobo) > auxX)):
                    self.coordRobo = [self.getAbscissa(self.coordRobo)-1,self.getOrdenada(self.coordRobo)]
                    #print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))
                    self.sendPosToSupervisor(self.coordRobo)
                    self.posInicial = self.coordRobo
                    time.sleep(random.randint(1,5))
                if(self.stop == True):
                    return
            while ((self.getOrdenada(self.coordRobo) < auxY ) or (self.getOrdenada(self.coordRobo) > auxY )):
                if((self.getOrdenada(self.coordRobo) < auxY)):
                    self.coordRobo = [self.getAbscissa(self.coordRobo),self.getOrdenada(self.coordRobo)+1]
                    #print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))
                    self.sendPosToSupervisor(self.coordRobo)
                    self.posInicial = self.coordRobo
                    time.sleep(random.randint(1,5))
                elif((self.getOrdenada(self.coordRobo) > auxY)):
                    self.coordRobo = [self.getAbscissa(self.coordRobo),self.getOrdenada(self.coordRobo)-1]
                    self.posInicial = self.coordRobo
                    self.sendPosToSupervisor(self.coordRobo)
                    #print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))   
                    time.sleep(random.randint(1,5))
                if(self.stop == True):
                    return
            if(self.coordRobo==coordBandeira):
                self.flag = True
                self._pair_socket.send_json(self.message.sendMessage(self.commands.GET_FLAG,self.coordRobo))
                return   

    """ 
    def alterarDestinoRobo(self, coordBandeira):
        self.flag=False
        self.startRobo(self.coordRobo,coordBandeira) """

    '''
        Responsável por iniciar a comunicação entre os sockets atráves do Poller
    '''
    def start(self):

        self._pair_socket.send_json(self.message.sendMessage(self.commands.READY, "OK"))    
        while True:
            #print("Starting receiver loop ...")
            polled = dict(self._poller.poll())
            if self._pair_socket in polled:
                msg = self.message.recvMessage(self._pair_socket.recv_json())
                print(msg)
                # Recebe POS_INICIAL e seta na posInicial do robo
                if(self.commands.POS_INICIAL in msg):
                    self.posInicial = msg[self.commands.POS_INICIAL]
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.CONFIRM,"OK"))
                # Recebe coordenada que deverá ir
                elif(self.commands.MOVE_TO in msg):
                    self.posDestino = msg[self.commands.MOVE_TO]
                    self.startRobo(self.posInicial,self.posDestino)
                # Comando para parar a movimentação
                elif(self.commands.STOP in msg):
                    self.stop = True
                """   
                elif(self.commands.UPDATE_FLAGS in msg):                    
                    if(self.alterarDestinoRobo(msg[self.commands.UPDATE_FLAGS])==True):
                        self._pair_socket.send_string(self.commands.GET_FLAG) """
            time.sleep(1)

if __name__ == "__main__":

    if (len(sys.argv) <= 2):
            print("Uso: python3 supervisor.py port IP_Supervisor ");
    else:    
        port = sys.argv[1]
        host = sys.argv[2]

        robo = Robo(port, host)
        robo.start() 