
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
    'run': {
        'rects': [
            (4,   1544, 60, 60),
            (67,  1544, 60, 60),
            (132, 1544, 60, 60),
            (198, 1544, 60, 60),
        ],
        'flip_when_left': True
    },
}



def draw_from_cfg(image, key, frame_idx, face_dir, x, y, draw_w=DRAW_W, draw_h=DRAW_H):
    cfg = SPRITE[key]

    # rects 우선(불규칙 좌표)
    if 'rects' in cfg:
        sx, sy, sw, sh = cfg['rects'][frame_idx % len(cfg['rects'])]
        if face_dir == -1 and cfg.get('flip_when_left', False):
            image.clip_composite_draw(sx, sy, sw, sh, 0, 'h', x, y, draw_w, draw_h)
        else:
            image.clip_draw(sx, sy, sw, sh, x, y, draw_w, draw_h)
        return

    # grid 방식
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
        if self.frame == 0:
            self.keroro.image.clip_draw(4, 1840, 60, 75, self.keroro.x, self.keroro.y, 100, 100)
        elif self.frame == 1:
            self.keroro.image.clip_draw(67, 1840, 60, 75, self.keroro.x, self.keroro.y, 100, 100)
        elif self.frame == 2:
            self.keroro.image.clip_draw(132, 1840, 60, 75, self.keroro.x, self.keroro.y, 100, 100)
        elif self.frame == 3:
            self.keroro.image.clip_draw(198, 1840, 60, 75, self.keroro.x, self.keroro.y, 100, 100)



class Run:
    def __init__(self, keroro):
        self.keroro = keroro
        self.frame = 0
        self.frame_count = 4
        self.SPEED = 8  # 업데이트 한 번에 이동 픽셀 수 (필요시 조절)

    def enter(self, e):
        self.frame = 0
        # 어떤 키로 Run에 들어왔는지 보고 진행 방향/얼굴 방향 결정
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
        pass  # 상태 전환 시 정지는 state_machine 쪽(up 이벤트)에서 처리

    def do(self):
        # 애니메이션
        self.frame = (self.frame + 1) % self.frame_count
        # 이동
        self.keroro.x += self.keroro.dir * self.SPEED
        # 화면 경계 클램프 (값은 프로젝트 해상도에 맞게)
        self.keroro.x = max(25, min(775, self.keroro.x))

    def draw(self):
        # lazy-load 보장
        self.keroro._ensure_image()
        draw_from_cfg(self.keroro.image, 'run', self.frame,
                      self.keroro.face_dir, self.keroro.x, self.keroro.y,
                      100, 100)
        if self.keroro.dir == 1:
            if self.frame == 0:
                self.keroro.image.clip_draw(4,   1544, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 1:
                self.keroro.image.clip_draw(67,  1544, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 2:
                self.keroro.image.clip_draw(132, 1544, 60, 60, self.keroro.x, self.keroro.y, 100, 100)
            elif self.frame == 3:
                self.keroro.image.clip_draw(198, 1544, 60, 60, self.keroro.x, self.keroro.y, 100, 100)




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
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, a_down: self.AUTORUN},
                self.RUN: {
                    right_up: self.IDLE,
                    left_up: self.IDLE,
                    right_down: self.RUN,  # ← 달리는 중 우측 키 다시 눌러도 즉시 우측으로
                    left_down: self.RUN,  # ← 달리는 중 좌측 키 다시 눌러도 즉시 좌측으로
                    a_down: self.AUTORUN
                },
                self.AUTORUN: {Time_out: self.IDLE, right_down: self.RUN, left_down: self.RUN}
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
