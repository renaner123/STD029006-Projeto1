import numpy as np
import random as roll

class Exploracao:
                  
    BANDEIRA = 5
    ABSCISSA = 0
    ORDENADA = 1
    flag = False
    tamanhoMatriz = 7
    listPosBandeira = []
    listPosRobos = []
    coordRobo = []
    matriz = np.zeros((tamanhoMatriz,tamanhoMatriz))
    nBandeiras = 3
    nRobos = 3

    def __init__(self, bandeiras, robos):     
        self.nBandeiras = bandeiras
        self.nRobos = robos

    def posBandeiras(self):
    
        i = 0
        while(i<self.nBandeiras):
            posBandeira = (roll.randrange(1, self.tamanhoMatriz-1),roll.randrange(1, self.tamanhoMatriz-1))
            if((posBandeira in self.listPosBandeira)or(posBandeira in self.listPosRobos)):
                i = i - 1
            else:
                 self.listPosBandeira.append(posBandeira)  
            i = i +1
        return self.listPosBandeira
        
    def posRobos(self):

        i = 0
        while(i<self.nRobos):
            posRobo = (roll.randrange(1, self.tamanhoMatriz-1),roll.randrange(1, self.tamanhoMatriz-1))
            if((posRobo in self.listPosRobos)or(posRobo in self.listPosBandeira)):
                i = i -1
            else:
                self.listPosRobos.append(posRobo)   
            i = i+1

        return self.listPosRobos 

    def inserirBandeirasMatriz(self, coordBandeira):
        
        self.matriz[coordBandeira[0]][coordBandeira[1]] = self.BANDEIRA
        return True

    def inserirRobosMatriz(self, coordRobo, nRobo):
        self.matriz[coordRobo[0]][coordRobo[1]] = nRobo
        return True

    def gerarCampoDeExploracao(self):


        robo = self.posRobos()
        bandeira = self.posBandeiras()

        for i in range(0,self.nBandeiras):
            self.inserirBandeirasMatriz(bandeira[i])
            self.inserirRobosMatriz(robo[i],i+1)
            continue
        return self.matriz
    
    def getAbscissa(self, coordenada):
        return coordenada[self.ABSCISSA]
    def getOrdenada(self, coordenada):
        return coordenada[self.ORDENADA]

    def startRobo(self,coordInicial, coordBandeira):
        self.flag = False
        auxX = self.getAbscissa(coordBandeira)        
        auxY = self.getOrdenada(coordBandeira)
        self.coordRobo = coordInicial

        while ((self.getAbscissa(self.coordRobo) < auxX ) or (self.getAbscissa(self.coordRobo) > auxX )):

                if((self.getAbscissa(self.coordRobo) < auxX)):
                    self.coordRobo = [self.getAbscissa(self.coordRobo)+1,self.getOrdenada(self.coordRobo)]
                    print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))
                if((self.getAbscissa(self.coordRobo) > auxX)):
                    self.coordRobo = [self.getAbscissa(self.coordRobo)-1,self.getOrdenada(self.coordRobo)]
                    print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))

        while ((self.getOrdenada(self.coordRobo) < auxY ) or (self.getOrdenada(self.coordRobo) > auxY )):

            if((self.getOrdenada(self.coordRobo) < auxY)):
                self.coordRobo = [self.getAbscissa(self.coordRobo),self.getOrdenada(self.coordRobo)+1]
                print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))
            if((self.getOrdenada(self.coordRobo) > auxY)):
                self.coordRobo = [self.getAbscissa(self.coordRobo),self.getOrdenada(self.coordRobo)-1]
                print("Andou para: " + str(self.getAbscissa(self.coordRobo)) + "," + str(self.getOrdenada(self.coordRobo)))   

        if(self.coordRobo==coordBandeira):
            self.flag = True

    def alterarDestinoRobo(self, coordBandeira):
        self.startRobo(self.coordRobo,coordBandeira)
        return True

teste = Exploracao(3,3)

teste.gerarCampoDeExploracao()

posBandeira = (1,1)
posRobo = (5,5)
print("Posicição inicial do robo:" + str(posRobo) + " -- Posição inicial da Bandeira: " + str(posBandeira))
teste.startRobo(posRobo, posBandeira)

posBandeiraNova = (3,4)
print("Nova bandeira posicionada em: ", str(posBandeiraNova))
print(teste.alterarDestinoRobo(posBandeiraNova))









