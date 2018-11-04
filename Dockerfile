FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN apt-get update && \
	apt-get install -y \
		pandoc && \
        rm -rf /var/lib/apt/lists/*
