SDK
===

The Lumigator SDK is a Python library that provides a simple interface to interact with the
Lumigator API. You can use it to create, update, delete, and list datasets, submit and monitor jobs,
download the results, and more.

Lumigator Client
----------------

The main entry point to the SDK is the `LumigatorClient` class. You can create an instance of this
class by providing the Lumigator API host and your Ray cluster address.

.. automodule:: lumigator_sdk.lumigator
   :members:
   :undoc-members:

Health
------

The `Health` class provides a simple interface to check the health of the Lumigator API and the
status of the Ray jobs running on the cluster.

.. automodule:: lumigator_sdk.health
   :members:
   :undoc-members:

Datasets
--------

The `Datasets` class provides a simple interface to create, update, delete, and list datasets.

.. automodule:: lumigator_sdk.lm_datasets
   :members:
   :undoc-members:

Jobs
----

The `Jobs` class provides a simple interface to submit and monitor jobs. Currently, we support two
types of jobs: Inference and Evaluation.

.. automodule:: lumigator_sdk.jobs
   :members:
   :undoc-members:

Base Client
-----------

The `BaseClient` class provides a base class for the LumigatorClient. You can use this class to
create your own client with custom methods.

.. automodule:: lumigator_sdk.client
   :members:
   :undoc-members:
