FROM python:3

WORKDIR /app 

COPY requirements.txt ./
COPY coletor.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50012

CMD [ "python", "./coletor.py" ]

