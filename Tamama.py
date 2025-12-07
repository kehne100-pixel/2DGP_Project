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

import camera  # 카메라/스크롤 연동용


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
def jump_to_fall(e):     return e[0] == 'JUMP_TO_FALL'
def land_idle(e):        return e[0] == 'LAND_IDLE'
def land_run(e):         return e[0] == 'LAND_RUN'

def skill_down(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_1
def skill2_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_2
def skill3_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_3


IMAGE_W, IMAGE_H = 996, 1917
CELL_W, CELL_H   = 40, 80
DRAW_W, DRAW_H   = 130, 130


def row_y_from_top(row_from_top):
    return IMAGE_H - (row_from_top + 1) * CELL_H


# 🔴 여기 SPRITE는 예시용이야.
# 네가 원래 Tamama.py에서 쓰던 SPRITE 딕셔너리를
# 이 자리에 그대로 복붙해서 쓰면 애니메이션이 정상으로 돌아와.
SPRITE = {
    'idle': {
        'rects': [
            (0, 0, 40, 60),
            (40, 0, 40, 60),
            (80, 0, 40, 60),
            (120, 0, 40, 60),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'run': {
        'rects': [
            (0, 60, 40, 60),
            (40, 60, 40, 60),
            (80, 60, 40, 60),
            (120, 60, 40, 60),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'attack': {
        'rects': [
            (0, 120, 50, 60),
            (50, 120, 50, 60),
            (100, 120, 50, 60),
        ],
        'frames': 3,
        'flip_when_left': True
    },

    'attack2': {
        'rects': [
            (0, 180, 60, 60),
            (60, 180, 60, 60),
            (120, 180, 60, 60),
        ],
        'frames': 3,
        'flip_when_left': True
    },

    'guard': {
        'rects': [
            (0, 240, 40, 60),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'jump': {
        'rects': [
            (0, 300, 40, 60),
            (40, 300, 40, 60),
            (80, 300, 40, 60),
            (120, 300, 40, 60),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'fall': {
        'rects': [
            (0, 360, 40, 60),
            (40, 360, 40, 60),
        ],
        'frames': 2,
        'flip_when_left': True
    },

    'skill': {
        'rects': [
            (0, 420, 60, 60),
            (60, 420, 60, 60),
            (120, 420, 60, 60),
        ],
        'frames': 3,
        'flip_when_left': True
    },

    'skill2': {
        'rects': [
            (0, 480, 60, 60),
            (60, 480, 60, 60),
            (120, 480, 60, 60),
            (180, 480, 60, 60),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'skill3': {
        'rects': [
            (0, 540, 60, 60),
            (60, 540, 60, 60),
            (120, 540, 60, 60),
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
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0.0
        self.frame_count = SPRITE['idle']['frames']

    def enter(self, e):
        self.tamama.dir = 0
        self.tamama.wait_start_time = get_time()
        self.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + idle_frame_per_second * game_framework.frame_time) % self.frame_count

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'idle',
            idx,
            self.tamama.face_dir,
            sx, sy,
            100, 100
        )


class Run:
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0
        self.frame_count = SPRITE['run']['frames']
        self.SPEED = 2

    def enter(self, e):
        self.frame = 0

        if e and e[0] == 'INPUT':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_RIGHT:
                    self.tamama.dir = 1
                    self.tamama.face_dir = 1
                elif ev.key == SDLK_LEFT:
                    self.tamama.dir = -1
                    self.tamama.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + Run_frame_per_second * game_framework.frame_time) % self.frame_count
        self.tamama.x += self.tamama.dir * self.SPEED
        self.tamama.x = max(50, min(1550, self.tamama.x))

    def draw(self):
        self.tamama._ensure_image()

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'run',
            self.frame,
            self.tamama.face_dir,
            sx, sy,
            100, 100
        )


class Attack:
    def __init__(self, tamama):
        self.tamama = tamama
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

        self.move_during_attack = (self.tamama.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.tamama.x += self.tamama.dir * self.SPEED
                self.tamama.x = max(50, min(1550, self.tamama.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame)

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'attack',
            idx,
            self.tamama.face_dir,
            sx, sy,
            100, 100
        )


class Attack2:
    def __init__(self, tamama):
        self.tamama = tamama
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

        self.move_during_attack = (self.tamama.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.tamama.x += self.tamama.dir * self.SPEED
                self.tamama.x = max(50, min(1550, self.tamama.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame)

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()
        offset = 50

        if self.tamama.face_dir == -1:
            draw_from_cfg(
                self.tamama.image,
                'attack2',
                idx,
                self.tamama.face_dir,
                sx - offset, sy,
                110, 100
            )
        else:
            draw_from_cfg(
                self.tamama.image,
                'attack2',
                idx,
                self.tamama.face_dir,
                sx + offset, sy,
                110, 100
            )


class Guard:
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.anim_speed = 0.15

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.tamama.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'guard',
            idx,
            self.tamama.face_dir,
            sx, sy,
            100, 100
        )


class Jump:
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']
        self.anim_speed = 0.2

        self.JUMP_POWER = 18
        self.GRAVITY    = -0.5

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']

        self.tamama.vy = self.JUMP_POWER

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.tamama.y += self.tamama.vy
        self.tamama.vy += self.GRAVITY

        if self.tamama.vy <= 0:
            self.tamama.state_machine.handle_state_event(('JUMP_TO_FALL', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'jump',
            idx,
            self.tamama.face_dir,
            sx, sy,
            100, 100
        )


class Fall:
    def __init__(self, tamama):
        self.tamama = tamama
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
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.tamama.y += self.tamama.vy
        self.tamama.vy += self.GRAVITY

        if self.tamama.y <= self.tamama.ground_y:
            self.tamama.y = self.tamama.ground_y
            self.tamama.vy = 0

            if self.tamama.dir != 0:
                self.tamama.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.tamama.state_machine.handle_state_event(('LAND_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'fall',
            idx,
            self.tamama.face_dir,
            sx, sy,
            100, 100
        )


class Skill:
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0.0
        self.frame_count = SPRITE['skill']['frames']

        self.SPEED = 3
        self.move_during_skill = False

        self.anim_speed = 0.08
        self.finished = False

        self.hold_time = 0.35
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        if self.tamama.face_dir != 0:
            self.tamama.dir = self.tamama.face_dir

        self.move_during_skill = (self.tamama.dir != 0)

    def exit(self, e):
        self.tamama.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_skill:
                self.tamama.x += self.tamama.dir * self.SPEED
                self.tamama.x = max(50, min(1550, self.tamama.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.tamama.dir != 0:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'skill',
            idx,
            self.tamama.face_dir,
            sx, sy + 10,
            110, 110
        )


class Skill2:
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0.0
        self.frame_count = SPRITE['skill2']['frames']

        self.SPEED = 3
        self.move_during_skill = False

        self.anim_speed = 0.08
        self.finished = False

        self.hold_time = 0.35
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        if self.tamama.face_dir != 0:
            self.tamama.dir = self.tamama.face_dir

        self.move_during_skill = (self.tamama.dir != 0)

    def exit(self, e):
        self.tamama.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_skill:
                self.tamama.x += self.tamama.dir * self.SPEED
                self.tamama.x = max(50, min(1550, self.tamama.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.tamama.dir != 0:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'skill2',
            idx,
            self.tamama.face_dir,
            sx, sy + 10,
            110, 110
        )


class Skill3:
    def __init__(self, tamama):
        self.tamama = tamama
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

        if self.tamama.face_dir != 0:
            self.tamama.dir = self.tamama.face_dir

        self.move_during_skill = (self.tamama.dir != 0)

    def exit(self, e):
        self.tamama.dir = 0

    def do(self):
        if not self.finished:
            if self.start_timer < self.start_hold_time:
                self.start_timer += game_framework.frame_time
                return

            self.frame += self.anim_speed

            if self.move_during_skill:
                self.tamama.x += self.tamama.dir * self.SPEED
                self.tamama.x = max(50, min(1550, self.tamama.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.tamama.dir != 0:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        sx, sy, _ = self.tamama.get_screen_pos_and_scale()

        draw_from_cfg(
            self.tamama.image,
            'skill3',
            idx,
            self.tamama.face_dir,
            sx, sy + 10,
            110, 110
        )


class Tamama:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.vy = 0.0
        self.ground_y = 90

        self.image_name = 'Tamama_Sheet.png'
        self.image = None

        self.IDLE    = Idle(self)
        self.RUN     = Run(self)
        self.ATTACK  = Attack(self)
        self.ATTACK2 = Attack2(self)
        self.GUARD   = Guard(self)
        self.JUMP    = Jump(self)
        self.FALL    = Fall(self)
        self.SKILL   = Skill(self)
        self.SKILL2  = Skill2(self)
        self.SKILL3  = Skill3(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    right_down:  self.RUN,
                    left_down:   self.RUN,
                    a_down:      self.GUARD,
                    s_down:      self.ATTACK,
                    d_down:      self.ATTACK2,
                    space_down:  self.JUMP,
                    skill_down:  self.SKILL,
                    skill2_down: self.SKILL2,
                    skill3_down: self.SKILL3,
                },

                self.RUN: {
                    right_up:    self.IDLE,
                    left_up:     self.IDLE,
                    right_down:  self.RUN,
                    left_down:   self.RUN,
                    a_down:      self.GUARD,
                    s_down:      self.ATTACK,
                    d_down:      self.ATTACK2,
                    space_down:  self.JUMP,
                    skill_down:  self.SKILL,
                    skill2_down: self.SKILL2,
                    skill3_down: self.SKILL3,
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
                    a_up: self.IDLE,
                },

                self.JUMP: {
                    jump_to_fall: self.FALL,
                },

                self.FALL: {
                    land_idle: self.IDLE,
                    land_run:  self.RUN,
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

    def get_screen_pos_and_scale(self):
        sx, sy = camera.world_to_screen(self.x, self.y)
        scale = camera.get_zoom()
        return sx, sy, scale

    def update(self):
        self.state_machine.update()

    def draw(self):
        self._ensure_image()
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


tamama = Tamama()
