import unittest

from PythonClientAPI.libs.Game.JSONParser import *


class ClientAPITest(unittest.TestCase):
    def setUp(self):
        file = open("TestMessage.json", "r")
        self.test_object = JSONParser(file.read())
        self.gameboard_object = self.test_object.gameboard
        self.player = self.test_object.player
        self.opponent = self.test_object.opponent

    def test_bullets_list_size(self):
        self.assertEqual(len(self.gameboard_object.bullets), 3)

    def test_wall_list_size(self):
        self.assertEqual(len(self.gameboard_object.walls), 1)

    def test_power_up_size(self):
        self.assertEqual(len(self.gameboard_object.power_ups), 2)

    def test_teleport_location_0(self):
        self.assertTrue(
            self.gameboard_object.teleport_locations[0][0] == 2 and self.gameboard_object.teleport_locations[0][1] == 1)

    def test_teleport_location_1(self):
        self.assertTrue(
            self.gameboard_object.teleport_locations[1][0] == 2 and self.gameboard_object.teleport_locations[1][1] == 2)

    def test_teleport_location_size(self):
        self.assertEqual(len(self.gameboard_object.teleport_locations), 2)

    def test_player_size(self):
        self.assertEqual(self.player.score, 2)

    def test_player_hp(self):
        self.assertEqual(self.player.hp, 2)

    def test_laser_count(self):
        self.assertEqual(self.player.laser_count, 2)

    def test_teleport_count(self):
        self.assertEquals(self.player.teleport_count, 1)

    def test_shield_count(self):
        self.assertEqual(self.player.shield_count, 0)

    def test_player_x(self):
        self.assertEqual(self.player.x, 1)

    def test_player_y(self):
        self.assertEqual(self.player.y, 2)

    def test_player_current_direction(self):
        self.assertEqual(self.player.direction, Direction.UP)

    def test_opponent_current_direction(self):
        self.assertEqual(self.opponent.direction, Direction.DOWN)

    def test_opponent_score(self):
        self.assertEqual(self.opponent.score, 5)

    def test_opponent_hp(self):
        self.assertEqual(self.opponent.hp, 2)

    def test_opponent_x(self):
        self.assertEqual(self.opponent.x, 2)

    def test_opponent_y(self):
        self.assertEqual(self.opponent.y, 1)

    def test_current_turn(self):
        self.assertEqual(self.gameboard_object.current_turn, 63)

    def test_turns_remaining(self):
        self.assertEqual(self.gameboard_object.get_turns_remaining(), 150 - 63)

    def test_width(self):
        self.assertEqual(self.gameboard_object.width, 3)

    def test_height(self):
        self.assertEqual(self.gameboard_object.height, 3)

    def test_size_coord_00(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[0][0]), 1)

    def test_type_coord_00(self):
        tested_object = self.gameboard_object.game_board_objects[0][0][0]
        self.assertTrue(isinstance(tested_object, PowerUp) and tested_object.power_up_type == PowerUpTypes.SHIELD)

    def test_size_coord_01(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[0][1]), 3)

    def test_type_coord_01(self):
        first_object = self.gameboard_object.game_board_objects[0][1][0]
        second_object = self.gameboard_object.game_board_objects[0][1][1]
        third_object = self.gameboard_object.game_board_objects[0][1][2]
        first = (isinstance(first_object, Bullet) or isinstance(first_object, PowerUp))
        second = (isinstance(second_object, Bullet) or isinstance(second_object, PowerUp))
        third = (isinstance(third_object, Bullet) or isinstance(third_object, PowerUp))
        self.assertTrue(first and second and third)

    def test_size_coord_02(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[0][2]), 1)

    def test_type_coord_02(self):
        test_object = self.gameboard_object.game_board_objects[0][2][0]
        self.assertTrue(isinstance(test_object, Bullet))
        self.assertEqual(test_object.shooter, self.player)
        self.assertEqual(test_object.direction, Direction.UP)

    def test_size_coord_10(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[1][0]), 1)

    def test_type_coord_10(self):
        self.assertTrue(isinstance(self.gameboard_object.game_board_objects[1][0][0], Wall))

    def test_size_coord_11(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[1][1]), 1)

    def test_type_coord_11(self):
        test_object = self.gameboard_object.game_board_objects[1][1][0]
        self.assertTrue(isinstance(test_object, Turret) and not test_object.is_firing_next_turn and test_object.fire_time == 1 and test_object.cooldown_time == 2)

    def test_size_coord_12(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[1][2]), 1)

    def test_type_coord_12(self):
        test_object = self.gameboard_object.game_board_objects[1][2][0]
        self.assertTrue(isinstance(test_object, Player) and test_object == self.player)

    def test_size_coord_20(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[2][0]), 1)

    def test_type_coord_20(self):
        test_object = self.gameboard_object.game_board_objects[2][0][0]
        self.assertTrue(isinstance(test_object, Turret) and test_object.is_firing_next_turn and test_object.fire_time == 2 and test_object.cooldown_time == 4)

    def test_coord_21(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[2][1]), 0)

    def test_size_coord_22(self):
        self.assertEqual(len(self.gameboard_object.game_board_objects[2][2]), 1)

    def test_type_coord_22(self):
        test_object = self.gameboard_object.game_board_objects[2][2][0]
        self.assertTrue(isinstance(test_object, Opponent) and test_object == self.opponent)

    def test_does_bullets_exist_at(self):
        self.assertTrue(
            self.gameboard_object.are_bullets_at_tile(0, 1) and not self.gameboard_object.are_bullets_at_tile(
                2, 2))

    def test_size_of_bullets_at_tile(self):
        self.assertEqual(len(self.gameboard_object.bullets_at_tile[0][1]), 2)

    def test_size_shooter(self):
        test_object = self.gameboard_object.bullets_at_tile[0][1][0]
        assert (test_object.shooter == self.opponent)

    def test_does_turret_exists_at(self):
        self.assertTrue(
            self.gameboard_object.is_turret_at_tile(2,
                                                    0) and not self.gameboard_object.is_turret_at_tile(
                0, 0))

    def test_does_power_up_exist_at(self):
        self.assertTrue(self.gameboard_object.is_power_up_at_tile(0,
                                                                  0) and not self.gameboard_object.is_power_up_at_tile(
            2, 1))

    def test_does_wall_exist_at(self):
        self.assertTrue(
            self.gameboard_object.is_wall_at_tile(1, 0) and not self.gameboard_object.is_wall_at_tile(2,
                                                                                                      1))

    def test_get_turret_at_tile(self):
        self.assertTrue(self.gameboard_object.turret_at_tile[2][0].is_firing_next_turn)

    def test_get_power_up_at_tile(self):
        self.assertEqual(self.gameboard_object.power_up_at_tile[0][0].power_up_type, PowerUpTypes.SHIELD)

    def test_size_teleport_locations(self):
        self.assertEqual(len(self.gameboard_object.teleport_locations), 2)

    def test_did_make_a_move_last_turn(self):
        self.assertTrue(self.player.did_make_a_move)

    def test_size_projectile_types(self):
        self.assertEqual(len(self.player.projectiles), 3)

    def test_size_shooter(self):
        self.assertEqual(len(self.player.shooters), 3)

    def test_get_projectile_object(self):
        array = self.player.projectiles
        self.assertEqual(array[0], ProjectileTypes.LASER)
        self.assertEqual(array[1], ProjectileTypes.BULLET)
        self.assertEqual(array[2], ProjectileTypes.LASER)

    def test_get_shooter_object(self):
        array = self.player.shooters
        self.assertEqual(array[0], self.opponent)
        self.assertTrue(array[1] == self.player)
        self.assertEqual(array[2], None)

    def test_get_last_move(self):
        self.assertEqual(self.opponent.last_move, Move.FACE_LEFT)

    def test_was_shield_active_player(self):
        self.assertTrue(self.player.shield_active)
        self.assertFalse(self.opponent.shield_active)

    def test_opponent_shield_count(self):
        self.assertEqual(self.opponent.shield_count, 0)

    def test_opponent_teleport_count(self):
        self.assertEqual(self.opponent.teleport_count, 1)

    def test_opponent_laser_count(self):
        self.assertEqual(self.opponent.laser_count, 2)


if __name__ == '__main__':
    unittest.main()
