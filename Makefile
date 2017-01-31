# Project configuration
PROJECT_NAME = rundeck_create_users_from_ldap
MODULE = $(PROJECT_NAME).py

# Call these functions before/after each target to maintain a coherent display
START_TARGET = @printf "[$(shell date +"%H:%M:%S")] %-40s" "$(1)"
END_TARGET = @printf "\033[32;1mOK\033[0m\n"

# Parameter expansion
PYTEST_OPTS ?=


.PHONY: clean help \
	check_pep8 check_pylint check_xenon check_lint


help:
	@echo "check_pep8         Apply pep8 checks (core coding style)"
	@echo "check_pylint       Apply pylint checks (code quality)"
	@echo "check_xenon        Apply xenon checks (code complexity)"
	@echo "check_lint         Apply pep8, pylint, xenon"
	@echo "clean              Remove useless temporary files"


check_pep8:
	$(call START_TARGET,Checking pep8)
	@pep8 $(MODULE)
	$(call END_TARGET)


check_pylint:
	$(call START_TARGET,Checking pylint)
	@pylint -rno $(MODULE)
	$(call END_TARGET)


check_xenon:
	$(call START_TARGET,Checking xenon)
	@xenon -m A -a A -b A --no-assert $(MODULE)
	$(call END_TARGET)


check_lint: check_pep8 check_pylint check_xenon


clean:
	$(call START_TARGET,Cleaning)
	@find . -type f -name '*.pyc' -exec rm {} \;
	@rm -rf dist/* *.egg-info .cache .eggs
	@rm -rf htmlcov .coverage
	@rm -f junit.xml
	$(call END_TARGET)
