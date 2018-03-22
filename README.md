## Installation

Create a conda environment

`conda create -n <environment name> python=3`

Activate the environment

`source activate <environment name>`

Install required python packages

`conda install --file requirements.txt`

### Running the application locally

`python manage.py runserver`

You might be asked to build a database for the application, follow the prompts to do so.

## Testing

You will need to download the Chrome driver for Selenium, find this on the internet.

Use the following command to run all tests.

`env PATH=<path to driver>:$PATH python manage.py test`

## Deployment

TODO
