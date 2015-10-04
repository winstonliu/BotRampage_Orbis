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

def dbout2(a):
    # print(a)
    pass

class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        self.i = -1;
        self.dieTurrets = None
        self.none_counter = 0;
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

    def avoid_opponent_fire(self, gameboard, opponent):
        avoid_list = []
        isWall = [False, False, False, False]
        for i in range(1, 4):
            if not isWall[0] and not gameboard.is_wall_at_tile(opponent.x, (opponent.y-i)%gameboard.height):
                if opponent.laser_count > 0:
                    avoid_list.append(((opponent.y-i)%gameboard.height, opponent.x)) # go up
                elif opponent.direction == Direction.UP and i < 3:
                    avoid_list.append(((opponent.y-i)%gameboard.height, opponent.x)) # go up
            else:
                isWall[0] = True
            if not isWall[1] and not gameboard.is_wall_at_tile(opponent.x, (opponent.y+i)%gameboard.height):
                if opponent.laser_count > 0: 
                    avoid_list.append(((opponent.y+i)%gameboard.height, opponent.x)) # down
                elif opponent.direction == Direction.DOWN and i < 3:
                    avoid_list.append(((opponent.y+i)%gameboard.height, opponent.x)) # down
            else:
                isWall[1] = True
            if not isWall[2] and not gameboard.is_wall_at_tile((opponent.x+i)%gameboard.width, opponent.y):
                if opponent.laser_count > 0: 
                    avoid_list.append((opponent.y, (opponent.x+i)%gameboard.width)) #right
                elif opponent.direction == Direction.RIGHT and i < 3:
                    avoid_list.append((opponent.y, (opponent.x+i)%gameboard.width)) #right
            else:
                isWall[2] = True
            if not isWall[3] and not gameboard.is_wall_at_tile((opponent.x-i)%gameboard.width, opponent.y):
                if opponent.laser_count > 0: 
                    avoid_list.append((opponent.y, (opponent.x-i)%gameboard.width)) #left
                elif opponent.direction == Direction.LEFT and i < 3:
                    avoid_list.append((opponent.y, (opponent.x-i)%gameboard.width)) #left
            else:
                isWall[3] = True
        avoid_list.append((opponent.y, opponent.x))
        return avoid_list

    def TilesToAvoid(self, gameboard, player, opponent):
        # Checks if a tile is dangerous, given that tile argument is 
        # dictionary of form {"x":x, "y":y}
        avoid = []

        # Check for incoming turret fire
        avoid += self.dieTurrets.buildAvoidanceListYX(gameboard)

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
        
    def single_source_shortest_path(self, player, avoid):
        """
            avoid ([nodes]): nodes to temporarily avoid, (y,x)
        """
        temp_edge_storage = []
        dbout("AVOID LIST:")
        dbout(avoid)
        temp_edge_storage = []
        paths = []
        for node in avoid:
            neighbors = list(nx.all_neighbors(self.G, node))
            for neighbor in neighbors:
                self.G.remove_edge(node, neighbor)
            temp_edge_storage.extend([(node, neighbor) for neighbor in neighbors])
        try:
            paths = nx.single_source_shortest_path(self.G, (player.y, player.x), cutoff=10)
            paths = list(paths.values())
            del paths[0]            
        except:
            dbout("EXCEPTION: UNABLE TO FIND SHORTEST PATH")
        for edge in temp_edge_storage:
            self.G.add_edge(edge[0], edge[1])
        dbout("PATH FROM PLAYER TO TARGET GIVEN AVOID LIST:")
        dbout(paths)
        return paths

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
    
    def path_to_enemy(self, gameboard, player, opponent, avoid):
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
        paths = [self.get_shortest_path(player, GameObject(end_node[1], end_node[0]), avoid) for end_node in end_nodes]
        if len(paths)==0:
            return []
        return paths[self.argmin([len(path) for path in paths])]        
        
    def enemy_is_pointed_toward_us(self, gameboard, opponent, path_to_opponent):
        mmove = self.movement_direction(list(reversed(path_to_opponent)), gameboard, opponent)
        if mmove == Move.FORWARD:
            return True
        return False
        
    def num_moves_to_execute_path(self, path, gameboard, player):
        num_moves = 0
        for i in range(0, len(path)-1):
            mmove = self.movement_direction(path[i::], gameboard, player)
            if mmove==Move.FORWARD:
                num_moves = num_moves+1
            else:
                num_moves = num_moves+2 # requires rotation and movement
        return num_moves
    
    def path_to_next_safest_spot(self, gameboard, player, opponent, avoid):
        if (player.y, player.x) in avoid:
            avoid.remove((player.y, player.x))
        paths = self.single_source_shortest_path(player, avoid)
        path_lengths = []
        for path in paths:
            dbout("111111111111111")
            dbout(path)
            if len(path) <= 1:
                continue
            path_lengths.append(self.num_moves_to_execute_path(path, gameboard, player))
        return paths[self.argmin(path_lengths)], self.argmin(path_lengths)
    
    def get_move(self, gameboard, player, opponent):
        start = millitime()  

        dbout2("##### Turn: " + str(gameboard.current_turn) + " #####")
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

        if player.laser_count>0 and self.should_fire_laser(gameboard, player, opponent):
             return Move.LASER

        # Winston, add turrets etc to this avoid list
        avoid_list = self.avoid_opponent_fire(gameboard, opponent)
        avoid_list += self.TilesToAvoid(gameboard, player, opponent)
        if (player.y, player.x) in avoid_list:
            path, nmoves = self.path_to_next_safest_spot(gameboard, player, opponent, avoid_list)
            if nmoves == 1:
                return self.movement_direction(path, gameboard, player)
        else:
            pass
        
        yesno, path = self.opponent_is_in_los(gameboard, player, opponent)
        if yesno:
            mmove = self.movement_direction(path, gameboard, player)
            if mmove == Move.FORWARD:
                return Move.SHOOT
            return mmove
            
        path = []        
        try:
            if opponent.laser_count > 0:
                avoid_list.extend(self.avoid_opponent_laser(gameboard, opponent))
            dbout(avoid_list)

            if (player.y, player.x) in avoid_list and player.shield_count > 0:
               return Move.SHIELD
            elif player.teleport_count > 0:
               return Move.TELEPORT

            to_avoid = []
            while True:
                if len(gameboard.power_ups) > 0:
                    path = self.closest_power_up(gameboard, player, to_avoid)
                else:
                    path = self.path_to_enemy(gameboard, player, opponent, to_avoid)

                if path[1] not in avoid_list:
                    break
                to_avoid.append(path[1])
        except:
            dbout("EXCEPTION: UNABLE TO FIND PATH")
            dbout(self.G.edges())
            path = []
            if ((player.y, player.x) in avoid_list and self.movement_direction(path, gameboard, player) != Move.FORWARD):
                if player.shield_count > 0:
                    return Move.SHIELD
                elif player.teleport_count > 0:
                    return Move.TELEPORT
        
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
        if (self.none_counter > 3):
            return Move.LEFT

        if len(path)>1:
            next_move = self.movement_direction(path, gameboard, player)
            if next_move == Move.NONE:
                ++self.none_counter;
            return next_move

        ++self.none_counter;
        return Move.NONE
