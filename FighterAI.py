# fighter_ai.py
import random
import game_framework

from sdl2 import (
    SDL_KEYDOWN, SDL_KEYUP,
    SDLK_RIGHT, SDLK_LEFT,
    SDLK_a, SDLK_s, SDLK_d,
    SDLK_1, SDLK_2, SDLK_3,
)

# 아주 단순한 더미 이벤트 객체 (키보드 이벤트 흉내내기용)
class DummyEvent:
    def __init__(self, type, key):



class FighterAI:
    def __init__(self, enemy, player):




    def _send_keydown(self, key):


    def _send_keyup(self, key):


    def _start_move(self, direction):


    def _stop_move(self):


    def _start_guard(self, duration=1.0):


    def _stop_guard(self):


    def _do_attack1(self):


    def _do_attack2(self):


    def _do_skill1(self):


    def _do_skill2(self):


    def _do_skill3(self):


    # ---------- 메인 업데이트 ----------

    def update(self):
