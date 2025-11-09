
from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a
from state_machine import StateMachine


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def Time_out(e):   return e[0] == 'TIME_OUT'

# ---------------------------
# 2) 스프라이트 시트 설정
# ---------------------------
IMAGE_W, IMAGE_H = 996, 1917     # Keroro 시트 크기
CELL_W, CELL_H   = 40, 80      # 칸 크기 (맞지 않으면 조정)
DRAW_W, DRAW_H   = 130, 130      # 화면 출력 크기

def row_y_from_top(row_from_top):
    """위에서 N번째 행(0기준)을 pico2d의 (왼-아래 기준) y로 변환"""
    return IMAGE_H - (row_from_top + 1) * CELL_H

# idle: 1행 1~4열, run: 5행 1~4열
SPRITE = {
    'idle': {'row': 0, 'start_col': 0, 'frames': 4, 'flip_when_left': True},
    'run':  {'row': 4, 'start_col': 0, 'frames': 4, 'flip_when_left': True},
}

def draw_from_cfg(image, key, frame_idx, face_dir, x, y, draw_w=DRAW_W, draw_h=DRAW_H):
    cfg = SPRITE[key]
    sx = (cfg['start_col'] + frame_idx) * CELL_W
    sy = row_y_from_top(cfg['row'])
    if face_dir == -1 and cfg.get('flip_when_left', False):
        image.clip_composite_draw(sx, sy, CELL_W, CELL_H, 0, 'h', x, y, draw_w, draw_h)
    else:
        image.clip_draw(sx, sy, CELL_W, CELL_H, x, y, draw_w, draw_h)

# ---------------------------
# 3) 상태들: Idle / Run / AutoRun
# ---------------------------
class Idle:
    def __init__(self, keroro):
        self.keroro = keroro

    def enter(self, e):
        self.keroro.dir = 0
        self.keroro.wait_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.keroro.frame = (self.keroro.frame + 1) % SPRITE['idle']['frames']

    def draw(self):
        # lazy-load 보장
        self.keroro._ensure_image()
        draw_from_cfg(self.keroro.image, 'idle', self.keroro.frame,
                      self.keroro.face_dir, self.keroro.x, self.keroro.y)

class Run:
    def __init__(self, keroro):
        self.keroro = keroro

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.keroro.dir = self.keroro.face_dir = 1
        elif left_down(e) or right_up(e):
            self.keroro.dir = self.keroro.face_dir = -1

    def exit(self, e): pass

    def do(self):
        self.keroro.frame = (self.keroro.frame + 1) % SPRITE['run']['frames']
        self.keroro.x += self.keroro.dir * 5
        self.keroro.x = max(25, min(775, self.keroro.x))

    def draw(self):
        # lazy-load 보장
        self.keroro._ensure_image()
        draw_from_cfg(self.keroro.image, 'run', self.keroro.frame,
                      self.keroro.face_dir, self.keroro.x, self.keroro.y)

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
        self.keroro.x = max(25, min(775, self.keroro.x))
        if self.keroro.x <= 25:
            self.keroro.dir = self.keroro.face_dir = 1
        elif self.keroro.x >= 775:
            self.keroro.dir = self.keroro.face_dir = -1
        if get_time() - self.start_time > 5:
            self.keroro.state_machine.handle_state_event(('TIME_OUT', 0))

    def draw(self):
        # lazy-load 보장
        self.keroro._ensure_image()
        draw_from_cfg(self.keroro.image, 'run', self.keroro.frame,
                      self.keroro.face_dir, self.keroro.x, self.keroro.y,
                      DRAW_W+8, DRAW_H+8)

# ---------------------------
# 4) 본체 Keroro (이미지 lazy-load)
# ---------------------------
class Keroro:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        # ★ 이미지 즉시 로드하지 않음 (renderer가 아직 없을 수 있음)
        self.image_name = 'Keroro_Sheet.png'
        self.image = None

        self.IDLE    = Idle(self)
        self.RUN     = Run(self)
        self.AUTORUN = AutoRun(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:    {right_down: self.RUN, left_down: self.RUN, a_down: self.AUTORUN},
                self.RUN:     {right_up:   self.IDLE, left_up:  self.IDLE, a_down: self.AUTORUN},
                self.AUTORUN: {Time_out:   self.IDLE, right_down: self.RUN, left_down: self.RUN}
            }
        )

    def _ensure_image(self):
        """open_canvas() 이후 첫 draw 시점에 이미지 로드"""
        if self.image is None:
            self.image = load_image(self.image_name)

    def update(self): self.state_machine.update()

    def draw(self):
        # 혹시 상태 draw 이전에 직접 호출되는 경우도 대비
        self._ensure_image()
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


keroro = Keroro()
