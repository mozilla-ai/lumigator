import requests

from sdk.core import LumigatorClient as cl


class HealthCheck():

    def __init__(self):
        self.status = ""
        self.deployment_type = ""

    def ok(self):
        return self.status == "OK"



