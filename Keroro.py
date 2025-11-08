# Keroro.py
from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a

# ===== 스프라이트 시트 설정 =====
SHEET_FILE   = 'Keroro_Sheet.png'  # 같은 폴더에 둬
TILE_W       = 64                  # <--- 셀 가로(필요시 맞춰 조정)
TILE_H       = 64                  # <--- 셀 세로(필요시 맞춰 조정)
SHEET_ORIGIN_X = 0                 # <--- 첫 칸의 좌상단 X
SHEET_ORIGIN_Y = 0                 # <--- 첫 칸의 좌상단 Y
IDLE_ROW     = 0                   # 맨 첫 줄(0행)
IDLE_COLS    = 8                   # idle 프레임 개수(보통 6~10 사이. 필요시 조정)
RUN_ROW      = 1                   # 달리기 행(대충 1행으로 시작해서 맞추기)
RUN_COLS     = 8

DRAW_W       = 100                 # 화면에 크게 보이도록
DRAW_H       = 100

# ===== 입력 판별 함수 =====
def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):   return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_RIGHT
def left_down(e):  return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP   and e[1].key == SDLK_LEFT
def a_down(e):     return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def Time_out(e):   return e[0] == 'TIME_OUT'

# ===== 간단 상태머신(파일 내 독립형) =====
class StateMachine:
    def __init__(self, start_state, table):
        self.cur_state = start_state
        self.table = table
        self.cur_state.enter(('START', 0))

    def update(self): self.cur_state.do()
    def draw(self):   self.cur_state.draw()

    def handle_state_event(self, e):
        if self.cur_state in self.table:
            for cond, next_state in self.table[self.cur_state].items():
                if cond(e):
                    self.cur_state.exit(e)
                    self.cur_state = next_state
                    self.cur_state.enter(e)
                    return

# ===== 시트 좌표 계산 도우미 =====
def get_src_rect(col, row, tile_w=TILE_W, tile_h=TILE_H):
    sx = SHEET_ORIGIN_X + col * tile_w   # 왼쪽에서 col칸
    sy = SHEET_ORIGIN_Y + row * tile_h   # 위에서 row칸 (아래 draw에서 상하 보정)
    return sx, sy, tile_w, tile_h

# ====== 상태들 ======
class Idle:
    def __init__(self, boy):
        self.boy = boy
        self.frame = 0
        self.last_t = 0

    def enter(self, e):
        self.boy.dir = 0
        self.last_t = get_time()

    def exit(self, e): pass

    def do(self):
        # 12fps 정도로 프레임 넘김
        now = get_time()
        if now - self.last_t > (1.0 / 12.0):
            self.frame = (self.frame + 1) % IDLE_COLS
            self.last_t = now

    def draw(self):
        col = self.frame
        row = IDLE_ROW
        sx, sy, sw, sh = get_src_rect(col, row)
        # 이미지 좌표계(아래가 원점) 보정: (시트높이 - sy - sh)
        self.boy.image.clip_draw(sx, (self.boy.sheet_h - sy - sh), sw, sh,
                                 self.boy.x, self.boy.y, DRAW_W, DRAW_H)

class Run:
    def __init__(self, boy):
        self.boy = boy
        self.frame = 0
        self.last_t = 0

    def enter(self, e):
        self.last_t = get_time()
        if right_down(e): self.boy.dir = self.boy.face_dir = 1
        elif left_down(e): self.boy.dir = self.boy.face_dir = -1

    def exit(self, e): pass

    def do(self):
        now = get_time()
        if now - self.last_t > (1.0 / 16.0):
            self.frame = (self.frame + 1) % RUN_COLS
            self.last_t = now
        self.boy.x += self.boy.dir * 5

    def draw(self):
        col = self.frame
        row = RUN_ROW
        sx, sy, sw, sh = get_src_rect(col, row)
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(sx, (self.boy.sheet_h - sy - sh), sw, sh,
                                     self.boy.x, self.boy.y, DRAW_W, DRAW_H)
        else:
            self.boy.image.clip_composite_draw(sx, (self.boy.sheet_h - sy - sh), sw, sh,
                                               0, 'h', self.boy.x, self.boy.y, DRAW_W, DRAW_H)

class AutoRun:
    def __init__(self, boy):
        self.boy = boy
        self.frame = 0
        self.last_t = 0
        self.start_time = 0

    def enter(self, e):
        self.start_time = get_time()
        self.last_t = self.start_time
        self.boy.dir = -1
        self.boy.face_dir = -1

    def exit(self, e):
        self.boy.dir = 0

    def do(self):
        now = get_time()
        if now - self.last_t > (1.0 / 16.0):
            self.frame = (self.frame + 1) % RUN_COLS
            self.last_t = now
        self.boy.x += self.boy.dir * 10
        self.boy.x = max(25, min(775, self.boy.x))
        if self.boy.x <= 25:  self.boy.dir = self.boy.face_dir =  1
        if self.boy.x >= 775: self.boy.dir = self.boy.face_dir = -1
        if now - self.start_time > 5:
            # 자동 달리기 5초 후 종료
            self.boy.state_machine.handle_state_event(('TIME_OUT', 0))

    def draw(self):
        col = self.frame
        row = RUN_ROW
        sx, sy, sw, sh = get_src_rect(col, row)
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(sx, (self.boy.sheet_h - sy - sh), sw, sh,
                                     self.boy.x, self.boy.y, DRAW_W, DRAW_H)
        else:
            self.boy.image.clip_composite_draw(sx, (self.boy.sheet_h - sy - sh), sw, sh,
                                               0, 'h', self.boy.x, self.boy.y, DRAW_W, DRAW_H)

# ====== Boy ======
class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.face_dir = 1
        self.dir = 0
        self.image = load_image(SHEET_FILE)
        self.sheet_w = self.image.w
        self.sheet_h = self.image.h

        self.IDLE = Idle(self)
        self.Run = Run(self)
        self.AutoRun = AutoRun(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE:   {right_down: self.Run, left_down: self.Run, a_down: self.AutoRun},
                self.Run:    {left_up: self.IDLE, right_up: self.IDLE, a_down: self.AutoRun},
                self.AutoRun:{lambda e:e[0]=='TIME_OUT': self.IDLE,
                              left_down: self.Run, right_down: self.Run}
            }
        )

    def update(self): self.state_machine.update()
    def draw(self):   self.state_machine.draw()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
