## es7s/pysuncalc            ## Library for sun timings calculations
## (C) 2023                  ## A. Shavykin <0.delameter@gmail.com>
##---------------------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pysuncalc

DOTENV = .env
DOTENV_DIST = .env.dist
OUT_BUILD_RELEASE_PATH = dist

include ${DOTENV_DIST}
-include ${DOTENV}
export
VERSION ?= 0.0.0

NOW    := $(shell date '+%Y-%b-%0e.%H%M%S.%3N')
BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
DIM    := $(shell tput -Txterm dim)
RESET  := $(shell printf '\e[m')
                                # tput -Txterm sgr0 returns SGR-0 with
                                # nF code switching esq, which displaces the columns
## Common commands

help:   ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^(##)\s?(\s*#?[^#]+)#*\s*(.*)/\1${YELLOW}\2${RESET}#\3/; s/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/; s/\*(\w+)\*/${BOLD}\1${RESET}/g; 2~1s/<([*<@>.A-Za-z0-9_-]+)>/${DIM}\1${RESET}/gi' -e 's/(\x1b\[)33m#/\136m/' | column -ts# | sed -Ee 's/ {3}>/ >/'

##
## Pre-build

demolish-build:  ## Delete build output folders
	rm -f -v ${OUT_BUILD_RELEASE_PATH}/*

show-version: ## Show current package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"

set-version: ## Set new package version
set-version: show-version
	@read -p "New version (press enter to keep current): " VERSION
	if [ -z $$VERSION ] ; then echo "No changes" && return 0 ; fi
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" ${DOTENV_DIST} ${DOTENV}
	sed -E -i "s/^__version__.+/__version__ = \"$$VERSION\"/" ${PROJECT_NAME}/_version.py
	echo "Updated version: ${GREEN}$$VERSION${RESET}"

purge-cache:  ## Clean up pycache
	find . -type d \( -name __pycache__ -or -name .pytest_cache \) -print -exec rm -rf {} +

##
## Testing

test: ## Run pytest
	hatch run test:test

cover: ## Run coverage and make a report
	hatch run test:cover

##
## Building / Packaging

build: ## Create new *public* build
build: demolish-build
	hatch --verbose -e build build

publish: ## Upload last *public* build (=> PRIMARY registry)
	hatch --verbose -e build publish \
		-u ${HATCH_INDEX_USER} \
		-a ${HATCH_INDEX_AUTH}

##
