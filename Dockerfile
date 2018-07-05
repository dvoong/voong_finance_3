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
RUN apt-get install -y default-libmysqlclient-dev
RUN pip3 install mysqlclient==1.*
RUN pip3 install django-widget-tweaks
RUN pip3 install django-livereload-server

COPY . /home/www-data/voong_finance
WORKDIR /home/www-data/voong_finance
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py collectstatic
RUN chown -R www-data:www-data /home/www-data

EXPOSE 80

CMD ["python3", "manage.py", "runmodwsgi", "--user=www-data", "--group=www-data", "--port=80"]
