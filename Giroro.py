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
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a   # Guard 시작
def a_up(e):       return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_a   # Guard 해제
def s_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s   # Attack
def d_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d   # Attack2
def space_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE  # 점프
def Time_out(e):   return e[0] == 'TIME_OUT'
def attack_done_idle(e): return e[0] == 'ATTACK_DONE_IDLE'
def attack_done_run(e):  return e[0] == 'ATTACK_DONE_RUN'
def jump_to_fall(e): return e[0] == 'JUMP_TO_FALL'   # Jump → Fall
def land_idle(e):    return e[0] == 'LAND_IDLE'      # Fall → Idle
def land_run(e):     return e[0] == 'LAND_RUN'       # Fall → Run


def skill_down(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_1
# 숫자 2 키 스킬2
def skill2_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_2
# 숫자 3 키 스킬3
def skill3_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_3


IMAGE_W, IMAGE_H = 996, 1917
CELL_W, CELL_H   = 40, 80
DRAW_W, DRAW_H   = 130, 130


def row_y_from_top(row_from_top):
    return IMAGE_H - (row_from_top + 1) * CELL_H


SPRITE = {
    'idle': {
        'rects': [
            (0,   2614, 49, 56),
            (50,  2613, 49, 58),
            (103, 2612, 50, 59),
            (155, 2614, 54, 56),
        ],
        'frames': 4,
        'flip_when_left': True
    },

    'run': {
        'rects': [
            (528,   2400, 39, 57),
            (576,  2402, 40, 54),
            (629, 2400, 40, 55),
            (678, 2403, 38, 53),
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
            (0, 2066, 40, 56),
        ],
        'frames': 1,
        'flip_when_left': True
    },

    'jump': {
        'rects': [
            (0, 2366, 44, 49),
            (48, 2369, 52, 59),
            (102, 2367, 50, 61),
            (155, 2368, 51, 57),


        ],
        'frames': 4,
        'flip_when_left': True
    },

    'fall': {
        'rects': [
            (213, 2368, 53, 59),
            (271, 2366, 53, 60),
            (331, 2365, 49, 53),
            (387, 2365, 44, 50),
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

    # 스킬2
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

            (228, 2006, 41, 50),
            (271, 2005, 48, 59),
            (321, 2006 ,46, 58),

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
    def __init__(self, giroro):
        self.giroro = giroro
        self.frame = 0.0
        self.frame_count = SPRITE['idle']['frames']

    def enter(self, e):
        self.giroro.dir = 0
        self.giroro.wait_start_time = get_time()
        self.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + idle_frame_per_second * game_framework.frame_time) % self.frame_count

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.giroro.image,
            'idle',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y,
            100, 100
        )


class Run:
    def __init__(self, giroro):
        self.giroro = giroro
        self.frame = 0
        self.frame_count = SPRITE['run']['frames']
        self.SPEED = 2

    def enter(self, e):
        self.frame = 0

        if e and e[0] == 'INPUT':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_RIGHT:
                    self.giroro.dir = 1
                    self.giroro.face_dir = 1
                elif ev.key == SDLK_LEFT:
                    self.giroro.dir = -1
                    self.giroro.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + Run_frame_per_second * game_framework.frame_time) % self.frame_count
        self.giroro.x += self.giroro.dir * self.SPEED
        self.giroro.x = max(50, min(1550, self.giroro.x))

    def draw(self):
        self.giroro._ensure_image()
        draw_from_cfg(
            self.giroro.image,
            'run',
            self.frame,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y,
            100, 100
        )




class Attack:
    def __init__(self, giroro):
        self.giroro = giroro
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

        self.move_during_attack = (self.giroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:

            self.frame += self.anim_speed

            if self.move_during_attack:
                self.giroro.x += self.giroro.dir * self.SPEED
                self.giroro.x = max(50, min(1550, self.giroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame)

        draw_from_cfg(
            self.giroro.image,
            'attack',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y,
            100, 100
        )


class Attack2:
    def __init__(self, giroro):
        self.giroro = giroro
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

        self.move_during_attack = (self.giroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_attack:
                self.giroro.x += self.giroro.dir * self.SPEED
                self.giroro.x = max(50, min(1550, self.giroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.move_during_attack:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame)

        if self.giroro.face_dir == -1:
            draw_from_cfg(
                self.giroro.image,
                'attack2',
                idx,
                self.giroro.face_dir,
                self.giroro.x - 50,
                self.giroro.y,
                110, 100
            )
        else:
            draw_from_cfg(
                self.giroro.image,
                'attack2',
                idx,
                self.giroro.face_dir,
                self.giroro.x + 50,
                self.giroro.y,
                110, 100
            )



class Guard:

    def __init__(self, giroro):
        self.giroro = giroro
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.anim_speed = 0.15

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['guard']['frames']
        self.giroro.dir = 0  # 가드 중엔 이동 안 함

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + self.anim_speed) % self.frame_count

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.giroro.image,
            'guard',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y,
            100, 100
        )



class Jump:

    def __init__(self, giroro):
        self.giroro = giroro
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']
        self.anim_speed = 0.2

        self.JUMP_POWER = 18
        self.GRAVITY    = -0.5

    def enter(self, e):
        self.frame = 0.0
        self.frame_count = SPRITE['jump']['frames']

        self.giroro.vy = self.JUMP_POWER

    def exit(self, e):
        pass

    def do(self):

        self.frame = (self.frame + self.anim_speed) % self.frame_count

        self.giroro.y += self.giroro.vy
        self.giroro.vy += self.GRAVITY

        if self.giroro.vy <= 0:
            self.giroro.state_machine.handle_state_event(('JUMP_TO_FALL', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.giroro.image,
            'jump',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y,
            100, 100
        )


class Fall:

    def __init__(self, giroro):
        self.giroro = giroro
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

        self.giroro.y += self.giroro.vy
        self.giroro.vy += self.GRAVITY

        if self.giroro.y <= self.giroro.ground_y:
            self.giroro.y = self.giroro.ground_y
            self.giroro.vy = 0

            if self.giroro.dir != 0:
                self.giroro.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.giroro.state_machine.handle_state_event(('LAND_IDLE', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        draw_from_cfg(
            self.giroro.image,
            'fall',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y,
            100, 100
        )




class Skill:

    def __init__(self, giroro):
        self.giroro = giroro
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

        # ★ 제자리 스킬: 이동 방향 없애기
        self.giroro.dir = 0
        self.move_during_skill = False

    def exit(self, e):
        # 스킬 종료 후에도 이동 방향 0 유지
        self.giroro.dir = 0

    def do(self):
        if not self.finished:

            self.frame += self.anim_speed



            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.giroro.dir != 0:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.giroro.image,
            'skill',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y + 10,
            skill_draw_w,
            skill_draw_h
        )




# 숫자 2 스킬 상태
class Skill2:

    def __init__(self, giroro):
        self.giroro = giroro
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

        if self.giroro.face_dir != 0:
            self.giroro.dir = self.giroro.face_dir

        self.move_during_skill = (self.giroro.dir != 0)

    def exit(self, e):
        self.giroro.dir = 0

    def do(self):
        if not self.finished:
            self.frame += self.anim_speed

            if self.move_during_skill:
                self.giroro.x += self.giroro.dir * self.SPEED
                self.giroro.x = max(50, min(1550, self.giroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.giroro.dir != 0:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.giroro.image,
            'skill2',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y + 10,
            skill_draw_w,
            skill_draw_h
        )



class Skill3:

    def __init__(self, giroro):
        self.giroro = giroro
        self.frame = 0.0
        self.frame_count = SPRITE['skill3']['frames']

        self.SPEED = 6
        self.move_during_skill = False

        self.anim_speed = 0.18
        self.finished = False

        self.hold_time = 0.35
        self.hold_timer = 0.0

        # ★ 첫 동작(프레임 0)을 얼마나 보여줄지
        self.start_hold_time = 0.15   # 0.15초 정도 시전 준비 포즈 유지
        self.start_timer = 0.0

    def enter(self, e):
        self.frame = 0.0
        self.finished = False
        self.hold_timer = 0.0

        # ★ 타이머 초기화
        self.start_timer = 0.0

        if self.giroro.face_dir != 0:
            self.giroro.dir = self.giroro.face_dir

        self.move_during_skill = (self.giroro.dir != 0)

    def exit(self, e):
        self.giroro.dir = 0

    def do(self):
        if not self.finished:

            # ★ 여기서 일정 시간 동안 0번 프레임 고정
            if self.start_timer < self.start_hold_time:
                self.start_timer += game_framework.frame_time
                # frame은 0 그대로 두고, 아래 코드 실행 안 함
                return

            # 그 다음부터 프레임을 넘기기 시작
            self.frame += self.anim_speed

            if self.move_during_skill:
                self.giroro.x += self.giroro.dir * self.SPEED
                self.giroro.x = max(50, min(1550, self.giroro.x))

            if self.frame >= self.frame_count:
                self.frame = self.frame_count - 1
                self.finished = True
        else:
            self.hold_timer += game_framework.frame_time

            if self.hold_timer >= self.hold_time:
                if self.giroro.dir != 0:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
                else:
                    self.giroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.giroro._ensure_image()
        idx = int(self.frame) % self.frame_count

        skill_draw_w = 110
        skill_draw_h = 110

        draw_from_cfg(
            self.giroro.image,
            'skill3',
            idx,
            self.giroro.face_dir,
            self.giroro.x,
            self.giroro.y + 10,
            skill_draw_w,
            skill_draw_h
        )


# ---------------------------
# Giroro 본체
# ---------------------------
class Giroro:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.vy = 0.0
        self.ground_y = 90

        self.image_name = 'Giroro_Sheet.png'
        self.image = None

        # 상태 인스턴스
        self.IDLE        = Idle(self)
        self.RUN         = Run(self)
        self.ATTACK      = Attack(self)
        self.ATTACK2     = Attack2(self)
        self.GUARD       = Guard(self)
        self.JUMP        = Jump(self)
        self.FALL        = Fall(self)
        self.SKILL       = Skill(self)    # 1번 스킬
        self.SKILL2      = Skill2(self)   # 2번 스킬
        self.SKILL3      = Skill3(self)   # 3번 스킬

        self.state_machine = StateMachine(
            self.IDLE,
            {

                # Idle 상태
                self.IDLE: {
                    right_down:     self.RUN,
                    left_down:      self.RUN,
                    a_down:         self.GUARD,
                    s_down:         self.ATTACK,
                    d_down:         self.ATTACK2,
                    space_down:     self.JUMP,
                    skill_down:     self.SKILL,     # 1
                    skill2_down:    self.SKILL2,    # 2
                    skill3_down:    self.SKILL3,    # 3
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
                    space_down:     self.JUMP,
                    skill_down:     self.SKILL,
                    skill2_down:    self.SKILL2,
                    skill3_down:    self.SKILL3,
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
                    a_up:           self.IDLE,
                },

                # Jump 상태
                self.JUMP: {
                    jump_to_fall:   self.FALL,
                },

                # Fall 상태
                self.FALL: {
                    land_idle:      self.IDLE,
                    land_run:       self.RUN,
                },

                # Skill1 상태
                self.SKILL: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                # Skill2 상태
                self.SKILL2: {
                    attack_done_idle: self.IDLE,
                    attack_done_run:  self.RUN,
                },

                # Skill3 상태
                self.SKILL3: {
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


giroro = Giroro()
