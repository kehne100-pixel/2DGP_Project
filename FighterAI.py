# fighter_ai.py
import random
import game_framework

from sdl2 import (
    SDL_KEYDOWN, SDL_KEYUP,
    SDLK_RIGHT, SDLK_LEFT,
    SDLK_a, SDLK_s, SDLK_d,
    SDLK_1, SDLK_2, SDLK_3,
)


class DummyEvent:
    def __init__(self, type, key):
        self.type = type
        self.key = key


class FighterAI:
    def __init__(self, enemy, player):

        self.enemy = enemy
        self.player = player

        # 이동 상태 관리
        self.current_move_key = None  # SDLK_RIGHT / SDLK_LEFT / None

        # 가드 상태 관리
        self.guard_active = False
        self.guard_timer = 0.0

        # 의사결정 쿨타임
        self.decision_timer = 0.0

        # 공격1/공격2 번갈아 사용
        self.use_attack1_next = True

        # 거리 기준 (상황에 맞게 나중에 조정 가능)
        self.APPROACH_DISTANCE = 350   # 이보다 멀면 접근
        self.CLOSE_RANGE       = 150   # 근접 공격/스킬1,2 사용 거리
        self.SKILL3_RANGE      = 300   # 필살기 스킬3은 좀 더 먼 거리에서도 사용



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

