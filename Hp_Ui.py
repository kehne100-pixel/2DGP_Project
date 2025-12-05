# hp_ui.py
from pico2d import *

class HPBar:
    def __init__(self, x, y, width, height, max_hp,


    def set_hp(self, hp):


    def damage(self, value):


    def heal(self, value):


    def draw(self):


class BattleUI:

    def __init__(self, player_max_hp=100, enemy_max_hp=100):





    def set_player_hp(self, hp):


    def set_enemy_hp(self, hp):


    def damage_player(self, value):


    def damage_enemy(self, value):


    def draw(self):

