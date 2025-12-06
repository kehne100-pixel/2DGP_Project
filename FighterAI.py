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

    # ---------- 메인 업데이트 ----------

    def update(self):
        dt = game_framework.frame_time

        # 가드 유지 시간 관리
        if self.guard_active:
            self.guard_timer -= dt
            if self.guard_timer <= 0:
                self._stop_guard()

        # 의사결정 쿨타임 관리
        if self.decision_timer > 0:
            self.decision_timer -= dt
            return  # 아직 다음 행동 결정할 시간이 아님

        # 플레이어와의 거리 계산
        dist = abs(self.player.x - self.enemy.x)
        # 플레이어가 오른쪽이면 +1, 왼쪽이면 -1
        direction = 1 if (self.player.x > self.enemy.x) else -1

        # HP / MP 정보 (없으면 기본값으로 처리)
        hp      = getattr(self.enemy, 'hp', 100)
        max_hp  = getattr(self.enemy, 'max_hp', 100)
        mp      = getattr(self.enemy, 'mp', 0)
        max_mp  = getattr(self.enemy, 'max_mp', 100)

        hp_ratio = hp / max_hp if max_hp > 0 else 1.0
        mp_full  = (max_mp > 0 and mp >= max_mp)  # "마나가 가득 찼다"는 기준

        # ----------------- 행동 우선순위 로직 -----------------
        # 1) 거리가 멀면 접근
        if dist > self.APPROACH_DISTANCE:
            self._start_move(direction)
            self.decision_timer = 0.2     # 자주 방향 재확인
            return

        # 2) 가까운 거리: 공격 / 가드 / 스킬 결정
        #    - 초반: 공격과 가드 반반
        #    - 체력 30% 이하: 가드 비율 증가 + 스킬 기회 있으면 활용
        if hp_ratio > 0.3:
            # Normal: 공격/가드 50:50 + 가끔 스킬
            guard_prob = 0.5
            skill_prob = 0.15   # 마나 풀일 때에만 의미 있음
        else:
            # 체력 30% 이하: 가드 늘리고 공격 줄이기
            guard_prob = 0.65
            skill_prob = 0.20

        r = random.random()

        # 2-1) 스킬 사용 우선 (마나 가득 찼을 때만)
        if mp_full:
            # 스킬3: 필살기, 거리가 좀 떨어져 있어도 맞도록
            if dist <= self.SKILL3_RANGE and r < skill_prob:
                self._do_skill3()
                self.decision_timer = 1.0
                return

            # 스킬1,2: 근접일 때
            if dist <= self.CLOSE_RANGE and r < skill_prob:
                if random.random() < 0.5:
                    self._do_skill1()
                else:
                    self._do_skill2()
                self.decision_timer = 0.9
                return

        # 2-2) 가드 / 공격 결정
        r2 = random.random()

        # 가드는 랜덤하게 가끔 막기 (위에서 guard_prob로 비율 조정)
        if r2 < guard_prob:
            # 약 1초 정도 가드 유지
            self._start_guard(duration=1.0)
            self.decision_timer = 1.0
            return
        else:
            # 공격1,2 번갈아 사용
            if dist <= self.CLOSE_RANGE:
                if self.use_attack1_next:
                    self._do_attack1()
                else:
                    self._do_attack2()
                self.decision_timer = 0.6
                return
            else:
                # 거리가 애매하면 조금 더 접근
                self._start_move(direction)
                self.decision_timer = 0.2
                return
