FROM python:3.10

RUN mkdir -p /home/app
COPY . /home/app

WORKDIR /home/app

RUN pip install -U pip
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]