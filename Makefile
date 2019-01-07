export SHELL=/bin/bash

default:
	@echo "A task must be specified"

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

unit-test-python-lambdas: check-directory check-unit_test_directory
	scripts/code-build-utils.sh unitTestPythonLambdas $(directory) $(unit_test_directory)

coverage-python-lambdas: check-directory check-unit_test_directory
	scripts/code-build-utils.sh coveragePythonLambdas $(directory) $(unit_test_directory) $(python_coverage_threshold)

lint-python-lambdas: check-directory
	scripts/code-build-utils.sh lintPythonLambdas $(directory)

package-python-lambdas: check-directory
	scripts/code-build-utils.sh packagePythonLambdas $(directory)
