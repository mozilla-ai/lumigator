import requests

class HealthCheck():

    def __init__(self):
        self.status = ""
        self.deployment_type = ""

    def ok(self):
        return self.status == "OK"



