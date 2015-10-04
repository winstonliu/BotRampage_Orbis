from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.GameObjects import GameObject
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *
from networkx import nx

class EvasiveManeuvers:
    def __init__(self):
        pass

    def findSafety(self, gb_local, player, avoid):

        nx.bfs_tree(gb_local, (player.y, player.x))


        
        
