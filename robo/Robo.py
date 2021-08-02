import zmq, json, time, sys, socket
from Comandos import Commands
from Comandos import Message 
import zmq, random

class Robo:

    coordRobo = []                
    BANDEIRA = 5
    ABSCISSA = 0
    ORDENADA = 1
    flag = False
    stop = False

    def __init__(self, port):
        self.port = int(port)

        # cria os sockets
        self._context = zmq.Context()
        self._pair_socket = self._context.socket(zmq.PAIR)
        self.message = Message()
        self.commands = Commands()
        self.posInicial = []
        self.host = "supervisor"
        self.posDestino = []
        self.stop = False

        self._pair_socket.connect("tcp://" + socket.gethostbyname(self.host) + ":" + str(self.port + 2))

        # poller
        self._poller = zmq.Poller()
        self._poller.register(self._pair_socket, zmq.POLLIN)
        

    def getAbscissa(self, coordenada):
        return coordenada[self.ABSCISSA]

    def getOrdenada(self, coordenada):
        return coordenada[self.ORDENADA]
    
    def sendPosToSupervisor(self, pos):
        self._pair_socket.send_json(self.message.sendMessage(self.commands.POS, pos))

    def startRobo(self,coordInicial, coordBandeira):
        auxX = self.getAbscissa(coordBandeira)        
        auxY = self.getOrdenada(coordBandeira)
        self.coordRobo = coordInicial

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
            elif(self.stop==True):
                self.stop = False
                break
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
            elif(self.stop==True):
                self.stop = False
                break

        if(self.coordRobo==coordBandeira):
            self.flag = True
            self._pair_socket.send_json(self.message.sendMessage(self.commands.GET_FLAG,self.coordRobo))
            

    """ 
    def alterarDestinoRobo(self, coordBandeira):
        self.flag=False
        self.startRobo(self.coordRobo,coordBandeira) """

    def start(self):

        self._pair_socket.send_json(self.message.sendMessage(self.commands.READY, "OK"))    
        while True:
            #print("Starting receiver loop ...")
            polled = dict(self._poller.poll())
            if self._pair_socket in polled:
                msg = self.message.recvMessage(self._pair_socket.recv_json())
                print(msg)
                if(self.commands.POS_INICIAL in msg):
                    self.posInicial = msg[self.commands.POS_INICIAL]
                    self._pair_socket.send_json(self.message.sendMessage(self.commands.CONFIRM,"OK"))
                elif(self.commands.MOVE_TO in msg):
                    self.stop = True
                    self.posDestino = msg[self.commands.MOVE_TO]
                    self.startRobo(self.posInicial,self.posDestino)
                elif(self.commands.STOP in msg):
                    self.stop = True
                """   
                elif(self.commands.UPDATE_FLAGS in msg):                    
                    if(self.alterarDestinoRobo(msg[self.commands.UPDATE_FLAGS])==True):
                        self._pair_socket.send_string(self.commands.GET_FLAG) """
            time.sleep(1)

if __name__ == "__main__":
    robo = Robo(50011)

    robo.start()
    if (len(sys.argv) <= 1):
            print("Uso: python3 supervisor.py port ");
    else:    
        port = sys.argv[1]

        robo = Robo(port)
        robo.start() 