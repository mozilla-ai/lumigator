import copy

import pytest
from inference_config import InferenceJobConfig
from pydantic import ValidationError


def configs_with_missing_field(cfgd):
    for k in cfgd.keys():
        # make a copy of the dict
        d_copy = cfgd.copy()

        if isinstance(cfgd[k], dict):
            # iterate depth-first on its keys
            for d_child in configs_with_missing_field(cfgd[k]):
                d_copy[k] = d_child
                yield d_copy

        # after removing each child, finally remove the parent
        print(f"Removing {k}")
        del d_copy[k]
        # return the dict without the key
        yield d_copy


def configs_with_extra_field(cfgd):
    for k in cfgd.keys():
        if isinstance(cfgd[k], dict):
            # add an extra key to the sub-dict
            d_copy = copy.deepcopy(cfgd)
            d_copy[k]["new_key"] = "whatever"
            yield d_copy

    # add an extra key to the root of the dict
    d_copy = copy.deepcopy(cfgd)
    d_copy["new_key"] = "whatever"
    yield d_copy


def test_minimal_cfg(json_config_minimal: dict):
    # the minimal config is always a valid config
    try:
        InferenceJobConfig.model_validate(json_config_minimal)
    except Exception as e:
        pytest.fail(f"Exception: {e}")

    # if you remove any key from the minimal config, pydantic should raise an exception
    for json_config_minus_field in configs_with_missing_field(json_config_minimal):
        with pytest.raises(ValidationError):
            InferenceJobConfig.model_validate(json_config_minus_field)


def test_full_cfg(json_config_full_api: dict, json_config_full_hf: dict):
    # the full config is always a valid config
    try:
        InferenceJobConfig.model_validate(json_config_full_api)
        InferenceJobConfig.model_validate(json_config_full_hf)
    except Exception as e:
        pytest.fail(f"Exception: {e}")

    # if you add any extra field to the full config, pydantic should raise an exception
    for json_config_plus_field in configs_with_extra_field(json_config_full_api):
        with pytest.raises(ValidationError):
            InferenceJobConfig.model_validate(json_config_plus_field)

    for json_config_plus_field in configs_with_extra_field(json_config_full_hf):
        with pytest.raises(ValidationError):
            InferenceJobConfig.model_validate(json_config_plus_field)


def test_invalid_hf_config(json_config_minimal):
    # the invalid task config is always an invalid config

    json_config_minimal.setdefault("pipeline", {})

    invalid_task = json_config_minimal["pipeline"]["task"] = "foo"
    with pytest.raises(ValidationError):
        InferenceJobConfig.model_validate(invalid_task)

    invalid_model_repo_id = json_config_minimal["pipeline"]["model_path"] = "hf://foo"
    with pytest.raises(ValidationError):
        InferenceJobConfig.model_validate(invalid_model_repo_id)

    invalid_torch_dtype = json_config_minimal["pipeline"]["torch_dtype"] = "foo"
    with pytest.raises(ValidationError):
        InferenceJobConfig.model_validate(invalid_torch_dtype)

    invalid_accelerator = json_config_minimal["pipeline"]["accelerator"] = "foo"
    with pytest.raises(ValidationError):
        InferenceJobConfig.model_validate(invalid_accelerator)
