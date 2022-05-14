FROM ubuntu:20.04

WORKDIR /fin_assist_bot

RUN apt-get update && apt-get install --yes --no-install-recommends python3-pip

COPY requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS=key.json

COPY . .

CMD [ "python3", "-m" , "main.py"]
