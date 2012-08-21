DIRS := $(shell find . -name ".batch-make" -printf "%h\n")

all: ${DIRS}

${DIRS}:
	@make -C $@

.PHONY: ${DIRS}
