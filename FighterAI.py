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
        self.type = type
        self.key = key


class FighterAI:
    def __init__(self, enemy, player):
        """
        enemy : AI가 조종할 캐릭터 (Dororo, Keroro, Tamama, Giroro, Kururu 중 하나)
        player: 인간이 조종하는 캐릭터
        """
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

    # ---------- 내부 유틸 함수들 ----------

    def _send_keydown(self, key):
        ev = DummyEvent(SDL_KEYDOWN, key)
        self.enemy.handle_event(ev)

    def _send_keyup(self, key):
        ev = DummyEvent(SDL_KEYUP, key)
        self.enemy.handle_event(ev)

    def _start_move(self, direction):
        """direction: +1 (오른쪽으로), -1 (왼쪽으로)"""
        # 먼저 기존 이동키 해제
        if self.current_move_key is not None:
            self._send_keyup(self.current_move_key)
            self.current_move_key = None

        # 새 방향으로 키 누르기
        if direction > 0:
            self.current_move_key = SDLK_RIGHT
        else:
            self.current_move_key = SDLK_LEFT

        self._send_keydown(self.current_move_key)

    def _stop_move(self):
        if self.current_move_key is not None:
            self._send_keyup(self.current_move_key)
            self.current_move_key = None

    def _start_guard(self, duration=1.0):
        """가드 시작 (약 1초 유지)"""
        if self.guard_active:
            return

        self.guard_active = True
        self.guard_timer = duration
        self._stop_move()              # 가드 시작할 땐 이동 멈춤
        self._send_keydown(SDLK_a)     # 가드 키 누르기

    def _stop_guard(self):
        if not self.guard_active:
            return

        self.guard_active = False
        self._send_keyup(SDLK_a)       # 가드 키 떼기

    def _do_attack1(self):
        self._stop_move()
        self._send_keydown(SDLK_s)     # Attack1
        self.use_attack1_next = False  # 다음엔 Attack2 사용

    def _do_attack2(self):
        self._stop_move()
        self._send_keydown(SDLK_d)     # Attack2
        self.use_attack1_next = True   # 다음엔 Attack1 사용

    def _do_skill1(self):
        self._stop_move()
        self._send_keydown(SDLK_1)

    def _do_skill2(self):
        self._stop_move()
        self._send_keydown(SDLK_2)

    def _do_skill3(self):
        self._stop_move()
        self._send_keydown(SDLK_3)

    def update(self):


