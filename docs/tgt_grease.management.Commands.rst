GREASE Cluster Management Commands
=====================================

Monitoring Prototype (monitor)
--------------------------------------------

This command prototype is installed on all servers by default. It ensures the cluster remains healthy
and that nodes that are no longer responding are culled from the environment

.. autoclass:: tgt_grease.management.Commands.monitor.ClusterMonitor
    :members:
    :undoc-members:
    :show-inheritance:

Administrative CLI (bridge)
--------------------------------------------

This command gives users a place to interact with their cluster on the CLI

.. autoclass:: tgt_grease.management.Commands.bridge.Bridge
    :members:
    :undoc-members:
    :show-inheritance:
