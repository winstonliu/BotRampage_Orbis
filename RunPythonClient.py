import os
import sys
import json
import importlib
import imp

from PythonClientAPI.libs.Communication.ClientHandlerProtocol import *
from PythonClientAPI.libs.Configurator.JSONSettingConfigurator import *
import PythonClientAPI.libs.Configurator.Constants as constants
import PythonClientAPI.libs.Communication.CommunicatorConstants as cc


def set_configurations(settings_path):
    script_dir = os.path.dirname(__file__)
    settings_path = os.path.join(script_dir,constants.JSON_SETTINGS_PATH)
    json_configurator = JSONSettingConfigurator(settings_path)
    json_configurator.set_configurations()
    cc.PORT_NUMBER = json_configurator.get_port_number()
    cc.MAXIMUM_ALLOWED_RESPONSE_TIME = json_configurator.get_maximum_allowed_response_time()

if __name__ == '__main__':
    UUIDForAi = ""
    try:
        set_configurations(constants.JSON_SETTINGS_PATH)
    except Exception as e:
        print (e)
    #Get rid of command
    sys.argv.pop(0)
    for i in range (int(len(sys.argv)/2)):
        if sys.argv[i*2] == "-p":
            cc.PORT_NUMBER = int(sys.argv[i*2+1])
        elif sys.argv[i*2] == "-d":
            constants.PLAYER_AI_PATH = sys.argv[i*2+1]
        elif sys.argv[i*2] == "-n":
            UUIDForAi = sys.argv[i*2+1]
    try:
        sys.path.append (constants.PLAYER_AI_PATH)
        tempString = constants.PLAYER_AI_PATH
        while ( '\\' in tempString):
            sys.path.append (tempString[:tempString.rindex('\\')])
            tempString = tempString[:tempString.rindex('\\')]
    except:
        pass
    fp, pathname, description = imp.find_module('PlayerAI', [constants.PLAYER_AI_PATH])
    player_ai_module = imp.load_module('PlayerAI', fp, pathname, description)
    client_ai = player_ai_module.PlayerAI()
    if (UUIDForAi == ""):
        client_handler_protocol = ClientHandlerProtocol(client_ai, cc.PORT_NUMBER, cc.MAXIMUM_ALLOWED_RESPONSE_TIME)
    else:
        client_handler_protocol = ClientHandlerProtocol(client_ai, cc.PORT_NUMBER, cc.MAXIMUM_ALLOWED_RESPONSE_TIME,
                                                        UUIDForAi)
    client_handler_protocol.start_communications()

