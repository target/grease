What is GREASE
*********************

GREASE is a distributed system written in Python designed to automate automation in operations. Typically for an
operations engineer to automated a repeated task or recovery they must account for

  #. Determine what the issue is
  #. Determine what the recovery is
  #. Figuring out when to run their recovery
  #. Writing the actual recovery
  #. Reporting the recovery event to alert developers an issue occurred

Here at Target GRE we noticed that engineers really only cared to actually fix the issue, not all the other stuff that
goes along with setting up cron jobs or scheduled tasks, and decided we could do something to make operations easier to
automate. GREASE was our solution. In GREASE an operations engineer's workflow looks like this:

  #. Determine what the issue is
  #. Determine what the recovery is
  #. Write a GREASE configuration
  #. Write the recovery

What Problem Does it Solve?
=================================

GREASE drastically reduces the complexity for our engineers since they can focus on recovery efforts rather than patching
their cron servers or "babysitting" their scripts directory. Additionally GREASE abstracts and reduces the amount of
code being written over and over to monitor our endpoints and detect when an issue is occurring.

*With GREASE engineers can engineer solutions to technical problems, not entire automation solutions*

What Does it Mean to be Distributed?
=======================================

A distributed system is where multiple discrete nodes in a network can communicate with each other to process data in a
faster more scalable way. GREASE takes advantage of this design to be able to handle production work loads of modern
operations staff.

This also means it is inherently more complex than a traditional application. Don't be worried though, it's simple enough
to get up and running! Typically GREASE is run on multiple VM's, Kubernetes Pods or physical hosts, although the entire
system can be sustained on a single system for either development or production.
*It is recommended in production to have at least two of each prototype (discussed later) to ensure minimum amounts of fault protection*

Where Can it Run?
=====================

Pretty much anywhere! GREASE is built in Python (supporting 2.7+ including 3!). This means anything that runs python
can run GREASE. The Daemon, our way of running GREASE services, is also cross-platform! We support all Systemd compliant
platforms (Linux), MacOS, and Windows Services. Checkout the :ref:`installing-grease` guide for more information on installing it.
