FROM python:3

WORKDIR /app


COPY requirements.txt ./
COPY Auditor.py ./ 
COPY Comandos.py ./
COPY Exploracao.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50011
EXPOSE 50012

CMD [ "python", "Auditor.py", "50011", "1"]

