from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *


class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        pass

    def isDanger(self, gameboard, player, opponent):
        
        # Check for turrets
        pass



    def get_move(self, gameboard, player, opponent):
        # Write your AI here.
        if len(gameboard.bullets) > 0:
            for b in gameboard.bullets:
                print(str(b.x) + "," + str(b.y) + "\t")
        return Move.SHOOT
