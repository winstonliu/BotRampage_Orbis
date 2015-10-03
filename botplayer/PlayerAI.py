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
        path = self.get_shortest_path(player, opponent)
        moves = [self.movement_direction(path[i], path[i+1]) for i in range(0, len(path)-1)]
        
        if len(path)<4:
            return True
        return False

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

    def TilesToAvoid(self, gameboard, opponent):
        # Checks if a tile is dangerous, given that tile argument is 
        # dictionary of form {"x":x, "y":y}
        avoid = []

        # Check for incoming turret fire
        for i, b in enumerate(gameboard.turrets):
            if b.is_firing_next_turn:
                avoid += [(k[1], k[0]) for k in self.tr_firingarc[i]] # Convert to (y,x)

        dbout("Turret tiles: " + str(self.tr_firingarc))
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
        dbout("Tiles to avoid: " + str(avoid))
        return avoid
                 
    def get_shortest_path(self, player, target, avoid):
        """
            avoid ([nodes]): nodes to temporarily avoid, (y,x)
        """
        temp_edge_storage = []
        for node in avoid:
            neighbors = list(nx.all_neighbors(self.G, node))         
            for neighbor in neighbors:
                self.G.remove_edge(node, neighbor)
            temp_edge_storage = [(node, neighbor) for neighbor in neighbors]
        path = nx.shortest_path(self.G, (player.y, player.x), (target.y, target.x))
        for edge in temp_edge_storage:
            self.G.add_edge(edge[0], edge[1])
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
        pu = gameboard.power_ups[0]        

        dbout("Width: " + str(gameboard.width) + " Height: " + str(gameboard.height))

        # Initialize bot params
        if gameboard.current_turn == 0:
            self.generate_graph(gameboard)
            dbout("graph generated!")
            dbout("Going for: " + str(pu.y) + ", " + str(pu.x))
            dbout("Starting at: " + str(player.y) + ", " + str(player.x))
            #dbout(nx.shortest_path(self.G, (player.y, player.x), (pu.y, pu.x)))
            self.getTurretFARC(gameboard)
            dbout("Calculated turret firing arcs")
    
        # path = self.get_shortest_path(player, pu, [(6,1)])
        avoidance_list = self.TilesToAvoid(gameboard, opponent)
        dbout(avoidance_list)
        path = self.get_shortest_path(player, pu, avoidance_list)
        dbout(path)

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

        if len(path)>1:
            next_move = self.movement_direction(path[0][0], path[0][1], path[1][0], path[1][1], gameboard, player)
            dbout(next_move)
            return next_move

        return Move.NONE

