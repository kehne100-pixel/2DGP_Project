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

# 🔥 충돌 디버그용
from fight_collision import DEBUG_COLLISION, draw_bb


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
            (14,   2447, 40, 52),
            (81,  2445, 39, 55),
            (146, 2445, 40, 55),
            (212, 2445, 42, 53),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'run': {
        'rects': [
            (11,   2221, 41, 54),
            (77,  2222, 41, 54),
            (145, 2221, 38, 53),
            (210, 2222, 39, 54),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'attack': {
        'rects': [
            (213,   1920, 38, 55),
            (271,  1920, 59, 53),
            (339, 1920, 61, 53),
        ],
        'frames': 4,   # rect는 3개지만 마지막 프레임은 첫 rect 재사용(현재 구조 유지)
        'flip_when_left': True
    },

    'attack2': {
        'rects': [
            (405, 1920, 37, 55),
            (479, 1921, 50, 48),
            (535, 1920, 59, 61),
            (607, 1921, 53, 61),
            (673, 1920, 47, 53),
        ],
        'frames': 5,
        'flip_when_left': True
    },

    'guard': {
        'rects': [
            (212, 2075, 39, 52),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'jump': {
        'rects': [
            (16, 2366, 45, 46),
            (79, 2369, 37, 58),
            (143, 2367, 40 ,58),
            (211, 2368, 38, 58),
            (275, 2366, 41, 58),
            (343, 2369, 37, 58),
            (407, 2367, 40, 58),
            (475, 2368, 38, 57),
            (539, 2369, 40, 58),
            (603, 2367, 44, 58),
            (667, 2368, 50, 58),
            (738, 2366, 51, 52),
            (806, 2369, 47, 46),
        ],
        'frames': 13,
        'flip_when_left': True
    },

    'fall': {
        'rects': [
            (333, 2071, 48, 67),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'skill': {
        'rects': [
            (6, 1769, 45, 54),
            (68, 1773, 66, 52),
            (142, 1775, 62, 50),
            (212, 1769, 37, 55),
            (275, 1770, 59, 69),
            (343, 1770, 56, 50),
        ],
        'frames': 6,
        'flip_when_left': True
    },

    'skill2': {
        'rects': [
            (253, 285, 71, 47),
            (333, 285, 74, 47),
            (416, 285, 67, 51),
            (494, 285, 76, 51),
            (577, 286, 70, 46),
            (657, 285, 75, 47),
            (736, 285, 50, 51),
            (818, 286, 58, 61),
            (900, 285, 36, 62),
        ],
        'frames': 9,
        'flip_when_left': True
    },

    'skill3': {
        'rects': [
            (482, 2071, 39, 47),
            (539, 2071, 49, 57),
            (607, 2071 ,43, 57),
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

        draw_from_cfg(
            self.tamama.image,
            'idle',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y,
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
        draw_from_cfg(
            self.tamama.image,
            'run',
            self.frame,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y,
            100, 100
        )


class Attack:
    def __init__(self, tamama):
        self.tamama = tamama

        self.frame_count = SPRITE['attack']['frames']
        self.frame_durations = [0.16, 0.06, 0.12, 0.18]

        self.frame = 0
        self.timer = 0.0

        self.SPEED = 7
        self.move_during_attack = False

        self.finished = False
        self.hold_time = 0.15
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0
        self.timer = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.move_during_attack = (self.tamama.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.timer += game_framework.frame_time

            if self.timer >= self.frame_durations[self.frame]:
                self.timer -= self.frame_durations[self.frame]
                self.frame += 1

                if self.frame >= self.frame_count:
                    self.frame = self.frame_count - 1
                    self.finished = True
                    return

            if self.move_during_attack:
                if self.frame == 0:
                    dx = self.tamama.dir * (self.SPEED * 0.3)
                elif self.frame == 1:
                    dx = self.tamama.dir * (self.SPEED * 1.0)
                elif self.frame == 2:
                    dx = self.tamama.dir * (self.SPEED * 0.1)
                else:
                    dx = 0

                self.tamama.x += dx
                self.tamama.x = max(50, min(1550, self.tamama.x))
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

        draw_from_cfg(
            self.tamama.image,
            'attack',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y,
            110, 110
        )


class Attack2:
    def __init__(self, tamama):
        self.tamama = tamama
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

        if self.tamama.face_dir == -1:
            draw_from_cfg(
                self.tamama.image,
                'attack2',
                idx,
                self.tamama.face_dir,
                self.tamama.x - 50,
                self.tamama.y,
                110, 100
            )
        else:
            draw_from_cfg(
                self.tamama.image,
                'attack2',
                idx,
                self.tamama.face_dir,
                self.tamama.x + 50,
                self.tamama.y,
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

        draw_from_cfg(
            self.tamama.image,
            'guard',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y,
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

        draw_from_cfg(
            self.tamama.image,
            'jump',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y,
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

        draw_from_cfg(
            self.tamama.image,
            'fall',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y,
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

        self.hold_time = 0.5
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.tamama.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.tamama.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.tamama.image,
            'skill',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y + 10,
            skill_draw_w,
            skill_draw_h
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

        self.hold_time = 0.5
        self.hold_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        self.tamama.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.tamama.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.tamama.image,
            'skill2',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Skill3:
    def __init__(self, tamama):
        self.tamama = tamama
        self.frame = 0.0
        self.frame_count = SPRITE['skill3']['frames']

        self.SPEED = 6          # 지금은 안 쓰지만 남겨둠
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

        self.tamama.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.tamama.dir = 0

    def do(self):
        if not self.finished:
            if self.start_timer < self.start_hold_time:
                self.start_timer += game_framework.frame_time
                return

            self.frame += self.anim_speed

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                self.tamama.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.tamama._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.tamama.image,
            'skill3',
            idx,
            self.tamama.face_dir,
            self.tamama.x,
            self.tamama.y + 10,
            skill_draw_w,
            skill_draw_h
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

        # 🔥 HP, 이전 위치(몸통 충돌용)
        self.max_hp = 100
        self.hp = self.max_hp
        self.prev_x = self.x
        self.prev_y = self.y

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

    # === 상태 체크 ===
    def is_attacking(self):
        s = self.state_machine.cur_state
        return s in (self.ATTACK, self.ATTACK2, self.SKILL, self.SKILL2, self.SKILL3)

    # === 몸통 바운딩 박스 ===
    def get_body_bb(self):
        # 타마마는 케로로보다 조금 작게
        half_w = 30
        half_h = 50
        return (self.x - half_w, self.y - half_h,
                self.x + half_w, self.y + half_h)

    # === 공격 판정 박스 ===
    def get_attack_bb(self):
        if not self.is_attacking():
            return None

        if self.face_dir == 1:
            left  = self.x
            right = self.x + 80
        else:
            left  = self.x - 80
            right = self.x

        bottom = self.y - 40
        top    = self.y + 60
        return (left, bottom, right, top)

    # === 공격 데미지 ===
    def get_attack_damage(self):
        s = self.state_machine.cur_state
        if s is self.ATTACK:
            return 6
        elif s is self.ATTACK2:
            return 8
        elif s is self.SKILL:
            return 13
        elif s is self.SKILL2:
            return 15
        elif s is self.SKILL3:
            return 22
        return 0

    # === 피격 ===
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        print(f'Tamama hit! hp = {self.hp}')

    def _ensure_image(self):
        if self.image is None:
            self.image = load_image(self.image_name)

    def update(self):
        # 몸통 충돌 막기 위한 이전 위치 저장
        self.prev_x = self.x
        self.prev_y = self.y

        self.state_machine.update()

    def draw(self):
        self._ensure_image()
        self.state_machine.draw()

        if DEBUG_COLLISION:
            draw_bb(self.get_body_bb())
            atk_bb = self.get_attack_bb()
            if atk_bb:
                draw_bb(atk_bb)

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


tamama = Tamama()
