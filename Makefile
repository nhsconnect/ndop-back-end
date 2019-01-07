export SHELL=/bin/bash


#--- VARIABLES ---
#Defaulted to ensure they are passed in
directory = none
unit_test_directory = none
#Build vars
python_version = 3.6.0
python_coverage_threshold = 90


default:
	@echo "A task must be specified"

check-directory:
ifeq ("$(directory)", "none")
	$(error A 'directory' param must be specified for this command)
endif

check-unit_test_directory:
ifeq ("$(unit_test_directory)", "none")
	$(error A 'unit_test_directory' param must be specified for this command)
endif

#--- BUILD UTILS TARGETS ---
install-python:
	scripts/code-build-utils.sh installPython $(python_version)

install-python-global-dependencies: check-directory
	scripts/code-build-utils.sh installPythonGlobalDependencies $(directory)

install-python-dependencies: check-directory
	scripts/code-build-utils.sh installPythonDependencies $(directory)

unit-test-python-lambdas:
	scripts/code-build-utils.sh unitTestPythonLambdas state_model unit_tests

coverage-python-lambdas:
	scripts/code-build-utils.sh coveragePythonLambdas state_model unit_tests $(python_coverage_threshold)

lint-python-lambdas: 
	scripts/code-build-utils.sh lintPythonLambdas state_model

package-python-lambdas: 
	scripts/code-build-utils.sh packagePythonLambdas state_model
