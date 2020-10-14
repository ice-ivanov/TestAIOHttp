FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /testaiohttp
WORKDIR /testaiohttp
ADD requirements.txt /testaiohttp/
RUN pip install -r requirements.txt
ADD . /testaiohttp/
