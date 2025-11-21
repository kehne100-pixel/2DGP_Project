from pico2d import *
from sdl2 import (
    SDL_KEYDOWN, SDL_KEYUP,
    SDLK_RIGHT, SDLK_LEFT,
    SDLK_a, SDLK_s, SDLK_d,
    SDLK_SPACE
)
import game_framework
from state_machine import StateMachine

def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a   # Guard 시작
def a_up(e):       return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_a   # Guard 해제
def s_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s   # Attack
def d_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d   # Attack2
def space_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE  # ★ 점프
def Time_out(e):   return e[0] == 'TIME_OUT'
def attack_done_idle(e): return e[0] == 'ATTACK_DONE_IDLE'
def attack_done_run(e):  return e[0] == 'ATTACK_DONE_RUN'
def jump_to_fall(e): return e[0] == 'JUMP_TO_FALL'   # Jump → Fall
def land_idle(e):    return e[0] == 'LAND_IDLE'      # Fall → Idle
def land_run(e):     return e[0] == 'LAND_RUN'       # Fall → Run


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


    'guard': {
        'rects': [

            (469, 1617, 51, 52),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'jump': {
        'rects': [

            (0, 1393, 75, 44),
            (79, 1391, 62, 60),
            (151, 1393, 64, 58),
            (227, 1392, 61, 58),
            (299, 1392, 64, 60),
            (375, 1392, 62, 59),
            (447, 1392, 64, 58),
            (522, 1392, 63, 56),
            (595, 1392, 63, 60),
        ],
        'frames': 9,
        'flip_when_left': True
    },


    'fall': {
        'rects': [

            (7, 1313, 52, 71),
            (73, 1313, 51, 73),
            (137, 1313, 53, 73),
            (203, 1313, 51, 73),
            (267, 1313, 52, 72),
            (333, 1313, 51, 71),
            (397, 1313, 52, 73),
            (463, 1313, 50, 73),


        ],
        'frames': 8,
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

Run_time_per_action = 0.5
Run_action_per_time = 1.0 / Run_time_per_action
Run_frames_per_action = 4
Run_frame_per_second = Run_frames_per_action * Run_action_per_time



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
        self.frame = (self.frame + Run_frame_per_second * game_framework.frame_time) % self.frame_count
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

        # 공격 시작할 때 움직이는 중이었는지 저장
        self.move_during_attack = (self.keroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:

            self.frame += self.anim_speed


            if self.move_during_attack:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            # 마지막 프레임 도달 체크
            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            # 마지막 프레임 홀드
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame)

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

        self.SPEED = 8
        self.move_during_attack = False

        self.anim_speed = 0.4
        self.finished = False

        self.hold_time = 0.15
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.move_during_attack = (self.keroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
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
                self.keroro.x + 50,
                self.keroro.y,
                110, 100
            )



class Guard:

    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.anim_speed = 0.15

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.keroro.dir = 0  # 가드 중엔 이동 안 함

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.keroro.image,
            'guard',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )



class Jump:

    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']
        self.anim_speed = 0.2

        self.JUMP_POWER = 18
        self.GRAVITY    = -0.5

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']


        self.keroro.vy = self.JUMP_POWER

    def exit(self, e):
        pass

    def do(self):

        self.frame = (self.frame + self.anim_speed) % self.frame_count


        self.keroro.y += self.keroro.vy
        self.keroro.vy += self.GRAVITY


        if self.keroro.vy <= 0:
            self.keroro.state_machine.handle_state_event(('JUMP_TO_FALL', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.keroro.image,
            'jump',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )


class Fall:

    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['fall']['frames']
        self.anim_speed = 0.25

        self.GRAVITY = -0.05

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['fall']['frames']

    def exit(self, e):
        pass

    def do(self):
        # 애니메이션
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        # 수직 이동 + 중력
        self.keroro.y += self.keroro.vy
        self.keroro.vy += self.GRAVITY

        # 바닥 도착 체크
        if self.keroro.y <= self.keroro.ground_y:
            self.keroro.y = self.keroro.ground_y
            self.keroro.vy = 0

            # 움직이고 있으면 Run, 아니면 Idle로 착지
            if self.keroro.dir != 0:
                self.keroro.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.keroro.state_machine.handle_state_event(('LAND_IDLE', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.keroro.image,
            'fall',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )


# ---------------------------
# Keroro 본체
# ---------------------------
class Keroro:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        # 점프/하강 물리값
        self.vy = 0.0
        self.ground_y = 90   # 바닥 높이

        self.image_name = 'Keroro_Sheet.png'
        self.image = None

        # 상태 인스턴스
        self.IDLE    = Idle(self)
        self.RUN     = Run(self)
        self.ATTACK  = Attack(self)
        self.ATTACK2 = Attack2(self)
        self.GUARD   = Guard(self)
        self.JUMP    = Jump(self)
        self.FALL    = Fall(self)

        # 상태 머신 구성
        self.state_machine = StateMachine(
            self.IDLE,
            {

                # Idle 상태
                self.IDLE: {
                    right_down:     self.RUN,
                    left_down:      self.RUN,
                    a_down:         self.GUARD,    # A → Guard
                    s_down:         self.ATTACK,   # S → Attack
                    d_down:         self.ATTACK2,  # D → Attack2
                    space_down:     self.JUMP,     # ★ Space → Jump
                },

                # Run 상태
                self.RUN: {
                    right_up:       self.IDLE,
                    left_up:        self.IDLE,
                    right_down:     self.RUN,
                    left_down:      self.RUN,
                    a_down:         self.GUARD,
                    s_down:         self.ATTACK,
                    d_down:         self.ATTACK2,
                    space_down:     self.JUMP,     # ★ 달리면서도 Space → Jump
                },



                # Attack 끝나면 Idle/Run
                self.ATTACK: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                # Attack2 끝나면 Idle/Run
                self.ATTACK2: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                # Guard 상태
                self.GUARD: {
                    a_up:           self.IDLE,   # A 떼면 Idle 로
                },

                # Jump 상태
                self.JUMP: {
                    jump_to_fall:   self.FALL,   # 최고점 → Fall
                },

                # Fall 상태
                self.FALL: {
                    land_idle:      self.IDLE,   # 착지 → Idle
                    land_run:       self.RUN,    # 착지 → Run
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
