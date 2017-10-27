# GREASE

###### Automation as a Service

[![Build Status](https://travis-ci.org/target/grease.svg?branch=master)](https://travis-ci.org/target/grease)
[![Current Version](https://badge.fury.io/py/tgt-grease.svg)](https://pypi.python.org/pypi/tgt-grease)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/target/grease/blob/master/LICENSE)


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

## Installation & Requirements

### Requirements
  1. Python2.7
  2. Pip
     * psycopg2
     * requests
     * pymongo
     * sqlalchemy
     * python-dotenv
     * psutil
