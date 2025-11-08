from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDLK_a

from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def a_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def Time_out(e): return e[0] == 'TIME_OUT'



class Run:
    def __init__(self, keroro):
        self.Keroro = keroro

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.keroro.dir = self.keroro.face_dir = 1
        elif left_down(e) or right_up(e):
            self.keroro.dir = self.keroro.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.keroro.frame = (self.keroro.frame + 1) % 8
        self.keroro.x += self.keroro.dir * 5
        self.keroro.x = max(25, min(775, self.keroro.x))

    def draw(self):
        if self.keroro.face_dir == 1:
            self.keroro.image.clip_draw(self.keroro.frame * 100, 100, 100, 100, self.keroro.x, self.keroro.y, 100, 100)
        else:
            self.keroro.image.clip_draw(self.keroro.frame * 100, 0, 100, 100, self.keroro.x, self.keroro.y, 100, 100)



class Idle:
    def __init__(self, keroro):
        self.keroro = keroro

    def enter(self, e):
        self.keroro.dir = 0
        self.keroro.wait_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.keroro.frame = (self.keroro.frame + 1) % 8

    def draw(self):
        if self.keroro.face_dir == 1:
            self.keroro.image.clip_draw(self.keroro.frame * 100, 300, 100, 100, self.keroro.x, self.keroro.y, 100, 100)
        else:
            self.keroro.image.clip_draw(self.keroro.frame * 100, 200, 100, 100, self.keroro.x, self.keroro.y, 100, 100)



class AutoRun:
    def __init__(self, keroro):
        self.keroro = keroro

    def enter(self, e):
        self.start_time = get_time()
        self.keroro.dir = -1
        self.keroro.face_dir = -1
        print("AutoRun Start")

    def exit(self, e):
        self.keroro.dir = 0
        print("AutoRun End")

    def do(self):
        self.keroro.frame = (self.keroro.frame + 1) % 8
        self.keroro.x += self.keroro.dir * 10
        self.keroro.x = max(25, min(775, self.keroro.x))


        if self.keroro.x <= 25:
            self.keroro.dir = 1
            self.keroro.face_dir = 1
        elif self.keroro.x >= 775:
            self.keroro.dir = -1
            self.keroro.face_dir = -1


        if get_time() - self.start_time > 5:
            self.keroro.state_machine.handle_state_event(('TIME_OUT', 0))

    def draw(self):

        if self.keroro.face_dir == 1:
            self.keroro.image.clip_draw(self.keroro.frame * 100, 100, 100, 100, self.keroro.x, self.keroro.y, 150, 150)
        else:
            self.keroro.image.clip_draw(self.keroro.frame * 100, 0, 100, 100, self.keroro.x, self.keroro.y, 150, 150)



class Kerororo:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('Keroro_sheet.png')

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.AutoRun = AutoRun(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.Run, left_down: self.Run, a_down: self.AutoRun},
                self.Run: {left_up: self.IDLE, right_up: self.IDLE, a_down: self.AutoRun},
                self.AutoRun: {Time_out: self.IDLE, left_down: self.Run, right_down: self.Run}
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
