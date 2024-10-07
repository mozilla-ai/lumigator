from pydantic.json_schema import models_json_schema

import yaml
import enum
import inspect

import mzai.schemas.completions
import mzai.schemas.datasets
import mzai.schemas.deployments
import mzai.schemas.experiments
import mzai.schemas.groundtruth
import mzai.schemas.jobs

def print_json_schema():
    packages = [mzai.schemas.completions, mzai.schemas.datasets, mzai.schemas.deployments, mzai.schemas.experiments, mzai.schemas.groundtruth, mzai.schemas.jobs]
    models = [(model, "validation") for model_list in [[model_p for (name, model_p) in inspect.getmembers(package, inspect.isclass) if model_p.__module__ == package.__name__ and not issubclass(model_p, enum.Enum)] for package in packages] for model in model_list]
    print(models)
    _, schemas = models_json_schema(
        models,
        ref_template="#/components/schemas/{model}",
    )
    openapi_schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Lumigator API",
            "version": "0.0.1",
        },
        "components": {
            "schemas": schemas.get('$defs'),
        }
    }
    print(yaml.dump(openapi_schema))

if __name__ == '__main__':
    print_json_schema()