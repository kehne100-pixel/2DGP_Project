from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a, SDLK_s, SDLK_d
import game_framework
from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def s_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s
def d_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def Time_out(e):   return e[0] == 'TIME_OUT'
def attack_done_idle(e): return e[0] == 'ATTACK_DONE_IDLE'
def attack_done_run(e):  return e[0] == 'ATTACK_DONE_RUN'



IMAGE_W, IMAGE_H = 996, 1917
CELL_W, CELL_H   = 40, 80
DRAW_W, DRAW_H   = 130, 130


def row_y_from_top(row_from_top):
    return IMAGE_H - (row_from_top + 1) * CELL_H



SPRITE = {
    'idle': {
        'rects': [
            (4,   1842, 60, 60),
            (67,  1842, 60, 60),
            (132, 1842, 60, 60),
            (198, 1842, 60, 60),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'run': {
        'rects': [
            (4,   1544, 60, 60),
            (67,  1544, 60, 60),
            (132, 1544, 60, 60),
            (198, 1544, 60, 60),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'attack': {
        'rects': [
            (4,   1228, 61, 80),
            (65,  1228, 61, 80),
            (138, 1228, 61, 80),
        ],
        'frames': 3,
        'flip_when_left': True
    },


    'attack2': {
        'rects': [
            (207, 1223, 60, 57),
            (295, 1223, 74, 47),
            (383, 1223, 74, 48),


        ],
        'frames': 3,
        'flip_when_left': True
    },
}




def draw_from_cfg(image, key, frame_idx, face_dir, x, y, draw_w=DRAW_W, draw_h=DRAW_H):
    cfg = SPRITE[key]

    if 'rects' in cfg:
        frame_idx = int(frame_idx)
        sx, sy, sw, sh = cfg['rects'][frame_idx % len(cfg['rects'])]
        if face_dir == -1 and cfg.get('flip_when_left', False):
            image.clip_composite_draw(sx, sy, sw, sh, 0, 'h', x, y, draw_w, draw_h)
        else:
            image.clip_draw(sx, sy, sw, sh, x, y, draw_w, draw_h)
        return

    sx = (cfg['start_col'] + frame_idx) * CELL_W
    sy = row_y_from_top(cfg['row'])
    if face_dir == -1 and cfg.get('flip_when_left', False):
        image.clip_composite_draw(sx, sy, CELL_W, CELL_H, 0, 'h', x, y, draw_w, draw_h)
    else:
        image.clip_draw(sx, sy, CELL_W, CELL_H, x, y, draw_w, draw_h)


idle_time_per_action = 0.5
idle_action_per_time = 1.0 / idle_time_per_action
idle_frames_per_action = 4
idle_frame_per_second = idle_frames_per_action * idle_action_per_time


class Idle:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['idle']['frames']

    def enter(self, e):
        self.keroro.dir = 0
        self.keroro.wait_start_time = get_time()
        self.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + idle_frame_per_second * game_framework.frame_time) % self.frame_count

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.keroro.image,
            'idle',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )


class Run:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0
        self.frame_count = SPRITE['run']['frames']
        self.SPEED = 2

    def enter(self, e):
        self.frame = 0

        if e and e[0] == 'INPUT':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_RIGHT:
                    self.keroro.dir = 1
                    self.keroro.face_dir = 1
                elif ev.key == SDLK_LEFT:
                    self.keroro.dir = -1
                    self.keroro.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + 1) % self.frame_count
        self.keroro.x += self.keroro.dir * self.SPEED
        self.keroro.x = max(50, min(1550, self.keroro.x))

    def draw(self):
        self.keroro._ensure_image()
        draw_from_cfg(
            self.keroro.image,
            'run',
            self.frame,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )


class AutoRun:
    def __init__(self, keroro):
        self.keroro = keroro

    def enter(self, e):
        self.start_time = get_time()
        self.keroro.dir = -1
        self.keroro.face_dir = -1

    def exit(self, e):
        self.keroro.dir = 0

    def do(self):
        self.keroro.frame = (self.keroro.frame + 1) % SPRITE['run']['frames']
        self.keroro.x += self.keroro.dir * 10
        self.keroro.x = max(50, min(1550, self.keroro.x))

    def draw(self):
        self.keroro._ensure_image()
        draw_from_cfg(
            self.keroro.image,
            'run',
            self.keroro.frame,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            DRAW_W + 8, DRAW_H + 8
        )


class Attack:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['attack']['frames']

        self.SPEED = 8
        self.move_during_attack = False

        self.anim_speed = 0.2
        self.finished = False

        self.hold_time = 0.15
        self.hold_timer = 0.0

    def enter(self, e):

        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        # 공격 시작할 때 캐릭터가 움직이는 중이었는지 기억
        self.move_during_attack = (self.keroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            # 공격 애니메이션 재생 구간
            self.frame += self.anim_speed  # 숫자 줄이면 더 느리게, 늘이면 더 빠르게

            # 공격 중 이동(달리던 상태에서 공격 시작한 경우)
            if self.move_during_attack:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            # 마지막 프레임에 도달했는지 체크
            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1  # 마지막 프레임에 고정
                self.finished = True               # 이제부터는 hold 단계로
        else:
            # 마지막 프레임 유지 구간
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                # hold 시간이 다 지나면 그제서야 상태 전환
                if self.move_during_attack:
                    # 달리던 중 공격 → Run 으로
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    # Idle 중 공격 → Idle 로
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):

        self.keroro._ensure_image()
        idx = int(self.frame)  # 안전하게 정수로

        draw_from_cfg(
            self.keroro.image,
            'attack',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )


class Attack2:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['attack2']['frames']

        self.SPEED = 8                 # 필요하면 Attack 과 다르게 조절 가능
        self.move_during_attack = False

        self.anim_speed = 0.4          # Attack2 전용 속도 (원하면 다르게)
        self.finished = False

        self.hold_time = 0.15          # 마지막 프레임 유지 시간
        self.hold_timer = 0.0

    def enter(self, e):

        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0


        # 공격 시작할 때 캐릭터가 움직이는 중이었는지 기억
        self.move_during_attack = (self.keroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            # Attack2 애니메이션 재생 구간
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            # 마지막 프레임 유지 구간
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):

        self.keroro._ensure_image()
        idx = int(self.frame)
        if self.keroro.face_dir == -1:
            # 왼쪽을 향할 때는 약간 위치 조정
            draw_from_cfg(
                self.keroro.image,
                'attack2',
                idx,
                self.keroro.face_dir,
                self.keroro.x - 50,
                self.keroro.y,
                110, 100
            )
        else:
            draw_from_cfg(
                self.keroro.image,
                'attack2',
                idx,
                self.keroro.face_dir,
                self.keroro.x+50,
                self.keroro.y,
                110, 100
            )


# ---------------------------

class Keroro:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.image_name = 'Keroro_Sheet.png'
        self.image = None

        self.IDLE    = Idle(self)
        self.RUN     = Run(self)
        self.AUTORUN = AutoRun(self)
        self.ATTACK  = Attack(self)
        self.ATTACK2 = Attack2(self)   # ★ Attack2 상태 추가

        self.state_machine = StateMachine(
            self.IDLE,
            {

                self.IDLE: {
                    right_down: self.RUN,
                    left_down:  self.RUN,
                    a_down:     self.AUTORUN,
                    s_down:     self.ATTACK,    # S → Attack
                    d_down:     self.ATTACK2,   # D → Attack2
                },

                self.RUN: {
                    right_up:   self.IDLE,
                    left_up:    self.IDLE,
                    right_down: self.RUN,
                    left_down:  self.RUN,
                    a_down:     self.AUTORUN,
                    s_down:     self.ATTACK,    # 달리는 중 S → Attack
                    d_down:     self.ATTACK2,   # 달리는 중 D → Attack2
                },

                # AutoRun 상태에서
                self.AUTORUN: {
                    Time_out:   self.IDLE,
                    right_down: self.RUN,
                    left_down:  self.RUN,
                    s_down:     self.ATTACK,
                    d_down:     self.ATTACK2,
                },

                # Attack 이 끝나면 Idle/Run 으로
                self.ATTACK: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                # Attack2 가 끝나도 Idle/Run 으로 (같은 이벤트 재사용)
                self.ATTACK2: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

            }
        )

    def _ensure_image(self):
        if self.image is None:
            self.image = load_image(self.image_name)

    def update(self):
        self.state_machine.update()

    def draw(self):
        self._ensure_image()
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


keroro = Keroro()
