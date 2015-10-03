import json

from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.GameObjects import *
from PythonClientAPI.libs.Game.GameBoard import *


class JSONParser:
    def __init__(self, JSON_string):
        self.JSON_string = JSON_string
        self.JSON_object = json.loads(JSON_string)
        self.JSON_board = self.JSON_object['gameboard']
        self.initialize_player()
        self.initialize_opponent()
        self.initialize_gameboard()
        self.populate_shooters()

    def initialize_gameboard(self):
        current_turn = self.JSON_object['currentTurn']
        max_turn = self.JSON_object['maxTurn']
        self.width = self.JSON_board['width']
        self.height = self.JSON_board['height']
        self.gameboard = Gameboard(self.width, self.height, current_turn, max_turn)
        self.populate_gameboard()
        self.add_teleport_locations()

    def populate_gameboard(self):
        for x in range(self.width):
            for y in range(self.height):
                self.current_square = self.JSON_board['board'][x][y]
                # Makes these field variables so other methods can use
                self.x = x
                self.y = y
                if "wall" in self.current_square:
                    self.add_wall()
                elif "turret" in self.current_square:
                    self.check_and_add_turret()
                elif "player" in self.current_square:
                    self.check_and_add_player()
                else:
                    if "powerUp" in self.current_square:
                        self.check_and_add_power_up()
                    if "bullets" in self.current_square:
                        self.check_and_add_bullets()

    def initialize_player(self):
        player_JSON = self.JSON_object['player']
        self.player_ID = self.JSON_object['playerID']
        player_x = player_JSON['x']
        player_y = player_JSON['y']
        player_direction = Direction[player_JSON['currentDirection']]
        hp = player_JSON['HP']
        score = player_JSON['score']
        power_ups = player_JSON['numberOfPowerUps']
        laser_count = power_ups['laser']
        teleport_count = power_ups['teleport']
        shield_count = power_ups['shield']
        did_make_a_move = self.JSON_object['didMakeAMove']
        shield_active = player_JSON['shieldActive']
        self.shooters = []
        self.projectiles = []
        self.player = Player(player_x, player_y, player_direction, score, hp, laser_count, teleport_count, shield_count,
                             did_make_a_move, self.projectiles, self.shooters, shield_active)

    def initialize_opponent(self):
        opponent_JSON = self.JSON_object['opponent']
        self.opponent_ID = self.JSON_object['opponentID']
        opponent_x = opponent_JSON['x']
        opponent_y = opponent_JSON['y']
        opponent_direction = Direction[opponent_JSON['currentDirection']]
        hp = opponent_JSON['HP']
        score = opponent_JSON['score']
        last_move = Move[opponent_JSON['opponentLastMove']]
        shield_active = opponent_JSON['shieldActive']
        power_ups = opponent_JSON['numberOfPowerUps']
        laser_count = power_ups['laser']
        teleport_count = power_ups['teleport']
        shield_count = power_ups['shield']
        self.opponent = Opponent(opponent_x, opponent_y, opponent_direction, score, hp, shield_active, last_move,
                                 laser_count, teleport_count, shield_count)

    def add_teleport_locations(self):
        teleport_locations = self.JSON_object['teleportLocations']
        self.gameboard.teleport_locations = teleport_locations

    def add_wall(self):
        wall = Wall(self.x, self.y)
        self.gameboard.walls.append(wall)
        self.gameboard.wall_at_tile[self.x][self.y] = wall
        self.gameboard.game_board_objects[self.x][self.y].append(wall)

    def check_and_add_turret(self):
        turret_JSON = self.current_square['turret']
        is_firing_next_turn = turret_JSON['isFiringNextTurn']
        is_dead = turret_JSON['isDead']
        did_fire = turret_JSON['didFire']
        fire_time = turret_JSON['fireTime']
        cooldown_time = turret_JSON['cooldownTime']
        turret = Turret(self.x, self.y, is_firing_next_turn, is_dead, did_fire, fire_time, cooldown_time)
        self.gameboard.game_board_objects[self.x][self.y].append(turret)
        self.gameboard.turret_at_tile[self.x][self.y] = turret
        self.gameboard.turrets.append(turret)

    def check_and_add_player(self):
        # appends player to the x,y if the id is the same otherwise it appends the opponent
        self.gameboard.game_board_objects[self.x][self.y].append(
            self.player if self.player_ID == self.current_square['player'] else self.opponent)

    def check_and_add_power_up(self):
        power_up = None
        power_up_type_string = self.current_square['powerUp']
        if power_up_type_string == "SHIELD":
            power_up = PowerUp(self.x, self.y, PowerUpTypes.SHIELD)
        if power_up_type_string == "TELEPORT":
            power_up = PowerUp(self.x, self.y, PowerUpTypes.TELEPORT)
        if power_up_type_string == "LASER":
            power_up = PowerUp(self.x, self.y, PowerUpTypes.LASER)
        if power_up is not None:
            self.gameboard.power_up_at_tile[self.x][self.y] = power_up
            self.gameboard.power_ups.append(power_up)
            self.gameboard.game_board_objects[self.x][self.y].append(power_up)

    def check_and_add_bullets(self):
        bullet_array = self.current_square['bullets']
        for i in bullet_array:
            player_id = i['player']
            direction = Direction[i['currentDirection']]
            player_to_add = self.player if (player_id == self.player_ID) else self.opponent
            bullet = Bullet(self.x, self.y, direction, player_to_add)
            self.gameboard.bullets.append(bullet)
            self.gameboard.bullets_at_tile[self.x][self.y].append(bullet)
            self.gameboard.game_board_objects[self.x][self.y].append(bullet)

    def populate_shooters(self):
        hit_by_array = self.JSON_object['wasHitByLastTurn']
        for i in hit_by_array:
            self.projectiles.append(ProjectileTypes[i['type']])
            if 'shooter' in i:
                self.shooters.append(self.player if self.player_ID == i['shooter'] else self.opponent)
            else:
                self.shooters.append(None)
