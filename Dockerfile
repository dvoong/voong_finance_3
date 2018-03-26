FROM debian:latest

RUN apt-get update && apt-get upgrade
RUN apt-get install -y python3
RUN apt-get install -y apache2
RUN apt-get install -y apache2-dev
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install mod_wsgi==4.*
RUN pip3 install django==2.*
RUN pip3 install pandas==0.*

COPY . /home/www-data/voong_finance
WORKDIR /home/www-data/voong_finance
RUN chown -R www-data:www-data /home/www-data
EXPOSE 80

CMD ["python3", "manage.py", "runmodwsgi", "--user=www-data", "--group=www-data", "--port=80"]

# RUN python3 manage.py collectstatic

# RUN apt-get install -y wget bzip2 ca-certificates curl git && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*
# RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.4.10-Linux-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda && \
#     rm ~/miniconda.sh && \
#     /opt/conda/bin/conda clean -tipsy && \
#     ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
#     echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
#     echo "conda activate base" >> ~/.bashrc

# ENV TINI_VERSION v0.16.1
# ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
# RUN chmod +x /usr/bin/tini

# # https://hub.docker.com/r/continuumio/miniconda3/~/dockerfile/
# ENV PATH /opt/conda/bin:$PATH

# RUN conda update -n base conda

# RUN conda create -n voong_finance python=3
# RUN [ "/bin/bash", "-c", "source activate voong_finance" ]
# RUN pip install django=2.*
# RUN pip install pandas=0.*
# RUN apt-get install -y apt-utils
# RUN apt-get install -y libapache2-mod-wsgi-py3

# COPY . /root/voong_finance
# COPY apache2.conf /etc/apache2/apache2.conf
# COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

# EXPOSE 80
# CMD ["apache2ctl", "-D", "FOREGROUND"]