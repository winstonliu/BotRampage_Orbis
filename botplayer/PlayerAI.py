from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *
from networkx import nx

class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        pass

    def get_move(self, gameboard, player, opponent):
        from time import time
        pu = gameboard.power_ups[1]        
        if gameboard.current_turn == 0:
            self.generate_graph(gameboard)
            print("graph generated!")
            print("Going for: " + str(pu.y) + ", " + str(pu.x))
            print("Starting at: " + str(player.y) + ", " + str(player.x))
            #print(nx.shortest_path(self.G, (player.y, player.x), (pu.y, pu.x)))

        path = self.get_shortest_path(player, pu, [(6,1)])
        print(path)
        if len(path)>1:
            start = time()
            next_move = self.movement_direction(path[0][0], path[0][1], path[1][0], path[1][1], gameboard, player)
            print(next_move)
            print(time()*1000-start*1000)            
            return next_move
        return Move.NONE
        
    def should_fire_laser(self, gameboard, player, opponent):
        path = self.get_shortest_path(player, opponent)
        moves = [self.movement_direction(path[i], path[i+1]) for i in range(0, len(path)-1)]
        
        if len(path)<4:
            return True
        return False
    
    def get_shortest_path(self, player, target, avoid):
        """
            avoid ([nodes]): nodes to temporarily avoid
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
            #print(str(row_nodes))
            G.add_edge(row_nodes[0], row_nodes[-1]) # connect from and last cell
            #print("connected: " + str(G.edges()[-1]))
            for j in range(0, gb.width-1):
                G.add_edge(row_nodes[j], row_nodes[j+1])    
                #print("connected: " + str(G.edges()[-1]))
                
        for i in range(0, gb.width): # for every column
            G.add_edge(nodes[i], nodes[(gb.height-1)*gb.width+i])
            #print("connected: " + str(G.edges()[-1]))
            for j in range(0, gb.height-1):
                G.add_edge(nodes[i+j*gb.width], nodes[i+(j+1)*gb.width])
                #print("connected: " + str(G.edges()[-1]))
        for wall in gb.walls:
            G.remove_node((wall.y, wall.x))
        for turret in gb.turrets:
            G.remove_node((turret.y, turret.x))
        self.G = G