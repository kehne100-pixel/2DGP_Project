from pico2d import *
from sdl2 import (
    SDL_KEYDOWN, SDL_KEYUP,
    SDLK_RIGHT, SDLK_LEFT,
    SDLK_a, SDLK_s, SDLK_d,
    SDLK_SPACE,
    SDLK_1,
    SDLK_2,
    SDLK_3,
)
import game_framework
from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def a_up(e):       return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_a
def s_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s
def d_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def space_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE
def Time_out(e):   return e[0] == 'TIME_OUT'
def attack_done_idle(e): return e[0] == 'ATTACK_DONE_IDLE'
def attack_done_run(e):  return e[0] == 'ATTACK_DONE_RUN'
def jump_to_fall(e): return e[0] == 'JUMP_TO_FALL'
def land_idle(e):    return e[0] == 'LAND_IDLE'
def land_run(e):     return e[0] == 'LAND_RUN'

def skill_down(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_1
def skill2_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_2
def skill3_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_3


IMAGE_W, IMAGE_H = 996, 1917
CELL_W, CELL_H   = 40, 80
DRAW_W, DRAW_H   = 130, 130


def row_y_from_top(row_from_top):
    return IMAGE_H - (row_from_top + 1) * CELL_H


SPRITE = {
    'idle': {
        'rects': [
            (0,   2145, 40, 55),
            (43,  2145, 39, 55),
            (84, 2146, 40, 56),
            (127, 2146, 38, 54),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'run': {
        'rects': [
            (0,   1966, 39, 52),
            (43,  1965, 33, 55),
            (82, 1965, 37, 54),
            (137, 1966, 34, 54),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'attack': {
        'rects': [
            (0,   2303, 56, 57),
            (58,  2305, 59, 55),
            (123, 2305, 58, 56),
        ],
        'frames': 3,
        'flip_when_left': True
    },

    'attack2': {
        'rects': [
            (1, 1497, 40, 54),
            (49, 1502, 56, 56),
            (110, 1505, 56, 56),
            (171, 1506, 63, 54),
            (243, 1503, 62, 60),
        ],
        'frames': 5,
        'flip_when_left': True
    },

    'guard': {
        'rects': [
            (0, 1665, 36, 57),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'jump': {
        'rects': [
            (0, 1905, 50, 54),
            (52, 1905, 49, 56),
            (103, 1906, 49, 55),
            (153, 1905, 48, 55),

        ],
        'frames': 4,
        'flip_when_left': True
    },

    'fall': {
        'rects': [
            (205, 1905, 47, 56),
            (255, 1905, 48, 55),
            (307, 1905, 48, 54),
            (357, 1905, 38, 53),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'skill': {
        'rects': [
            (0, 1826, 54, 53),
            (57, 1825, 56, 54),
            (115, 1826, 53, 54),
            (194, 1824, 49, 54),
            (260, 1825, 47, 55),
            (321, 1825, 46, 54),
            (378, 1825, 50, 53),
            (438, 1828, 48, 52),
            (505, 1825, 49, 55),
        ],
        'frames': 9,
        'flip_when_left': True
    },

    'skill2': {
        'rects': [
            (0, 1761, 40, 59),
            (41, 1761, 47, 59),
            (92, 1765, 62, 55),
            (158, 1765, 62, 55),
            (223, 1765, 67, 55),
            (295, 1766, 63, 56),
        ],
        'frames': 6,
        'flip_when_left': True
    },

    'skill3': {
        'rects': [
            (185, 1605, 46, 55),
            (239, 1605, 49, 59),
            (298, 1604 ,49, 57),
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

Run_time_per_action = 0.5
Run_action_per_time = 1.0 / Run_time_per_action
Run_frames_per_action = 4
Run_frame_per_second = Run_frames_per_action * Run_action_per_time


class Idle:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['idle']['frames']

    def enter(self, e):
        self.kururu.dir = 0
        self.kururu.wait_start_time = get_time()
        self.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + idle_frame_per_second * game_framework.frame_time) % self.frame_count

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.kururu.image,
            'idle',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y,
            100, 100
        )


class Run:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0
        self.frame_count = SPRITE['run']['frames']
        self.SPEED = 2

    def enter(self, e):
        self.frame = 0

        if e and e[0] == 'INPUT':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_RIGHT:
                    self.kururu.dir = 1
                    self.kururu.face_dir = 1
                elif ev.key == SDLK_LEFT:
                    self.kururu.dir = -1
                    self.kururu.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + Run_frame_per_second * game_framework.frame_time) % self.frame_count
        self.kururu.x += self.kururu.dir * self.SPEED
        self.kururu.x = max(50, min(1550, self.kururu.x))

    def draw(self):
        self.kururu._ensure_image()
        draw_from_cfg(
            self.kururu.image,
            'run',
            self.frame,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y,
            100, 100
        )


class Attack:
    def __init__(self, kururu):
        self.kururu = kururu
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

        self.move_during_attack = (self.kururu.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.kururu.x += self.kururu.dir * self.SPEED
                self.kururu.x = max(50, min(1550, self.kururu.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.kururu.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.kururu.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame)

        draw_from_cfg(
            self.kururu.image,
            'attack',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y,
            100, 100
        )


class Attack2:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['attack2']['frames']

        self.SPEED = 8
        self.move_during_attack = False

        self.anim_speed = 0.1
        self.finished = False

        self.hold_time = 0.15
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.move_during_attack = (self.kururu.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.kururu.x += self.kururu.dir * self.SPEED
                self.kururu.x = max(50, min(1550, self.kururu.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.kururu.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.kururu.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame)

        if self.kururu.face_dir == -1:
            draw_from_cfg(
                self.kururu.image,
                'attack2',
                idx,
                self.kururu.face_dir,
                self.kururu.x - 50,
                self.kururu.y,
                110, 100
            )
        else:
            draw_from_cfg(
                self.kururu.image,
                'attack2',
                idx,
                self.kururu.face_dir,
                self.kururu.x + 50,
                self.kururu.y,
                110, 100
            )


class Guard:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.anim_speed = 0.15

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.kururu.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.kururu.image,
            'guard',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y,
            100, 100
        )


class Jump:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']
        self.anim_speed = 0.2

        self.JUMP_POWER = 18
        self.GRAVITY    = -0.5

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']

        self.kururu.vy = self.JUMP_POWER

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.kururu.y += self.kururu.vy
        self.kururu.vy += self.GRAVITY

        if self.kururu.vy <= 0:
            self.kururu.state_machine.handle_state_event(('JUMP_TO_FALL', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.kururu.image,
            'jump',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y,
            100, 100
        )


class Fall:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['fall']['frames']
        self.anim_speed = 0.03  # 느리게 한 프레임처럼 보이게

        self.GRAVITY = -0.05

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['fall']['frames']

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.kururu.y += self.kururu.vy
        self.kururu.vy += self.GRAVITY

        if self.kururu.y <= self.kururu.ground_y:
            self.kururu.y = self.kururu.ground_y
            self.kururu.vy = 0

            if self.kururu.dir != 0:
                self.kururu.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.kururu.state_machine.handle_state_event(('LAND_IDLE', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.kururu.image,
            'fall',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y,
            100, 100
        )


class Skill:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['skill']['frames']

        self.SPEED = 3
        self.move_during_skill = False

        self.anim_speed = 0.08
        self.finished = False

        self.hold_time = 0.5
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.kururu.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.kururu.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                # 스킬 끝나면 항상 Idle로
                self.kururu.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.kururu.image,
            'skill',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Skill2:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['skill2']['frames']

        self.SPEED = 3
        self.move_during_skill = False

        self.anim_speed = 0.08
        self.finished = False

        self.hold_time = 0.5
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.kururu.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.kururu.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                # 항상 Idle로 복귀
                self.kururu.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.kururu.image,
            'skill2',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Skill3:
    def __init__(self, kururu):
        self.kururu = kururu
        self.frame = 0.0
        self.frame_count = SPRITE['skill3']['frames']

        self.SPEED = 6
        self.move_during_skill = False

        self.anim_speed = 0.18
        self.finished = False

        self.hold_time = 0.35
        self.hold_timer = 0.0

        self.start_hold_time = 0.15
        self.start_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.start_timer = 0.0

        if self.kururu.face_dir != 0:
            self.kururu.dir = self.kururu.face_dir

        self.move_during_skill = (self.kururu.dir != 0)

    def exit(self, e):
        self.kururu.dir = 0

    def do(self):
        if not self.finished:
            if self.start_timer < self.start_hold_time:
                self.start_timer += game_framework.frame_time
                return

            self.frame += self.anim_speed

            if self.move_during_skill:
                self.kururu.x += self.kururu.dir * self.SPEED
                self.kururu.x = max(50, min(1550, self.kururu.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                # 스킬3도 Idle로 끝
                self.kururu.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.kururu._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.kururu.image,
            'skill3',
            idx,
            self.kururu.face_dir,
            self.kururu.x,
            self.kururu.y + 10,
            skill_draw_w,
            skill_draw_h
        )


# ---------------------------
# Kururu 본체
# ---------------------------
class Kururu:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.vy = 0.0
        self.ground_y = 90

        # 실제 이미지 파일 이름에 맞게 수정해줘
        self.image_name = 'Kururu_Sheet.png'
        self.image = None

        self.IDLE   = Idle(self)
        self.RUN    = Run(self)
        self.ATTACK = Attack(self)
        self.ATTACK2 = Attack2(self)
        self.GUARD  = Guard(self)
        self.JUMP   = Jump(self)
        self.FALL   = Fall(self)
        self.SKILL  = Skill(self)
        self.SKILL2 = Skill2(self)
        self.SKILL3 = Skill3(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    right_down:     self.RUN,
                    left_down:      self.RUN,
                    a_down:         self.GUARD,
                    s_down:         self.ATTACK,
                    d_down:         self.ATTACK2,
                    space_down:     self.JUMP,
                    skill_down:     self.SKILL,
                    skill2_down:    self.SKILL2,
                    skill3_down:    self.SKILL3,
                },

                self.RUN: {
                    right_up:       self.IDLE,
                    left_up:        self.IDLE,
                    right_down:     self.RUN,
                    left_down:      self.RUN,
                    a_down:         self.GUARD,
                    s_down:         self.ATTACK,
                    d_down:         self.ATTACK2,
                    space_down:     self.JUMP,
                    skill_down:     self.SKILL,
                    skill2_down:    self.SKILL2,
                    skill3_down:    self.SKILL3,
                },

                self.ATTACK: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                self.ATTACK2: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                self.GUARD: {
                    a_up:           self.IDLE,
                },

                self.JUMP: {
                    jump_to_fall:   self.FALL,
                },

                self.FALL: {
                    land_idle:      self.IDLE,
                    land_run:       self.RUN,
                },


                self.SKILL: {
                    attack_done_idle: self.IDLE,
                },

                self.SKILL2: {
                    attack_done_idle: self.IDLE,
                },

                self.SKILL3: {
                    attack_done_idle: self.IDLE,
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


kururu = Kururu()
