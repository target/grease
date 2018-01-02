The GREASE User Guide
***********************

.. _userguide:


.. _ugconfig:

1. Writing New Configurations
===============================

Typically a user will write prototype configurations, so we will focus on those here. To learn more about all the
different types of configurations see the :ref:`datamodel` page for more information.

A Prototype Config tells GREASE where to look, what to watch for , where to run, and what to pass to a command. The
schema for a configuration can be found here :ref:`datamodel`. Let's say you have GREASE installed and you want to
monitor :code:`localhost` to make sure a webserver is still running via a synthetic transaction using a GET request.
That configuration would look something like this::

    {
        "name": "webserver_check_alive",
        "job": "reboot_local_webserver",
        "source": "url_source",
        "url": ["http://localhost:3000/users/7"],
        'minute': 30,
        "logic": {
            "Range": [
                {
                    "field": "status_code",
                    "min": 200,
                    "max": 200,
                    "variable": true,
                    "variable_name": "status_code"
                }
            ]
        }
    }

This configuration will tell GREASE to perform a HTTP GET on the address :code:`http://localhost:3000/users/7` once
every hour and ensure that a status code of 200 is returned. If it is not then the job :code:`reboot_local_webserver`
will be scheduled to run. It will be passed the variable :code:`status_code` in its' context.

Now that we have a config written lets focus on the command :code:`reboot_local_webserver` in the next section.

2. Writing Commands
======================

Commands are Python classes that are executed when configurations determine to do so. Building from :ref:`ugconfig` lets
now write the command :code:`reboot_local_webserver`.

Commands extend a base class :code:`tgt_grease.core.Types.Command` found here: :ref:`commandtype`. Here is a basic command
for explaining a command::

    from tgt_grease.core.Types import Command
    import subprocess

    # Class name doesn't have to match command. But your Plugin Package must export the matching name (use alias')
    class RestartLocalWebServer(Command):

        def __init__(self):
            super(RestartLocalWebServer, self).__init__()

        def execute(self, context):
            # Send a notification
            self.ioc.getNotification().SendMessage("ERROR: Local Web Server returned back health check::status code [{0}]".format(context.get("status_code")))
            # Attempt the restart
            return self.restart_nginx()

        def restart_nginx(self):
            if subprocess.call(["systemctl", "restart", "nginx"]) == 0:
                return True
            else:
                return False

This command attempts to restart Nginx. If successful it will return true telling the engine the recovery has been
performed. If it does not get a good exit code it returns false letting the engine know it needs to attempt the recovery
again. **NOTE**: GREASE will only attempt a recovery 6 times before determining the command cannot succeed and stops attempting
execution of it.

Since this is just traditional Python code you can do anything here! Call PowerShell scripts, interact with executables,
call some Java Jar you need, the possibilities are endless. All the GREASE Prototypes extend this base class and run all
of what we call GREASE.

Variable Storage
-------------------

Lets say we want to expand this example. We now want to execute only on the fifth 404. Rather than making the configuration
language very complicated we chose to put application logic in the applications, or as we call them, commands. This is where
variable storage comes into play. Since commands are typically short lived executions we offer the :code:`variable_storage`
property to your commands which is a provisioned collection just for your command. Lets refactor our command to use this
feature::

    from tgt_grease.core.Types import Command
    import subprocess
    import datetime

    # Class name doesn't have to match command. But your Plugin Package must export the matching name (use alias')
    class RestartLocalWebServer(Command):

        def __init__(self):
            super(RestartLocalWebServer, self).__init__()

        def execute(self, context):
            # Store the new bad status code
            self.variable_storage.insert_one(
                {
                    'createTime': (datetime.datetime.utcnow() + datetime.timedelta(hours=6)),
                    'docType': 'statusCode',
                    'status_code': context.get('status_code')
                }
            )
            # Ensure a TTL for these documents
            self.variable_storage.create_index([('createTime', 1), ('expireAfterSeconds', 1)])
            # Count the number of bad status'
            if self.variable_storage.find({'docType': 'status_code'}).count() > 5:
                # Send a notification
                self.ioc.getNotification().SendMessage("ERROR: Local Web Server returned back health check::status code [{0}]".format(context.get("status_code")))
                # Attempt the restart
                return self.restart_nginx()
            else:
                # Don't have enough bad status codes yet, so no failure condition
                return True

        def restart_nginx(self):
            if subprocess.call(["systemctl", "restart", "nginx"]) == 0:
                return True
            else:
                return False

Look at that! We have a pretty complete program there to restart a web server in the event of more than 5 bad requests
sent to a web server.

3. Testing your Code
=====================

Testing your code is very important, especially when you are engineering reliability! So GREASE helps with that too! Using
the built in test class found here: :ref:`commandtesttype`. Lets continue our series by writing a test for our command.
First We will write a test using the original command without Variable Storage::

    from tgt_grease.core.Types import AutomationTest
    from tgt_grease.core import Configuration
    from my_demo_package import webserver_check_alive


    class TestLocalWSRestart(AutomationTest):

        def __init__(self, *args, **kwargs):
            AutomationTest.__init__(self, *args, **kwargs)
            # For example our file name is basic.config.json so after install it will be here
            self.configuration = "fs://{0}".format(Configuration.greaseDir + 'etc/basic.config.json')
            # Mock data we expect to see from the web server
            self.mock_data = {
                'url': 'localhost:8000',
                'status_code': 500
            }
            # What we expect detection to tell us
            self.expected_data = {
                'status_code': 500
            }
            # Enable testing
            self.enabled = True

        def test_command(self):
            d = webserver_check_alive()
            # Overload the restart_nginx function for testing purposes
            d.restart_nginx = lambda: True
            self.assertTrue(d.execute({'status_code': 500}))

Now when running `python setup.py test` on your plugin your commands will be tested for their ability to detect
correctly and execute the way you would like. Since we use standard tooling you can also use tools to extract code
coverage and other statistics.

Testing with Variable Storage
--------------------------------

Testing commands that use Variable Storage is just as simple. We just need to refactor our test a little bit to
arrange state around the command a bit::

    from tgt_grease.core.Types import AutomationTest
    from tgt_grease.core import Configuration
    from my_demo_package import webserver_check_alive
    import datetime


    class TestLocalWSRestart(AutomationTest):

        def __init__(self, *args, **kwargs):
            AutomationTest.__init__(self, *args, **kwargs)
            # For example our file name is basic.config.json so after install it will be here
            self.configuration = "fs://{0}".format(Configuration.greaseDir + 'etc/basic.config.json')
            # Mock data we expect to see from the web server
            self.mock_data = {
                'url': 'localhost:8000',
                'status_code': 500
            }
            # What we expect detection to tell us
            self.expected_data = {
                'status_code': 500
            }
            # Enable testing
            self.enabled = True

        def test_command(self):
            d = webserver_check_alive()
            # Overload the restart_nginx function for testing purposes
            for i in range(0, 5):
                d.variable_storage.insert_one(
                    {
                        'createTime': (datetime.datetime.utcnow() + datetime.timedelta(hours=6)),
                        'docType': 'statusCode',
                        'status_code': context.get('status_code')
                    }
                )
            d.restart_nginx = lambda: True
            self.assertTrue(d.execute({'status_code': 500}))
            # Now just clean up state
            d.variable_storage.drop()
