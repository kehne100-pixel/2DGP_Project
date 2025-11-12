from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a
from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def Time_out(e):   return e[0] == 'TIME_OUT'


class Idle:
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0
        self.frame_count = 4

    def enter(self, e):
        self.dororo.dir = 0
        self.frame = 0

    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 1) % self.frame_count

    def draw(self):
        self.dororo._ensure_image()
        if self.dororo.face_dir == 1:
            self.dororo.image.clip_draw(0, 0, 60, 60, self.dororo.x, self.dororo.y, 100, 100)
        else:
            self.dororo.image.clip_composite_draw(0, 0, 60, 60, 0, 'h', self.dororo.x, self.dororo.y, 100, 100)


class Run:
    def __init__(self, dororo):
        self.dororo = dororo
        self.frame = 0
        self.frame_count = 4
        self.SPEED = 8

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

    def exit(self, e): pass
    def do(self):
        self.frame = (self.frame + 1) % self.frame_count
        self.dororo.x += self.dororo.dir * self.SPEED
        self.dororo.x = max(50, min(1550, self.dororo.x))

    def draw(self):
        self.dororo._ensure_image()
        if self.dororo.face_dir == 1:
            self.dororo.image.clip_draw(0, 0, 60, 60, self.dororo.x, self.dororo.y, 100, 100)
        else:
            self.dororo.image.clip_composite_draw(0, 0, 60, 60, 0, 'h', self.dororo.x, self.dororo.y, 100, 100)


class Dororo:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image_name = 'Dororo_Sheet.png'
        self.image = None

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN},
                self.RUN: {right_up: self.IDLE, left_up: self.IDLE}
            }
        )

    def _ensure_image(self):
        if self.image is None:
            self.image = load_image(self.image_name)

    def update(self): self.state_machine.update()
    def draw(self): self._ensure_image(); self.state_machine.draw()
    def handle_event(self, event): self.state_machine.handle_state_event(('INPUT', event))


dororo = Dororo()
