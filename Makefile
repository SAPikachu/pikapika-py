DIRS := $(shell find . -name ".batch-make" -printf "%h\n")

all: ${DIRS} update_static_version

${DIRS}:
	@make -C $@

update_static_version:
	./manage.py update_static_version

.PHONY: ${DIRS} update_static_version
