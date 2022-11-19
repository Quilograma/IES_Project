FROM python:3.9

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN sed -i -e 's/\r$//' run.sh

CMD ["bash", "-c", "./run.sh"]

