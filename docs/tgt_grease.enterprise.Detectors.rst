GREASE Source Detectors
=====================================

Detectors are used to parse data from sourcing and determine if a job needs to be executed.

**NOTE**: If developing a new detector it is the accepted practice for all non-error log messages to be set to only
print in *verbose* mode

Regex Detector
--------------------------------------------

.. autoclass:: tgt_grease.enterprise.Detectors.Regex
    :members:
    :undoc-members:
    :show-inheritance:

Exists Detector
--------------------------------------------

.. autoclass:: tgt_grease.enterprise.Detectors.Exists
    :members:
    :undoc-members:
    :show-inheritance:

Range Detector
--------------------------------------------

.. autoclass:: tgt_grease.enterprise.Detectors.Range
    :members:
    :undoc-members:
    :show-inheritance:

DateRange Detector
--------------------------------------------

.. autoclass:: tgt_grease.enterprise.Detectors.DateRange
    :members:
    :undoc-members:
    :show-inheritance:

DateDelta Detector
--------------------------------------------

.. autoclass:: tgt_grease.enterprise.Detectors.DateDelta
    :members:
    :undoc-members:
    :show-inheritance:
