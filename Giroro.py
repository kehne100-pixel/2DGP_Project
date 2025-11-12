from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a
from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def Time_out(e):   return e[0] == 'TIME_OUT'

IMAGE_W, IMAGE_H = 996, 1917
CELL_W, CELL_H = 40, 80
DRAW_W, DRAW_H = 130, 130

def row_y_from_top(row_from_top):
    return IMAGE_H - (row_from_top + 1) * CELL_H

SPRITE = {
    'idle': {'row': 0, 'start_col': 0, 'frames': 4, 'flip_when_left': True},
    'run': {
        'rects': [
            (4, 1544, 60, 60),
            (67, 1544, 60, 60),
            (132, 1544, 60, 60),
            (198, 1544, 60, 60),
        ],
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


class Idle:
    def __init__(self, Giroro):
        self.Giroro = Giroro
        self.frame = 0
        self.frame_count = 4

    def enter(self, e):
        self.Giroro.dir = 0
        self.Giroro.wait_start_time = get_time()
        self.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + 1) % self.frame_count

    def draw(self):
        self.Giroro._ensure_image()

        if self.Giroro.face_dir == 1:
            if self.frame == 0:
                self.Giroro.image.clip_draw(0, 2621, 50, 60, self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 1:
                self.Giroro.image.clip_draw(49, 2621, 50, 60, self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 2:
                self.Giroro.image.clip_draw(99, 2621, 50, 60, self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 3:
                self.Giroro.image.clip_draw(149, 2621, 50, 60, self.Giroro.x, self.Giroro.y, 100, 100)
        else:
            if self.frame == 0:
                self.Giroro.image.clip_composite_draw(0, 2621, 50, 60, 0, 'h', self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 1:
                self.Giroro.image.clip_composite_draw(49, 2621, 50, 60, 0, 'h', self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 2:
                self.Giroro.image.clip_composite_draw(99, 2621, 50, 60, 0, 'h', self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 3:
                self.Giroro.image.clip_composite_draw(149, 2621, 50, 60, 0, 'h', self.Giroro.x, self.Giroro.y, 100, 100)


class Run:
    def __init__(self, Giroro):
        self.Giroro = Giroro
        self.frame = 0
        self.frame_count = 4
        self.SPEED = 8

    def enter(self, e):
        self.frame = 0
        if e and e[0] == 'INPUT':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_RIGHT:
                    self.Giroro.dir = 1
                    self.Giroro.face_dir = 1
                elif ev.key == SDLK_LEFT:
                    self.Giroro.dir = -1
                    self.Giroro.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.frame = (self.frame + 1) % self.frame_count
        self.Giroro.x += self.Giroro.dir * self.SPEED
        self.Giroro.x = max(50, min(1550, self.Giroro.x))

    def draw(self):
        self.Giroro._ensure_image()
        draw_from_cfg(self.Giroro.image, 'run', self.frame,
                      self.Giroro.face_dir, self.Giroro.x, self.Giroro.y, 100, 100)
        if self.Giroro.dir == 1:
            if self.frame == 0:
                self.Giroro.image.clip_draw(0, 2322, 50, 58, self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 1:
                self.Giroro.image.clip_draw(49, 2322, 50, 58, self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 2:
                self.Giroro.image.clip_draw(99, 2322, 50, 58, self.Giroro.x, self.Giroro.y, 100, 100)
            elif self.frame == 3:
                self.Giroro.image.clip_draw(149, 2322, 50, 58, self.Giroro.x, self.Giroro.y, 100, 100)


class AutoRun:
    def __init__(self, Giroro):
        self.Giroro = Giroro

    def enter(self, e):
        self.start_time = get_time()
        self.Giroro.dir = -1
        self.Giroro.face_dir = -1

    def exit(self, e):
        self.Giroro.dir = 0

    def do(self):
        self.Giroro.frame = (self.Giroro.frame + 1) % SPRITE['run']['frames']
        self.Giroro.x += self.Giroro.dir * 10
        self.Giroro.x = max(50, min(1550, self.Giroro.x))

    def draw(self):
        self.Giroro._ensure_image()
        draw_from_cfg(self.Giroro.image, 'run', self.Giroro.frame,
                      self.Giroro.face_dir, self.Giroro.x, self.Giroro.y,
                      DRAW_W + 8, DRAW_H + 8)


class Giroro:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.image_name = 'Giroro_Sheet.png'
        self.image = None

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.AUTORUN = AutoRun(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, a_down: self.AUTORUN},
                self.RUN: {
                    right_up: self.IDLE,
                    left_up: self.IDLE,
                    right_down: self.RUN,
                    left_down: self.RUN,
                    a_down: self.AUTORUN
                },
                self.AUTORUN: {Time_out: self.IDLE, right_down: self.RUN, left_down: self.RUN}
            }
        )

    def _ensure_image(self):
        if self.image is None:
            self.image = load_image(self.image_name)

    def update(self): self.state_machine.update()
    def draw(self):
        self._ensure_image()
        self.state_machine.draw()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


#Giroro = Giroro()
