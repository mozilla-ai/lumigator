# Are these schemas used in both API and SDK?
# As long as they're not used for other purposes
# like DB storage, it should be ok

# We could start with an OpenAPI spec and then generate the models
# using https://docs.pydantic.dev/latest/integrations/datamodel_code_generator/

# Otherwise, we can generate manually the openapi spec using
# https://www.speakeasy.com/openapi/frameworks/pydantic

# One important item is versioning: the `info` item in an OpenAPI
# spec contains the version of the application API itself.
# We'd need to check how to add the info to the openapi spec, but
# here are detailed instructions that we could explore:
# https://www.speakeasy.com/openapi/frameworks/pydantic