## Captura de bandeiras com robôs autônomos

<!--ts-->
   * [Descrição](#Descrição)  
   * [Criando as imagens com o Docker](#Criando-as-imagens-com-o-Docker)
   * [Executando a aplicação com Docker run](#Executando-a-aplicação-usando-o-Docker-run)
   * [Criando as imagens com o Docker-Compose e executando](#Criando-as-imagens-com-o-Docker-Compose)
   * [Arquivo docker-compose](#Docker-compose)

<!--te-->

### Descrição 

### Criando as imagens com o Docker

Para construir as imagens do auditor, supervisor e do robo respectivamente, estando na pasta raiz, é necessário os seguintes comandos.

```docker
    docker build -t std/auditor auditor/
    docker build -t std/supervisor supervisor/
    docker build -t std/robo robo/
```

### Executando a aplicação usando o Docker run

Nesse exemplo, foi criado uma rede chamada rede-std com driver bridge.

```docker
docker network create --driver bridge rede-std
```

Necessáro iniciar primeiro o Container do auditor, informando a porta e a quantidade de supervisores que o auditor terá. Isso é passado no arquivo do Dockerfile na pasta auditor na camada CMD.

```docker
docker run -it --rm --name auditor --network rede-std std/auditor
```
Após subir o auditor, pode subir o supervisor e robo. Caso precise alterar a porta, estão nos Dockerfile das respectivas pastas

```docker
docker run -it --rm --name supervisor --network rede-std std/supervisor
```
```docker
docker run -it --rm --name robo --network rede-std std/robo
```
### Criando as imagens com o Docker-compose

Para compilar os containeres usando o compose basta estar na pasta raiz 

```docker
docker-compose build
```

Usando o compose é necessário subir inicialmente o auditor com:

```docker
docker-compose up auditor
```

Após pode subir o resto com:

```docker
docker-compose up
```

Nesse caso, o resto consiste em dois supervisores(supervisor e supervisor2) e dois robos(robo e robo2). 

### Docker compose

No arquivo docker-compose.yml estão sendo instanciados os serviços dos containers do auditor, supervisor e do robo. No auditor, deve-se informar a porta em que o container ficará ouvindo os sockets do supervisor e o número de supervisores que serão conectados, conforme exemplo abaixo:

```docker
   command: python Auditor.py 50011 2
```

No supervisor, é necessário informar a porta de escuta do auditor, o nome que a rede do supervisor terá e a porta que utilizará para fazer o bind com seu robo, conforme exemplo abaixo:

```docker
  command: python Supervisor.py 50011 supervisor 50015
```
O supervisor permite ter mais de um, então para criar um novo supervisor é só criar outro serviço com o nome desejado e a porta de bind para o robo, conforme consta no arquivo docker-compose.yml

O serviço robo, assim como o supervisor, permite criar mais de um. No caso, cada supervisor terá o seu robo, portando pode usar como argumentos o nome do supervidor e a porta que ele estará ouvindo, conforme abaixo:

```docker
   command: python Robo.py 50015 supervisor
```
### Demonstração do projeto em execução

Terá um gif
