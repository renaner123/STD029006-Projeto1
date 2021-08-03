FROM python:3

WORKDIR /app 

COPY requirements.txt ./
COPY Robo.py ./
COPY Comandos.py ./
COPY Exploracao.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50012
EXPOSE 50011

#CMD [ "python", "./Robo.py" , "50011" ]

