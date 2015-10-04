import time

from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *
from networkx import nx

millitime = lambda: int(round(time.time() * 1000))

def dbout(a):
    # Debug printout
    print(a)
    pass

class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        self.tr_firingarc = [] # Turrets, firing arc (x,y)
        self.i = -1;
        pass
        
    def should_fire_laser(self, gameboard, player, opponent):
        path = self.get_shortest_path(player, opponent, [])
        if len(path)<=5:
            return True
        return False
        
    def closest_power_up(self, gameboard, player, avoid_list):
        paths = []
        for ps in gameboard.power_ups:
            paths.append(self.get_shortest_path(player, ps, avoid_list)) #TO ADD - AVOID
        mind = 1000000
        cur_index = 0
        for i in range(0, len(paths)):
            if len(paths[i]) < mind:
                mind = len(paths[i])
                cur_index = i
        return paths[cur_index]

    def avoid_opponent_laser(self, gameboard, opponent):
        avoid_list = []
        wall_encountered = [False, False, False, False]
        for i in range(1, 4):
            if not wall_encountered[0] and not gameboard.is_wall_at_tile(opponent.x, (opponent.y-i)%gameboard.height):
                avoid_list.append(((opponent.y-i)%gameboard.height, opponent.x)) # go up
            else:
                wall_encountered[0] = True
            if not wall_encountered[1] and not gameboard.is_wall_at_tile(opponent.x, (opponent.y+i)%gameboard.height):
                avoid_list.append(((opponent.y+i)%gameboard.height, opponent.x)) # down
            else:
                wall_encountered[1] = True
            if not wall_encountered[2] and not gameboard.is_wall_at_tile((opponent.x+i)%gameboard.width, opponent.y):
                avoid_list.append((opponent.y, (opponent.x+i)%gameboard.width)) #right
            else:
                wall_encountered[2] = True
            if not wall_encountered[3] and not gameboard.is_wall_at_tile((opponent.x-i)%gameboard.width, opponent.y):
                avoid_list.append((opponent.y, (opponent.x-i)%gameboard.width)) #left
            else:
                wall_encountered[3] = True
        return avoid_list

    def getTurretFARC(self, gameboard):
        # Tiles affected by turrets firing
        # Calculates a list of lists (y,x)
        
        for b in gameboard.turrets:
            # Firing range of turret
            d = []
            hasWall = [False, False, False, False] 
            dbout("Checking turret: " + str(b.x) + " " + str(b.y))
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

    def TilesToAvoid(self, gameboard, player, opponent):
        # Checks if a tile is dangerous, given that tile argument is 
        # dictionary of form {"x":x, "y":y}
        avoid = []

        # Check for incoming turret fire
        for i, b in enumerate(gameboard.turrets):
            if b.is_firing_next_turn:
                avoid += [(k[1], k[0]) for k in self.tr_firingarc[i]] # Convert to (y,x)

        dbout("Turret tiles: " + str(avoid))

        # Check for incoming bullets
        for i, b in enumerate(gameboard.bullets):
            # Predict next position of all bullets
            dbout(str(i) + ":" + str(b.x) + "," + str(b.y) + "," + str(b.direction)+ "\t")
            if (b.direction == Direction.UP):
                avoid.append(((b.y-1)%gameboard.height, b.x))
            elif (b.direction == Direction.DOWN):
                avoid.append(((b.y+1)%gameboard.height, b.x))
            elif (b.direction == Direction.RIGHT):
                avoid.append((b.y, (b.x+1)%gameboard.width))
            elif (b.direction == Direction.LEFT):
                avoid.append((b.y, (b.x-1)%gameboard.width))

        avoid.append((opponent.y, opponent.x))
        if (player.y, player.x) in avoid:
            del avoid[avoid.index((player.y, player.x))]
        return avoid
                 
    def get_shortest_path(self, player, target, avoid):
        """
            avoid ([nodes]): nodes to temporarily avoid, (y,x)
        """
        temp_edge_storage = []
        if (target.y, target.x) in self.G.nodes():
            dbout("TARGET NODE EXISTS:")
            dbout(str(target.y) + "," + str(target.x))
        else:
            dbout("TARGET NODE DOES NOT EXIST")
            dbout(str(target.y) + "," + str(target.x))

        if (player.y, player.x) in self.G.nodes():
            dbout("PLAYER NODE EXISTS")
        else:
            dbout("PLAYER NODE DOES NOT EXIST")
        dbout("AVOID LIST:")
        dbout(avoid)
        temp_edge_storage = []
        path = []
        for node in avoid:
            neighbors = list(nx.all_neighbors(self.G, node))
            for neighbor in neighbors:
                self.G.remove_edge(node, neighbor)
            temp_edge_storage.extend([(node, neighbor) for neighbor in neighbors])
        try:
            path = nx.shortest_path(self.G, (player.y, player.x), (target.y, target.x))
        except:
            print("EXCEPTION: UNABLE TO FIND SHORTEST PATH")
        dbout("Restoring edges:")
        dbout(temp_edge_storage)        
        for edge in temp_edge_storage:
            self.G.add_edge(edge[0], edge[1])
        dbout("PATH FROM PLAYER TO TARGET GIVEN AVOID LIST:")
        dbout(path)
        return path

    def movement_direction(self, y1, x1, y2, x2, gameboard, player):
        cur_direction = player.direction
        if y1==y2:
            if (x2<x1 and not (x1==gameboard.width-1 and x2==0)) or (x1==0 and x2==gameboard.width-1):
                if cur_direction == Direction.LEFT:
                    return Move.FORWARD
                else:
                    return Move.FACE_LEFT
            elif (x2>x1 and not (x1==0 and x2==gameboard.width-1)) or (x1==gameboard.width-1 and x2==0):
                if cur_direction == Direction.RIGHT:
                    return Move.FORWARD
                else:
                    return Move.FACE_RIGHT
            else:
                return Move.NONE
        elif x1==x2:
            if (y2<y1 and not(y1==gameboard.height-1 and y2==0)) or (y1==0 and y2==gameboard.height-1):
                if cur_direction == Direction.UP:
                    return Move.FORWARD
                else:
                    return Move.FACE_UP
            elif (y2>y1 and not(y1==0 and y2==gameboard.height-1)) or (y1==gameboard.height-1 and y2==0):
                if cur_direction == Direction.DOWN:
                    return Move.FORWARD
                else:
                    return Move.FACE_DOWN
        else:
            return Move.NONE

    def generate_graph(self, gb): 
        G = nx.Graph()
        nodes = []
        for y in range(0, gb.height):
            for x in range(0, gb.width):
                G.add_node((y, x))        
                nodes.append((y, x))
        
        for i in range(0, gb.height): # for every row
            row_nodes = nodes[i*gb.width:(i+1)*gb.width]
            #dbout(str(row_nodes))
            G.add_edge(row_nodes[0], row_nodes[-1]) # connect from and last cell
            #dbout("connected: " + str(G.edges()[-1]))
            for j in range(0, gb.width-1):
                G.add_edge(row_nodes[j], row_nodes[j+1])    
                #dbout("connected: " + str(G.edges()[-1]))
                
        for i in range(0, gb.width): # for every column
            G.add_edge(nodes[i], nodes[(gb.height-1)*gb.width+i])
            #dbout("connected: " + str(G.edges()[-1]))
            for j in range(0, gb.height-1):
                G.add_edge(nodes[i+j*gb.width], nodes[i+(j+1)*gb.width])
                #dbout("connected: " + str(G.edges()[-1]))
        for wall in gb.walls:
            G.remove_node((wall.y, wall.x))
        for turret in gb.turrets:
            G.remove_node((turret.y, turret.x))
        self.G = G

    def get_move(self, gameboard, player, opponent):
        start = millitime()  
        dbout("")
        dbout("")
        dbout("")
        # Initialize bot params
        if gameboard.current_turn == 0:
            self.generate_graph(gameboard)
            dbout("graph generated!")
            #dbout(nx.shortest_path(self.G, (player.y, player.x), (pu.y, pu.x)))
            self.getTurretFARC(gameboard)
            dbout("Calculated turret firing arcs")
    
        if player.shield_count>0:
            return Move.SHIELD
    
        if player.laser_count>0 and self.should_fire_laser(gameboard, player, opponent):
            return Move.LASER
    
    
        # path = self.get_shortest_path(player, pu, [(6,1)])
        path = []        
        try:
            avoidance_list = self.TilesToAvoid(gameboard, player, opponent)
            if opponent.laser_count > 0:
                avoidance_list.extend(self.avoid_opponent_laser(gameboard, opponent))
            dbout(avoidance_list)
       
            to_avoid = []
            while True:
                path = self.closest_power_up(gameboard, player, to_avoid)
                if path[1] not in avoidance_list:
                    break
                to_avoid.append(path[1])
        except:
            print("EXCEPTION: UNABLE TO FIND PATH")
            dbout(self.G.edges())
            path = []
        
        # Debug for printing bullet specs
        # if len(gameboard.bullets) > 0:
        #     for i, b in enumerate(gameboard.bullets):
        #         dbout(str(i) + ":" + str(b.x) + "," + str(b.y) + "," + str(b.direction)+ "\t")
        
        end = millitime()
        print("Time elapsed:" + str(end - start))

        # Hardcode movements 
        # moves = [Move.SHOOT, Move.NONE]
        # self.i = self.i+1 if self.i<len(moves)-1 else len(moves)-1
        # return moves[self.i]

        dbout("Attempting to Follow path: ")
        dbout(path)
        if len(path)>1:
            next_move = self.movement_direction(path[0][0], path[0][1], path[1][0], path[1][1], gameboard, player)
            dbout("Move")            
            dbout(next_move)
            return next_move

        return Move.NONE

