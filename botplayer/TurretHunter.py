from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.GameObjects import GameObject
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *

def dbout(a):
    # Debug dboutout
    # dbout(a)
    pass

class TurretHunter:
    def __init__(self):
        self.turret_mappings = {}
        self.turret_info = {} # key is index, elements is dictionary of firing arc and mappings
    
    def getTurretFARC(self, gameboard):
        # Tiles affected by turrets firing
        
        for j, b in enumerate(gameboard.turrets):
            # Firing range of turret
            d = []
            hasWall = [False, False, False, False]
            for i in range(1,5):
                # Check in each of the four cardinal directions
                if (not gameboard.is_wall_at_tile(b.x, (b.y+i)%gameboard.height) and not hasWall[0]):
                    d.append((b.x, (b.y+i)%gameboard.height))
                else: 
                    hasWall[0]=True
                if (not gameboard.is_wall_at_tile(b.x, (b.y-i)%gameboard.height) and not hasWall[1]):
                    d.append((b.x, (b.y-i)%gameboard.height))
                else:
                    hasWall[1]=True
                if (not gameboard.is_wall_at_tile((b.x+i)%gameboard.width, b.y) and not hasWall[2]):
                    d.append(((b.x+i)%gameboard.width, b.y))
                else:
                    hasWall[2]=True
                if (not gameboard.is_wall_at_tile((b.x-i)%gameboard.width, b.y) and not hasWall[3]):
                    d.append(((b.x-i)%gameboard.width, b.y))
                else:
                    hasWall[3]=True
            dbout("Key: " + str(j))
            self.turret_info[j] = {"FARC" : d, "MAP" : {}}
        self.updateTurretMappings() 

    def updateTurretList(self, gameboard):
        for i, b in enumerate(gameboard.turrets):
            if b.is_dead and i in self.turret_info:
                del self.turret_info[i]
         
    def updateTurretMappings(self):
        for turret in (self.turret_info):
            for b in self.turret_info[turret]["FARC"]:
                self.turret_info[turret]["MAP"][(b[0], b[1])] = turret

    def buildAvoidanceListYX(self, gameboard):
        avoid = []
        for i, b in enumerate(gameboard.turrets):
            dbout(str(i) + " index " + str(b.is_firing_next_turn))
            if b.is_firing_next_turn:
                dbout(self.turret_info[i]["FARC"])
                for k in self.turret_info[i]["FARC"]:
                    avoid.append((k[1], k[0]))
        return avoid
