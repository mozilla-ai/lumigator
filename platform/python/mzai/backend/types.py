from typing import Any, NewType

S3Client = NewType("S3Client", Any)
"""Dummy type for a boto3 S3 client becuase the library is untyped.

TODO(MZPLATFORM-87): Look into using a type stub library for boto3.
"""


UnprocessableEntityError = UnicodeError  # TODO: Add more in a union type here
"""An expected error from failing to process a file."""
