<img src="images/logo.png" height=72>

# NDOP Back End Code

This is the source code repository for the back end portion of the National Data Opt-out Service.

## Description
This repository contains a variety of backend lambda functions, including the following:

* state_model:
  * `check-state-model` - Lambda used to check a specified state model in ElastiCache
  * `delete-state-model` - Lambda used to delete a specified state model from ElastiCache
  * `get-state-model` - Lambda used to get a specified state model from ElastiCache
  * `put-state-model` - Lambda used to set a specified state model in ElastiCache

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
