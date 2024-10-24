.. Lumigator documentation

Lumigator documentation
====================================
Lumigator is a collection of jobs for finetuning and evaluating open-source (large) language models.
The library makes use of YAML-based configuration files as inputs to CLI commands for each job,
and tracks input/output data with Weights and Biases artifacts.

Getting Started
---------------
.. toctree::
   :maxdepth: 3

   README
   .devcontainer/README


Evaluation
----------

.. toctree::
   :maxdepth: 3

   EVALUATION_GUIDE

Examples
----------
.. toctree::
   :maxdepth: 3

   examples/README

SDK
===

.. toctree::
   :maxdepth: 2

   sdk
   tests


API
===

.. autosummary::
   :recursive:

   sdk.client
   sdk.completions
   sdk.experiments
   sdk.health
   sdk.lm_datasets
   sdk.lumigator
   tests

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
