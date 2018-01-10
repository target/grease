# GREASE

###### [Our Trello Board for Feature Tracking](https://trello.com/b/c1jXxBvA/grease)

###### Automation as a Service

[![Travis](https://img.shields.io/travis/rust-lang/rust.svg)](https://travis-ci.org/target/grease)
[![AppVeyor](https://img.shields.io/appveyor/ci/lemoney/grease.svg)](https://ci.appveyor.com/project/lemoney/grease)
[![Current Version](https://badge.fury.io/py/tgt-grease.svg)](https://pypi.python.org/pypi/tgt-grease)
[![Read the Docs](https://img.shields.io/readthedocs/pip.svg)](https://grease.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/target/grease/blob/master/LICENSE)


## GREASE
  * Guest
  * Reliability
  * Engineering
  * Automation
  * Solution
  * Engine
  
## What it does

GREASE is designed as a system to enable generalized and large scale 
automation efforts. Rather than approaching automation via manual 
scripts, scheduled runs in a task runner system, GREASE is designed 
to be completely hands free. This _enables true and actual 
automation and reduction of toil_. GREASE is designed to stop the 
decades old mentality of operations and operators from 
break/fix work, and redirect their efforts to the principles
of SRE. A common simile for GREASE is: "Let Operations 
**STOP** fighting all these fires (automated preventable incidents), 
install the sprinkler system (GREASE) and begin performing arson 
investigation (helping solutions portfolio working on & prioritizing
their backlog/Designing better processes and infrastructure)

GREASE provides a simple JSON configuration schema for
issue detection and a safe Python command class for 
implementing resolutions. 

## How it works

GREASE runs 24/7/365 monitoring sources you define and 
based on configuration can act on these sources. These actions
can be anything you can do in python.

Out of the box GREASE is very minimal, it is but an engine. Similar
to Django, you write your application, GREASE just serves it. 

## Getting the Docs

  1. Install sphinx `pip install sphinx`
  2. generate the docs by running `make html`
  3. Use a web browser to read the docs starting at `<project root>/docs/_build/index.html`

## Requirements
  1. Python2.7
  2. Pip
     * requests
     * pymongo
     * psutil
     * psycopg2
     * elasticsearch
     * psutil
     * **FOR WINDOWS ONLY** pypiwin32
     
## Installing
  
### Via PIP

Simply run `pip install tgt_grease`

### Manually

  1. Clone this repo to your machine
  2. from the created directory run `python setup.py install`
