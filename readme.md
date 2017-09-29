# GREASE

###### Automation as a Service

[![Build Status](https://travis-ci.org/target/grease.svg?branch=master)](https://travis-ci.org/target/grease)

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
  1. PostgreSQL 9.4+
      * Provision the database with the `database.sql` file
      included here.
  2. Python2.7
  3. Pip
      * Requests
      * Psycopg2
      * PyMongo

### Installation
  1. Setup Your Environment Variables
      * `GREASE_DSN` is the only one required at this point
  2. Install GREASE
      * `python setup.py install`
  3. Register with your database
      * `grease enterprise bridge register`
  4. Next Steps
      * Develop your module for GREASE Commands and Configurations
      * Setup your environment for this package:
          * `GREASE_CONF_PKG`: Your configuration Package
          * `GREASE_CONF_DIR`: The directory in your package for 
          configurations to be loaded from
          * `GREASE_SOURCES_PKG`: The package to load sources from
      * if you plan to enable MongoDB for source de-duplication you'll
      need some additional variables set:
          * `GREASE_MONGO_HOST`: MongoDB Host Name
          * `GREASE_MONGO_PORT`: MongoDB Port (Defaults to 27017)
          * `GREASE_MONGO_USER`: MongoDB Auth Username
          * `GREASE_MONGO_PASSWORD`: MongoDB Auth Password
          * `GREASE_MONGO_DB`: Database Name (defaults to grease)
