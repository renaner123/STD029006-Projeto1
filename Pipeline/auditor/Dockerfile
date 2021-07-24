FROM python:3

WORKDIR /app

COPY requirements.txt ./
COPY distribuidor.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50011
EXPOSE 50012

CMD [ "python", "distribuidor.py" ]

