from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *

class TurretHunter:
    def __init__(self):
        self.turret_mappings = {}
        self.tr_firingarc = []
    
    def inFARC(self, gameboard, player):

    def getTurretFARC(self, gameboard):
        # Tiles affected by turrets firing
        # Calculates a list of lists (y,x)
        
        for b in gameboard.turrets:
            # Firing range of turret
            d = []
            hasWall = [False, False, False, False] 
            turretFARC("Checking turret: " + str(b.x) + " " + str(b.y))
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
            self.tr_firingarc.append(d)

        self.updateTurretMappings() 
        return self.tr_firingarc

    def updateTurretList(self, gameboard):
        for i, b in enumerate(gameboard.turrets):
            if b.is_dead:
               del self.tr_firingarc[i] 
        updateTurretMappings()
        return self.tr_firingarc
         
    def updateTurretMappings(self):
        for i, turret_arc in enumerate(self.tr_firingarc):
            for b in turret_arc:
                self.turret_mappings[(b.x, b.y)] = i

         
        
