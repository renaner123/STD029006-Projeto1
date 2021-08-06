import zmq, json, time, socket
import random as roll

'''
    Classe utilizada para criação do mapa a ser explorado
'''
class Exploracao:
                  
    BANDEIRA = 5
    ABSCISSA = 0
    ORDENADA = 1
    flag = False
    tamanhoMatriz = 12
    listPosBandeira = []
    listPosRobos = []
    coordRobo = []
    matriz = []
    nBandeiras = 2
    nRobos = 2

    def __init__(self, bandeiras, robos):     
        self.nBandeiras = int(bandeiras)
        self.nRobos = int(robos)
        self.crie_matriz()

    '''
        Gera uma matriz nxn
    '''
    def crie_matriz(self,n_linhas=tamanhoMatriz, n_colunas=tamanhoMatriz, valor=0):
    
        for i in range(n_linhas):
            # cria a linha i
            linha = [] # lista vazia
            for j in range(n_colunas):
                linha += [valor]
            # coloque linha na matriz
            self.matriz += [linha] 
        return self.matriz

    '''
        gera posição randomica das bandeiras
    '''
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
        
    '''
        gera posição randomica dos robos
    '''
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

    '''
        insere as bandeiras na matriz
    '''
    def inserirBandeirasMatriz(self, coordBandeira):
        
        self.matriz[coordBandeira[0]][coordBandeira[1]] = self.BANDEIRA
        return True

    '''
        insere os robos na matriz
    '''
    def inserirRobosMatriz(self, coordRobo, nRobo):
        self.matriz[coordRobo[0]][coordRobo[1]] = nRobo
        return True

    '''
        retorna o mapa a ser explorado
    '''
    def gerarCampoDeExploracao(self):

        robo = self.posRobos()
        bandeira = self.posBandeiras()

        for i in range(0,self.nBandeiras):
            self.inserirBandeirasMatriz(bandeira[i])

        for i in range(0,self.nRobos):
            self.inserirRobosMatriz(robo[i],i+1)

        return self.matriz
    
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
    
    def findPosicao(self,valorProcurado, matriz):
        posicoes = []
        for i in range(0,len(matriz)):
            for y in range(0,len(matriz)):
                if(matriz[i][y]==valorProcurado):
                    posicoes.append((i,y))
       
        return posicoes