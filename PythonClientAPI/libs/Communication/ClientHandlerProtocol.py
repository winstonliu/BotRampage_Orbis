import time
import uuid
import sys, traceback
import threading

import PythonClientAPI.libs.Communication.CommunicatorConstants as cc
from PythonClientAPI.libs.Communication.ClientChannelHandler import *
from PythonClientAPI.libs.Game.JSONParser import *
from PythonClientAPI.libs.Communication.Signals import *
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Communication.AIHandlerThread import *

class ClientHandlerProtocol():
    def __init__(self, player_ai, port_number, max_response_time, uuidString=uuid.uuid4()):
        self.player_ai = player_ai
        self.client_guid = uuidString
        self.game_is_ongoing = False
        self.ai_responded = True
        cc.MAXIMUM_ALLOWED_RESPONSE_TIME = max_response_time
        cc.PORT_NUMBER = port_number

    def start_connection(self):
        self.client_channel_handler = ClientChannelHandler()
        self.client_channel_handler.start_socket_connection(cc.PORT_NUMBER, cc.HOST_NAME)

    def receive_message(self):
        message = ''
        while message == '':
            message = self.client_channel_handler.receive_message()
        return message

    def communication_protocol(self):
        message_from_server = ''
        while (self.game_is_ongoing):
            message_from_server = self.receive_message()
            self.relay_message_and_respond_to(message_from_server)

    def validate_server_credentials(self):
        if hasattr(self.client_guid, 'urn'):
            uuid_as_string = ((self.client_guid.urn)[9:]).strip()
            self.client_channel_handler.send_message(uuid_as_string)
        else:
            self.client_channel_handler.send_message(self.client_guid)

    def start_communications(self):
        self.start_connection()
        self.validate_server_credentials()
        self.game_is_ongoing = True
        self.communication_protocol()

    def end_communications(self):
        self.client_channel_handler.close_connection()
        self.game_is_ongoing = False

    def relay_message_and_respond_to(self, message_from_server):
        if message_from_server == Signals.BEGIN.name:
            self.start_game()
        elif message_from_server == Signals.MOVE.name:
            self.next_move_from_client()
        elif message_from_server == Signals.END.name:
            self.end_communications()
        else:
            raise Exception("Unrecognized signal received from server {0}".format(message_from_server))
            self.end_communications()

    def start_game(self):
        client_information = ''
        self.client_channel_handler.send_message(client_information)

    def next_move_from_client(self):
        game_data_from_server = self.client_channel_handler.receive_message()
        decoded_game_data = decode_game_board_from_server_message(game_data_from_server)
        client_move = self.get_timed_ai_response(decoded_game_data)
        self.client_channel_handler.send_message(client_move)


    def get_timed_ai_response(self, game_data):
        if self.ai_responded:
            self.player_move_event = threading.Event()
            self.ai_handler_thread = AIHandlerThread(kwargs={'player_ai':self.player_ai,
                                                             'decoded_game_data': game_data,
                                                             'player_move_event': self.player_move_event})
            self.ai_handler_thread.start()
        end_time, start_time = self.time_response(self.player_move_event)
        if self.player_move_event.is_set() and is_valid_response_time(start_time, end_time):
            self.ai_responded = True
            return validate_game_move(self.ai_handler_thread.get_move()).name
        else:
            print("The AI timed out with a maximum allowed response time of: {0} ms".format(cc.MAXIMUM_ALLOWED_RESPONSE_TIME))
            print("time ", (time.time() - start_time) * 1000)
            self.ai_responded = False
            return Signals.NO_RESPONSE.name

    def time_response(self, player_move_event):
        start_time = time.time()
        while not player_move_event.is_set() and is_valid_response_time(start_time, time.time()):
            pass
        end_time = time.time()
        return end_time, start_time


def decode_game_board_from_server_message(game_data_from_server):
    decoded_game_data = JSONParser(game_data_from_server)
    return decoded_game_data

def validate_game_move(game_move):
    if game_move in Move:
        return game_move
    else:
        print("The AI did not return a valid move.")
        return Move.NONE

def is_valid_response_time(start_time, end_time):
    milliseconds_elapsed = (end_time - start_time) * 1000
    return milliseconds_elapsed < cc.MAXIMUM_ALLOWED_RESPONSE_TIME

