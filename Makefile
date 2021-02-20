###
# Config
###

JOBS ?= $(shell nproc)
MAKEFLAGS += -j $(JOBS) -r

PATH := $(abspath node_modules)/.bin:$(PATH)

.DELETE_ON_ERROR:
.SECONDARY:
.SUFFIXES:

LPAREN := (
RPAREN := )

###
# Clean
###

TARGET := mllp_http.egg-info build target

.PHONY: clean
clean:
	rm -fr $(TARGET)

###
# Format
###
FORMAT_SRC := $(shell find . $(TARGET:%=-not \$(LPAREN) -name % -prune \$(RPAREN)) -name '*.py')

.PHONY: format
format: target/format.log

.PHONY: test-format
test-format: target/format-test.log

target/format.log: $(FORMAT_SRC) target/node_modules.target
	black $(FORMAT_SRC)
	node_modules/.bin/prettier --write .
	mkdir -p $(@D)
	touch $@ target/format-test.log

target/format-test.log: $(FORMAT_SRC)
	black --check $(FORMAT_SRC)
	mkdir -p $(@D)
	touch $@ target/format.log

###
# Npm
###
target/node_modules.target:
	yarn install
	> $@

###
# Pip
###
PY_SRC := $(shell find . $(TARGET:%=-not \$(LPAREN) -name % -prune \$(RPAREN)) -name '*.py')

.PHONY: install
install:
	pip3 install -e .

.PHONY: package
package: target/package.log

upload: target/package-test.log
	python3 -m twine upload target/package/*

target/package.log: setup.py README.md $(PY_SRC)
	rm -fr $(@:.log=)
	mkdir -p $(@:.log=)
	./$< bdist_wheel -d $(@:.log=) sdist -d $(@:.log=)
	> $@

target/package-test.log: target/package.log
	python3 -m twine check target/package/*
	mkdir -p $(@D)
	> $@

###
# Docker
###

.PHONY: docker
docker:
	docker build -t rivethealth/mllp-http .
