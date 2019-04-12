<img src="images/logo.png" height=72>

# NDOP (National Data Opt-out)

The National Data Opt-out Service is a service that allows patients to opt out of their confidential patient information being used for research and planning, the website project consists of multiple repositories ([ndop-back-end](https://github.com/nhsconnect/ndop-back-end), [ndop-front-end](https://github.com/nhsconnect/ndop-front-end), [ndop-nojs](https://github.com/nhsconnect/ndop-nojs))

# NDOP Back End Code

This is the source code repository for the back end portion of the National Data Opt-out Service.

## Description
This repository contains a variety of backend lambda functions, including the following:

* state model lambdas:
  * `check-state-model` - Lambda used to check a specified state model in ElastiCache
  * `delete-state-model` - Lambda used to delete a specified state model from ElastiCache
  * `get-state-model` - Lambda used to get a specified state model from ElastiCache
  * `put-state-model` - Lambda used to set a specified state model in ElastiCache
  * The state model lambdas are being placed in the same VPC as ElastiCache to control the access to the ElastiCache, any other backend or frontend lambda that needs to read/write to the state model in the ElastiCache can do that through the state model lambdas.

## Building the code

To build the NDOP back end code locally

- clone the repository 
```
git clone https://github.com/nhsconnect/ndop-back-end.git
```

## Running the code

This repository contains the source code for the backend lambdas, and as such, can not be directly run in a local environment and will need to be deployed into AWS. 

To run the unit tests from the command line, run:

    make unit-test-python-lambdas

### Running coverage
To run coverage from the command line, run:

    make coverage-python-lambdas

### Running pylint
To run linting from the command line, run:

    make lint-python-lambdas
