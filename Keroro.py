from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a, SDLK_s
from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def s_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s
def Time_out(e):   return e[0] == 'TIME_OUT'
def attack_done_idle(e): return e[0] == 'ATTACK_DONE_IDLE'
def attack_done_run(e):  return e[0] == 'ATTACK_DONE_RUN'



# ---------------------------
IMAGE_W, IMAGE_H = 996, 1917
CELL_W, CELL_H   = 40, 80
DRAW_W, DRAW_H   = 130, 130


def row_y_from_top(row_from_top):
    return IMAGE_H - (row_from_top + 1) * CELL_H


SPRITE = {
    'idle': {'row': 0, 'start_col': 0, 'frames': 4, 'flip_when_left': True},

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
             (4, 1226, 61, 80),
             (65, 1226, 61, 80),
             (138, 1226, 61, 80),

        ],

        'frames': 3,
        'flip_when_left': True
    },
}


def draw_from_cfg(image, key, frame_idx, face_dir, x, y, draw_w=DRAW_W, draw_h=DRAW_H):
    cfg = SPRITE[key]

    if 'rects' in cfg:
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


# ---------------------------

class Idle:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0
        self.frame_count = 4

    def enter(self, e):
        self.keroro.dir = 0
        self.keroro.wait_start_time = get_time()
        self.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + 1) % self.frame_count

    def draw(self):
        self.keroro._ensure_image()

        if self.keroro.face_dir == 1:
            if self.frame == 0:
                self.keroro.image.clip_draw(4, 1842, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 1:
                self.keroro.image.clip_draw(67, 1842, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 2:
                self.keroro.image.clip_draw(132, 1842, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 3:
                self.keroro.image.clip_draw(198, 1842, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
        else:
            if self.frame == 0:
                self.keroro.image.clip_composite_draw(4, 1842, 60, 60, 0, 'h', self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 1:
                self.keroro.image.clip_composite_draw(67, 1842, 60, 60, 0, 'h', self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 2:
                self.keroro.image.clip_composite_draw(132, 1842, 60, 60, 0, 'h', self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 3:
                self.keroro.image.clip_composite_draw(198, 1842, 60, 60, 0, 'h', self.keroro.x, self.keroro.y, 100, 100)


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
        self.keroro.x = max(50, min(1550, self.keroro.x))  # 화면 전체 이동 허용

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
        self.frame = 0
        self.frame_count = SPRITE['attack']['frames']
        self.SPEED = 8       # 달리면서 공격할 때 속도
        self.move_during_attack = False  # 공격 중 이동할지 여부

    def enter(self, e):
        # 공격 시작 시 프레임 초기화
        self.frame = 0
        # 현재 방향 유지
        # 지금 dir 이 0 이면 (Idle) 제자리 공격,
        # 0이 아니면 (Run/AutoRun) 달리면서 공격
        self.move_during_attack = (self.keroro.dir != 0)

    def exit(self, e):
        pass

    def do(self):
        # 프레임 진행
        self.frame += 1

        # 달리면서 공격해야 하는 경우에만 이동
        if self.move_during_attack:
            self.keroro.x += self.keroro.dir * self.SPEED
            self.keroro.x = max(50, min(1550, self.keroro.x))

        # 공격 애니메이션 끝났을 때
        if self.frame >= self.frame_count:
            self.frame = self.frame_count - 1
            if self.move_during_attack:
                # 달리던 중에 공격 → 다시 Run 으로
                self.keroro.state_machine.handle_state_event(('ATTACK_DONE_RUN', None))
            else:
                # Idle 상태에서 공격 → 다시 Idle 로
                self.keroro.state_machine.handle_state_event(('ATTACK_DONE_IDLE', None))

    def draw(self):
        self.keroro._ensure_image()
        idx = min(self.frame, self.frame_count - 1)

        draw_from_cfg(
            self.keroro.image,
            'attack',
            idx,
            self.keroro.face_dir,
            self.keroro.x,
            self.keroro.y,
            100, 100
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

        self.state_machine = StateMachine(
            self.IDLE,
            {

                self.IDLE: {
                    right_down: self.RUN,
                    left_down:  self.RUN,
                    a_down:     self.AUTORUN,
                    s_down:     self.ATTACK,   # S → Attack
                },


                self.RUN: {
                    right_up:   self.IDLE,
                    left_up:    self.IDLE,
                    right_down: self.RUN,
                    left_down:  self.RUN,
                    a_down:     self.AUTORUN,
                    s_down:     self.ATTACK,   # 달리는 중에도 S → Attack
                },

                # AutoRun 상태에서
                self.AUTORUN: {
                    Time_out:   self.IDLE,
                    right_down: self.RUN,
                    left_down:  self.RUN,
                    s_down:     self.ATTACK,
                },

                self.ATTACK: {
                    attack_done_idle: self.IDLE,  # Idle 에서 공격 → 다시 Idle
                    attack_done_run: self.RUN,  # Run 중 공격 → 다시 Run
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
