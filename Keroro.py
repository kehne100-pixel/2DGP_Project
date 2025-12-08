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


# -----------------------------
# 이벤트 체크 함수들
# -----------------------------
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

# ❗ 맞았을 때 / Hit 끝났을 때
def got_hit(e):   return e[0] == 'GOT_HIT'
def hit_end(e):   return e[0] == 'HIT_END'


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

    'skill': {
        'rects': [
            (18, 756, 48, 54),
            (87, 756, 90, 58),
            (193, 756, 66, 59),
            (265, 756, 58, 58),
            (352, 756, 89, 58),
            (458, 756, 65, 59),
            (547, 756, 37, 75),
            (639, 756, 59, 58),
            (731, 756, 46, 70),
        ],
        'frames': 9,
        'flip_when_left': True
    },

    'skill2': {
        'rects': [
            (24, 343, 44, 51),
            (123, 344, 74, 43),
            (205, 346, 53, 54),
            (296, 344, 60, 57),
            (391, 328, 100, 63),
            (515, 344, 59, 53),
            (611, 344, 46, 50),
            (710, 344, 47, 46),
            (24, 271, 71, 48),
            (121, 271, 73, 47),
            (220, 271, 72, 45),
        ],
        'frames': 11,
        'flip_when_left': True
    },

    'skill3': {
        'rects': [
            (0, 1, 47, 58),
            (80, 3, 63, 47),
            (149, 3, 66, 46),
        ],
        'frames': 3,
        'flip_when_left': True
    },


    'hit': {
        'rects': [
            (207, 1470, 48, 63),
        ],
        'frames': 1,
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


# -----------------------------
# 상태 클래스들
# -----------------------------
class Idle:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['idle']['frames']

    def enter(self, e):
        self.keroro.dir = 0
        self.keroro.wait_start_time = get_time()
        self.frame = 0.0

        self.keroro.is_attacking = False
        self.keroro.attack_hit_done = False

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

        self.move_during_attack = (self.keroro.dir != 0)

        # 공격 시작
        self.keroro.is_attacking = True
        self.keroro.attack_hit_done = False

    def exit(self, e):
        # 공격 끝
        self.keroro.is_attacking = False

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

        self.keroro.is_attacking = True
        self.keroro.attack_hit_done = False

    def exit(self, e):
        self.keroro.is_attacking = False

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

        offset = 50
        if self.keroro.face_dir == -1:
            draw_from_cfg(
                self.keroro.image,
                'attack2',
                idx,
                self.keroro.face_dir,
                self.keroro.x - offset,
                self.keroro.y,
                110, 100
            )
        else:
            draw_from_cfg(
                self.keroro.image,
                'attack2',
                idx,
                self.keroro.face_dir,
                self.keroro.x + offset,
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
        self.keroro.dir = 0

        self.keroro.is_attacking = False
        self.keroro.attack_hit_done = False

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

        self.keroro.is_attacking = False
        self.keroro.attack_hit_done = False

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
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.keroro.y += self.keroro.vy
        self.keroro.vy += self.GRAVITY

        if self.keroro.y <= self.keroro.ground_y:
            self.keroro.y = self.keroro.ground_y
            self.keroro.vy = 0

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


class Skill:
    def __init__(self, keroro):
        self.keroro = keroro
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

        if self.keroro.face_dir != 0:
            self.keroro.dir = self.keroro.face_dir

        self.move_during_skill = (self.keroro.dir != 0)

        self.keroro.is_attacking = True
        self.keroro.attack_hit_done = False

    def exit(self, e):
        self.keroro.dir = 0
        self.keroro.is_attacking = False

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_skill:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.keroro.dir != 0:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.keroro.image,
            'skill',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Skill2:
    def __init__(self, keroro):
        self.keroro = keroro
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

        if self.keroro.face_dir != 0:
            self.keroro.dir = self.keroro.face_dir

        self.move_during_skill = (self.keroro.dir != 0)

        self.keroro.is_attacking = True
        self.keroro.attack_hit_done = False

    def exit(self, e):
        self.keroro.dir = 0
        self.keroro.is_attacking = False

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_skill:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.keroro.dir != 0:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.keroro.image,
            'skill2',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Skill3:
    def __init__(self, keroro):
        self.keroro = keroro
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

        if self.keroro.face_dir != 0:
            self.keroro.dir = self.keroro.face_dir

        self.move_during_skill = (self.keroro.dir != 0)

        self.keroro.is_attacking = True
        self.keroro.attack_hit_done = False

    def exit(self, e):
        self.keroro.dir = 0
        self.keroro.is_attacking = False

    def do(self):
        if not self.finished:
            if self.start_timer < self.start_hold_time:
                self.start_timer += game_framework.frame_time
                return

            self.frame += self.anim_speed

            if self.move_during_skill:
                self.keroro.x += self.keroro.dir * self.SPEED
                self.keroro.x = max(50, min(1550, self.keroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.keroro.dir != 0:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.keroro.image,
            'skill3',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y + 10,
            skill_draw_w,
            skill_draw_h
        )


# -----------------------------
# Hit 상태 (맞았을 때)
# -----------------------------
class Hit:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0.0
        self.frame_count = SPRITE['hit']['frames']
        self.anim_speed = 0.2

        self.timer = 0.0
        self.duration = 0.3
        self.knockback_speed = 5.0
        self.knock_dir = 0

    def enter(self, e):
        self.frame = 0.0
        self.timer = 0.0

        self.keroro.is_attacking = False
        self.keroro.attack_hit_done = False

        self.knock_dir = self.keroro.hit_from_dir if hasattr(self.keroro, 'hit_from_dir') else 0

    def exit(self, e):
        pass

    def do(self):
        self.timer += game_framework.frame_time
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.keroro.x += self.knock_dir * self.knockback_speed
        self.keroro.x = max(50, min(1550, self.keroro.x))

        if self.timer >= self.duration:
            self.keroro.state_machine.handle_state_event(('HIT_END', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.keroro.image,
            'hit',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
        )


# -----------------------------
# Keroro 본체
# -----------------------------
class Keroro:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.vy = 0.0
        self.ground_y = 90

        self.image_name = 'Keroro_Sheet.png'
        self.image = None

        # HP, 공격 관련
        self.hp = 100
        self.is_attacking = False
        self.attack_hit_done = False
        self.hit_from_dir = 0

        # 상태 인스턴스
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
        self.HIT     = Hit(self)

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
                    got_hit:     self.HIT,
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
                    got_hit:     self.HIT,
                },

                self.ATTACK: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                    got_hit:          self.HIT,
                },

                self.ATTACK2: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                    got_hit:          self.HIT,
                },

                self.GUARD: {
                    a_up:   self.IDLE,
                    got_hit: self.HIT,
                },

                self.JUMP: {
                    jump_to_fall: self.FALL,
                    got_hit:      self.HIT,
                },

                self.FALL: {
                    land_idle: self.IDLE,
                    land_run:  self.RUN,
                    got_hit:   self.HIT,
                },

                self.SKILL: {
                    attack_done_idle: self.IDLE,
                    got_hit:          self.HIT,
                },

                self.SKILL2: {
                    attack_done_idle: self.IDLE,
                    got_hit:          self.HIT,
                },

                self.SKILL3: {
                    attack_done_idle: self.IDLE,
                    got_hit:          self.HIT,
                },

                self.HIT: {
                    hit_end: self.IDLE,
                    got_hit: self.HIT,
                },
            }
        )

    def _ensure_image(self):
        if self.image is None:
            self.image = load_image(self.image_name)

    # --------- 충돌 박스들 ---------
    def get_hurtbox(self):
        """몸통 피격 박스"""
        w = 40
        h = 80
        left   = self.x - w / 2
        right  = self.x + w / 2
        bottom = self.y - 10
        top    = bottom + h
        return (left, bottom, right, top)

    def get_attack_hitbox(self):
        """공격 판정 박스 (is_attacking & hit_done==False 일 때만 유효)"""
        if not self.is_attacking or self.attack_hit_done:
            return None

        range_x = 70
        w = 40
        h = 80
        bottom = self.y - 10
        top    = bottom + h

        if self.face_dir >= 0:
            left  = self.x
            right = self.x + range_x
        else:
            left  = self.x - range_x
            right = self.x

        return (left, bottom, right, top)

    def take_hit(self, damage, attacker_dir):
        """피격 처리 (play_mode에서 호출)"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

        self.hit_from_dir = attacker_dir if attacker_dir is not None else 0

        self.is_attacking = False
        self.attack_hit_done = False

        self.state_machine.handle_state_event(('GOT_HIT', None))

    # -----------------------------
    def update(self):
        self.state_machine.update()

    def draw(self):
        self._ensure_image()
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


keroro = Keroro()
