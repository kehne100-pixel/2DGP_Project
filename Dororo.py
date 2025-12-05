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
            (0,   2882, 42, 48),
            (43,  2882, 41, 49),
            (85, 2882, 42, 49),
            (135, 2883, 41, 48),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'run': {
        'rects': [
            (0,   2709, 52, 46),
            (58,  2711, 50, 44),
            (112, 2710, 49, 45),
            (165, 2711, 50, 44),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'attack': {
        'rects': [
            (0,   2582, 47, 46),
            (54,  2582, 70, 50),
            (127, 2582, 54, 50),
            (186, 2581, 40, 51),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'attack2': {
        'rects': [
            (4, 2514, 41, 50),
            (48, 2514, 64, 54),
            (120, 2514, 53, 56),

        ],
        'frames': 3,
        'flip_when_left': True
    },

    'guard': {
        'rects': [
            (0, 2342, 42, 51),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'jump': {
        'rects': [
            (0, 2642, 40, 43),
            (45, 2642, 37, 60),
            (87, 2642, 40 ,60),
            (131, 2658, 42, 44),
            (176, 2659, 40, 49),
        ],
        'frames': 5,
        'flip_when_left': True
    },

    'fall': {
        'rects': [
            (263, 2639, 42, 68),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'skill': {
        'rects': [
            (0, 2118, 47, 45),
            (50, 2117, 71, 53),
            (123, 2118, 65, 48),
        ],
        'frames': 3,
        'flip_when_left': True
    },

    'skill2': {
        'rects': [
            (0, 2034, 40, 50),
            (42, 2034, 82, 65),
            (139, 2020, 65, 80),
            (213, 2046, 82, 65),
            (301, 2036, 66, 81),
            (377, 2049, 62, 49),
            (454, 2034, 51, 53),
            (508, 2035, 43, 46),
            (559, 2034, 39, 44),
            (612, 2033, 37, 58),
        ],
        'frames': 10,
        'flip_when_left': True
    },

    'skill3': {
        'rects': [
            (278, 2281, 40, 47),
            (320, 2281, 46, 61),
            (371, 2281 ,43, 61),
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
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0.0
        self.frame_count = SPRITE['idle']['frames']

    def enter(self, e):
        self.dororo.dir = 0
        self.dororo.wait_start_time = get_time()
        self.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + idle_frame_per_second * game_framework.frame_time) % self.frame_count

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.dororo.image,
            'idle',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y,
            100, 100
        )


class Run:
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0
        self.frame_count = SPRITE['run']['frames']
        self.SPEED = 2

    def enter(self, e):
        self.frame = 0

        if e and e[0] == 'INPUT':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_RIGHT:
                    self.dororo.dir = 1
                    self.dororo.face_dir = 1
                elif ev.key == SDLK_LEFT:
                    self.dororo.dir = -1
                    self.dororo.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + Run_frame_per_second * game_framework.frame_time) % self.frame_count
        self.dororo.x += self.dororo.dir * self.SPEED
        self.dororo.x = max(50, min(1550, self.dororo.x))

    def draw(self):
        self.dororo._ensure_image()
        draw_from_cfg(
            self.dororo.image,
            'run',
            self.frame,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y,
            100, 100
        )


class Attack:
    def __init__(self, dororo):
        self.dororo = dororo

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

        self.move_during_attack = (self.dororo.dir != 0)

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
                    dx = self.dororo.dir * (self.SPEED * 0.3)
                elif self.frame == 1:
                    dx = self.dororo.dir * (self.SPEED * 1.0)
                elif self.frame == 2:
                    dx = self.dororo.dir * (self.SPEED * 0.1)
                else:
                    dx = 0

                self.dororo.x += dx
                self.dororo.x = max(50, min(1550, self.dororo.x))
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                # ★ 항상 Idle 로
                self.dororo.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame)

        draw_from_cfg(
            self.dororo.image,
            'attack',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y,
            110, 110
        )


class Attack2:
    def __init__(self, dororo):
        self.dororo = dororo
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

        self.move_during_attack = (self.dororo.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.dororo.x += self.dororo.dir * self.SPEED
                self.dororo.x = max(50, min(1550, self.dororo.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                # ★ Attack2도 항상 Idle 로
                self.dororo.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame)

        if self.dororo.face_dir == -1:
            draw_from_cfg(
                self.dororo.image,
                'attack2',
                idx,
                self.dororo.face_dir,
                self.dororo.x - 50,
                self.dororo.y,
                110, 100
            )
        else:
            draw_from_cfg(
                self.dororo.image,
                'attack2',
                idx,
                self.dororo.face_dir,
                self.dororo.x + 50,
                self.dororo.y,
                110, 100
            )


class Guard:
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.anim_speed = 0.15

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.dororo.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.dororo.image,
            'guard',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y,
            100, 100
        )


class Jump:
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']
        self.anim_speed = 0.2

        self.JUMP_POWER = 18
        self.GRAVITY    = -0.5

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']

        self.dororo.vy = self.JUMP_POWER

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.dororo.y += self.dororo.vy
        self.dororo.vy += self.GRAVITY

        if self.dororo.vy <= 0:
            self.dororo.state_machine.handle_state_event(('JUMP_TO_FALL', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.dororo.image,
            'jump',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y,
            100, 100
        )


class Fall:
    def __init__(self, dororo):
        self.dororo = dororo
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

        self.dororo.y += self.dororo.vy
        self.dororo.vy += self.GRAVITY

        if self.dororo.y <= self.dororo.ground_y:
            self.dororo.y = self.dororo.ground_y
            self.dororo.vy = 0

            if self.dororo.dir != 0:
                self.dororo.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.dororo.state_machine.handle_state_event(('LAND_IDLE', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.dororo.image,
            'fall',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y,
            100, 100
        )


class Skill:
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0.0
        self.frame_count = SPRITE['skill']['frames']

        # 🔥 달리면서 나가는 스킬 속도 (크게 할수록 더 멀리 전진)
        self.RUN_SPEED = 4.0   # 필요하면 5.0, 6.0 으로 더 올려봐도 됨

        self.anim_speed = 0.06
        self.finished = False

        self.hold_time = 0.4      # 스킬 끝나고 살짝 멈춰주는 시간
        self.hold_timer = 0.0

        self.move_during_skill = False

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        # 🔹 방향 유지: 달리다가 쓰면 달리던 방향 그대로,
        #   제자리에서 쓰면 바라보는 방향(face_dir)으로 살짝 앞으로 이동
        if self.dororo.dir == 0:
            # 안 움직이고 있었으면 바라보는 방향으로 움직이게
            if self.dororo.face_dir != 0:
                self.dororo.dir = self.dororo.face_dir
            else:
                self.dororo.dir = 1  # 혹시 face_dir이 0이면 기본 오른쪽

        self.move_during_skill = True

    def exit(self, e):
        # 스킬 끝나면 멈추고 Idle로 돌아가니까 방향 0
        self.dororo.dir = 0
        self.move_during_skill = False

    def do(self):
        if not self.finished:
            # ⭐ 스킬 애니메이션 진행되는 동안 계속 앞으로 달리는 느낌
            if self.move_during_skill:
                self.dororo.x += self.dororo.dir * self.RUN_SPEED
                self.dororo.x = max(50, min(1550, self.dororo.x))

            # 애니메이션 프레임 진행
            self.frame += self.anim_speed

            # 애니메이션이 끝까지 재생되면 finished 처리
            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            # 마지막 포즈 잠깐 유지 후 Idle 로 복귀
            self.hold_timer += game_framework.frame_time
            if self.hold_timer >= self.hold_time:
                self.dororo.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.dororo.image,
            'skill',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y + 10,
            skill_draw_w,
            skill_draw_h
        )




class Skill2:
    def __init__(self, dororo):
        self.dororo = dororo
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

        self.dororo.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.dororo.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                self.dororo.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.dororo.image,
            'skill2',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Skill3:
    def __init__(self, dororo):
        self.dororo = dororo
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

        self.dororo.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        self.dororo.dir = 0

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
                self.dororo.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.dororo._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.dororo.image,
            'skill3',
            idx,
            self.dororo.face_dir,
            self.dororo.x,
            self.dororo.y + 10,
            skill_draw_w,
            skill_draw_h
        )


class Dororo:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.vy = 0.0
        self.ground_y = 90

        self.image_name = 'Dororo_Sheet.png'
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
                    attack_done_run:  self.IDLE,   # ★ 공격 끝나면 항상 IDLE
                },

                self.ATTACK2: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.IDLE,
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

    def update(self):
        self.state_machine.update()

    def draw(self):
        self._ensure_image()
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


dororo = Dororo()
