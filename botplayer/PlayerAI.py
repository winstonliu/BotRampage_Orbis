import time

from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.GameObjects import GameObject
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *
from TurretHunter import TurretHunter
from networkx import nx

millitime = lambda: int(round(time.time() * 1000))

def dbout(a):
    # Debug printout
    # print(a)
    pass

def turretFARC(a):
    # print(a)
    pass

class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        self.i = -1;
        self.dieTurrets = None
        pass
        
    def should_fire_laser(self, gameboard, player, opponent):
        path = self.get_shortest_path(player, opponent, [])
        if len(path)<=5 and (player.x==opponent.x or player.y==opponent.y):
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

    def opponent_is_in_los(self, gameboard, player, opponent):
        if opponent.x==player.x or opponent.y==player.y:
            path = self.get_shortest_path(player, opponent, [])
            if self.is_direct_path(path):
                return True, path
        return False, []

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


    def TilesToAvoid(self, gameboard, player, opponent):
        # Checks if a tile is dangerous, given that tile argument is 
        # dictionary of form {"x":x, "y":y}
        avoid = []

        # Check for incoming turret fire
        avoid += self.dieTurrets.buildAvoidanceListYX(gameboard)

        turretFARC("Turret tiles: " + str(avoid))

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
        return avoid
                 
    def get_shortest_path(self, player, target, avoid):
        """
            avoid ([nodes]): nodes to temporarily avoid, (y,x)
        """
        temp_edge_storage = []
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
            dbout("EXCEPTION: UNABLE TO FIND SHORTEST PATH")
        for edge in temp_edge_storage:
            self.G.add_edge(edge[0], edge[1])
        dbout("PATH FROM PLAYER TO TARGET GIVEN AVOID LIST:")
        dbout(path)
        return path

    def movement_direction(self, path, gameboard, player):
        y1 = path[0][0]        
        x1 = path[0][1]
        y2 = path[1][0]
        x2 = path[1][1]
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
        
    def is_direct_path(self, path):
        sety = set([node[0] for node in path])
        if len(sety)==1:
            return True
        setx = set([node[1] for node in path])
        if len(setx)==1:
            return True
        return False
        
    def argmin(self, mlist):
        minval = mlist[0]
        minindex = 0
        for i in range(1, len(mlist)):
            if mlist[i] < minval:
                minval = mlist[i]
                minindex = i
        return minindex
    
    def path_to_enemy(self, gameboard, player, opponent):
        end_nodes = list(nx.all_neighbors(self.G, (opponent.y, opponent.x)))
        opp_front_node = None
        if opponent.direction == Direction.UP:
            opp_front_node = (opponent.y-1, opponent.x)
        if opponent.direction == Direction.DOWN:
            opp_front_node = (opponent.y+1, opponent.x)
        if opponent.direction == Direction.RIGHT:
            opp_front_node = (opponent.y, opponent.x+1)
        if opponent.direction == Direction.LEFT:
            opp_front_node = (opponent.y, opponent.x-1)
        if opp_front_node in end_nodes:
            end_nodes.remove(opp_front_node)
        dbout((player.y, player.x))
        for end_node in end_nodes:
            dbout(end_node)
        paths = [self.get_shortest_path(player, GameObject(end_node[1], end_node[0]), []) for end_node in end_nodes]
        if len(paths)==0:
            return []
        return paths[self.argmin([len(path) for path in paths])]        
        
    def get_move(self, gameboard, player, opponent):
        start = millitime()  

        turretFARC("##### Turn: " + str(gameboard.current_turn) + " #####")
        dbout("")
        dbout("")
        # Initialize bot params
        if gameboard.current_turn == 0:
            self.dieTurrets = TurretHunter()
            self.generate_graph(gameboard)
            dbout("graph generated!")
            #dbout(nx.shortest_path(self.G, (player.y, player.x), (pu.y, pu.x)))
            self.dieTurrets.getTurretFARC(gameboard)
            dbout("Calculated turret firing arcs")
        
        # Update turret list to check for dead turrets
        self.dieTurrets.updateTurretList(gameboard)

        los, path = self.opponent_is_in_los(gameboard, player, opponent)
        if los==True:
            dbout("ENEMY IN LOS")
            mmove = self.movement_direction(path, gameboard, player)
            if mmove == Move.FORWARD:
                return Move.SHOOT
            else:
                return mmove
        else:
            dbout("ENEMY NOT IN LOS")
    
        # if player.shield_count>0:
        #     return Move.SHIELD
    
        if player.laser_count>0 and self.should_fire_laser(gameboard, player, opponent):
            return Move.LASER
    
        # path = self.get_shortest_path(player, pu, [(6,1)])
        path = []        
        avoidance_list = self.TilesToAvoid(gameboard, player, opponent)
        try:
            if opponent.laser_count > 0:
                avoidance_list.extend(self.avoid_opponent_laser(gameboard, opponent))
            dbout(avoidance_list)

            if (player.y, player.x) in avoidance_list and player.shield_count > 0:
               return Move.SHIELD
       
            to_avoid = []
            while True:
                path = self.closest_power_up(gameboard, player, to_avoid)
                if path[1] not in avoidance_list:
                    break
                to_avoid.append(path[1])
        except:
            dbout("EXCEPTION: UNABLE TO FIND PATH")
            dbout(self.G.edges())
            path = []
            if (player.y, player.x) in avoidance_list and player.shield_count > 0:
                return Move.SHIELD
       
        
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
            next_move = self.movement_direction(path, gameboard, player)
            return next_move

        return Move.NONE
