* [Installation](#installation)
* [Running the development server](#1-running-the-test-django-server)
* [How to connect to the digitalocean droplet](#how-to-connect-to-the-digitalocean-droplet)
* [Interacting with the production database](#interacting-with-the-production-database)

## Installation

Create a conda environment

`conda create -n <environment name> python=3`

Activate the environment

`source activate <environment name>`

Install required python packages

`conda install --file requirements.txt`

Note: at the moment this file is stale, instead look in the Dockerfile to see which python packages are required and install them manually with conda/pip.

### Other requirements
node.js

### Running the application locally
There are are few ways to run the application,
1. Using the django development server
2. Using Apache's mod_wsgi module, https://modwsgi.readthedocs.io/en/develop/
3. Using a docker container running an Apache HTTP server and `mod_wsgi`

You primarily should be using approaches the development server and the Docker container. Running the application with the development server when developing and then running in it a Docker container to check how it will run in production. In rare cases you may want to use the local Apache and `mod_wsgi` method to more quickly debug issues resulting from Dockerising the application. You can find how to run the application via these methods explained below.

#### 1. Running the test django server
This is the simplest way to get the application running, first make sure you have activated the conda environment and use the following command.

`python manage.py runserver`

By default this will serve the application on port 8000, goto http://localhost:8000 to see it running. You can also specify the port with the command,

`python manage.py runserver <port_number>`

e.g.

`python manage.py runserver 8888`

Note: You might be asked to build a database for the application, the command for this is, 

`python manage.py syncdb`

there should be prompts to help you with creating the database.

#### 2. Running the application with Apache's HTTP server and `mod_wsgi` module
You will need to have Apache HTTP server installed, you can check this by using the command,

`which httpd`

in the terminal. You can install `mod_wsgi` using `pip` via the command,

`pip install mod_wsgi`

To check it is working use the command, 

`mod_wsgi-express start-server`

and then go to http://localhost:8000 in your web browser. To run the django application kill the previous command and then use the command,

`python manage.py collectstatic`

followed by

`python manage.py runmodwsgi --reload-on-changes`

which again you can check is working properly using your web browser. This method using the `mod_wsgi-express` approach together with django to automatically manage the staticfiles, https://pypi.org/project/mod_wsgi/


#### 3. Running the application within a Docker container
Using a docker container to run the application is one of the best ways to remove any dependence on your own local environment and hence gives a good representation of how the application will look when it is deployed into production. To run the application you will first need to build a Docker image, in the project directory use the following command,

`docker build -t voong_finance:latest .`

which will build the image based on the instructions found in the `Dockerfile` which you can find in the project directory. This will take a few minutes, subsequent rebuilds which run much faster however. Next to run the container use the command,

`docker run -p 8000:80 voong_finance`

The `-p` option is to allow you local machine to interact with the application in the Docker container, the port you use on your local machine is optional. Again to check this is working as intended, go to http://localhost:8000 in your web browser.


## Testing

You will need to download the Chrome driver for Selenium, http://chromedriver.chromium.org/downloads.

Use the following command to run all tests.

`env PATH=<path to driver>:$PATH python manage.py test`

## Deployment

## How to connect to the digitalocean droplet
1. Login to the web interface, https://cloud.digitalocean.com/login
2. Find the IP address
3. `ssh root@<ip address`

## Interacting with the production database
1. `ssh` into the digitalocean droplet
2. List the docker containers, `docker ps`
3. Connect to the container running the database, `docker exec -it <container id> /bin/bash`
4. `psql -U postgres` to open the postgres shell
5. `\dt` to list the tables
6. `\q` to quit the shell
