FROM debian:latest

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3
RUN apt-get install -y apache2
RUN apt-get install -y apache2-dev
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install mod_wsgi==4.*
RUN pip3 install django==2.*
RUN pip3 install pandas==0.*
RUN pip3 install django-widget-tweaks
RUN pip3 install django-livereload-server
RUN pip3 install psycopg2-binary

ADD . /code/
WORKDIR /code

