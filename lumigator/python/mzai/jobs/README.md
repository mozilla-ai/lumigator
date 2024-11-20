# How to write a new job

To add a new job to Lumigator, go to the `lumigator/python/mzai/schemas/lumigator_schemas` folder and perform the following steps:

* Create a new enum value in `lumigator_schemas.jobs.JobType` called for example `<JOB_NAME>`.
* Create a new file named `<job_name>_config.py` containing:
  * Any necessary Pydantic models for the job configuration (passed as payload to the `CreateJob` endpoint).
  * The following properties:
    * `COMMAND`: the shell command needed to run the job (config is added automatically as a json in the `--config` command line paramater). If the rest of Python files are just scripts, this could be just `python <entrypoint>.py`
    * `PIP_REQS`: the name of the file including the package requirements (see below).
    * `WORK_DIR`: the URL for the packed directory containing any necessary input files, or `None` if a fresh environment is to be used.
    * `MODEL`: the class holding the top level job configuration model.

Then create a new folder under the `lumigator/python/mzai/jobs` folder called `<job_name>`. Within that folder:

* Create any new files as needed to implement the task itself. These files need not be structured in modules. These files can import the entities declared in `<job_name>_config.py` file created above with `import lumigator_schemas.<job_name>_config`.
* Create a file containing the package requirements, usually called `requirements.txt`, which has been referenced in the `PIP_REQS` property above.