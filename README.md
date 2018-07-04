## Installation

Create a conda environment

`conda create -n <environment name> python=3`

Activate the environment

`source activate <environment name>`

Install required python packages

`conda install --file requirements.txt`

### Other requirements
node.js

### Running the application locally
#### Running the test django server
`python manage.py runserver`

You might be asked to build a database for the application, follow the prompts to do so.
#### Running the application within a Docker container
1. Build the docker image, from within top level directory `docker build .`, you probably will want to tag the build e.g. `docker build -t voong_finance:latest .`
2. Run a container, you will need to link a local port to the container's exposed port (port 80), e.g. `docker run -p 8888:80`
3. Check it's working properly, in a web browser go to http://localhost:8888, or whichever port you chose to link the container to

## Testing

You will need to download the Chrome driver for Selenium, find this on the internet.

Use the following command to run all tests.

`env PATH=<path to driver>:$PATH python manage.py test`

## Deployment

TODO
