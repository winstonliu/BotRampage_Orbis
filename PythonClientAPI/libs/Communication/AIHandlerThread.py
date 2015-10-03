import threading
import traceback, sys
from PythonClientAPI.libs.Game.Enums import *

class AIHandlerThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, daemon=daemon, args=args, kwargs=kwargs)
        self.player_move = Move.NONE

    def run(self):
        player_ai = self._kwargs['player_ai']
        decoded_game_data = self._kwargs['decoded_game_data']
        player_move_event = self._kwargs['player_move_event']
        try:
            self.player_move = player_ai.get_move(decoded_game_data.gameboard, decoded_game_data.player,
                                                      decoded_game_data.opponent)
            player_move_event.set()
        except:
            print("An exception occurred in calling get_move: \n")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          file=sys.stdout)

    def get_move(self):
        return self.player_move