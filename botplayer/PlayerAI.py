import time

from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *

millitime = lambda: int(round(time.time() * 1000))

def dbout(a):
    # Debug printout
    print(a)
    pass

class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        self.currentTurn = 0
        self.tr_firingarc = [] # Turrets, firing arc
        self.i = -1;
        pass

    def getTurretFARC(self, gameboard):
        # Tiles affected by turrets firing
        # Calculates a list of lists
        
        for b in gameboard.turrets:
            # Firing range of turret
            d = []
            hasWall = [False, False, False, False] 
            dbout("Checking turret: " + str(b.x) + " " + str(b.y))
            for i in range(1,5):
                # Check in each of the four cardinal directions
                if (not gameboard.is_wall_at_tile(b.x, (b.y+i)%gameboard.width) and not hasWall[0]):
                    d.append((b.x, b.y+i)) 
                else: 
                    hasWall[0]=True

                if (not gameboard.is_wall_at_tile(b.x, (b.y-i)%gameboard.width) and not hasWall[1]):
                    d.append((b.x, b.y-i)) 
                else:
                    hasWall[1]=True

                if (not gameboard.is_wall_at_tile((b.x+i)%gameboard.width, b.y) and not hasWall[2]):
                    d.append((b.x+i, b.y)) 
                else:
                    hasWall[2]=True

                if (not gameboard.is_wall_at_tile((b.x-i)%gameboard.width, b.y) and not hasWall[3]):
                    d.append((b.x-i, b.y)) 
                else:
                    hasWall[3]=True
            self.tr_firingarc.append(d)

    def isDangerousTile(self, gameboard, tile):
        # Checks if a tile is dangerous, given that tile argument is 
        # dictionary of form {"x":x, "y":y}

        # Check for incoming turret fire
        if len(gameboard.turrets) > 0:
            for i, b in enumerate(gameboard.turrets):
                if (b.x == tile.x or b.y == tile.y) and b.is_firing_next_turn and (tile.x, tile.y) in self.tr_firingarc[i]:
                    return False

        # Check for incoming bullets
        # if len(gameboard.bullets) > 0:
        #     for i, b in enumerate(gameboard.bullets):
        #         

        return True

    def get_move(self, gameboard, player, opponent):
        start = millitime()

        dbout(gameboard.current_turn)
        # Initialize bot params
        if self.currentTurn == 0:
            self.getTurretFARC(gameboard)
        
        # Write your AI here.
        if len(gameboard.bullets) > 0:
            for i, b in enumerate(gameboard.bullets):
                dbout(str(i) + ":" + str(b.x) + "," + str(b.y) + "," + str(b.direction)+ "\t")
        
        dbout(self.isDangerousTile(gameboard, player))

        end = millitime()
        print("Time elapsed:" + str(end - start))
        
        moves = [Move.SHOOT, Move.NONE]
        self.i = self.i+1 if self.i<len(moves)-1 else len(moves)-1

        return moves[self.i]
