import json
import PythonClientAPI.libs.Communication.CommunicatorConstants as cc
class JSONSettingConfigurator():

    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.json_string = ""

    def set_configurations(self):
        self.read_json_from_file()
        self.read_configurations_from_json()

    def read_configurations_from_json(self):
        json_object = json.loads(self.json_string)
        cc.MAXIMUM_ALLOWED_RESPONSE_TIME = int(json_object['maxResponseTime'])
        cc.PORT_NUMBER = int(json_object['portNumber'])

    def read_json_from_file(self):
        with open(self.settings_path, "r") as json_file:
            self.json_string = json_file.read().replace('\n', '')

    def get_port_number(self):
        return cc.PORT_NUMBER

    def get_maximum_allowed_response_time(self):
        return cc.MAXIMUM_ALLOWED_RESPONSE_TIME