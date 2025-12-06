# camera.py
from pico2d import get_canvas_width, get_canvas_height

# ----- 전역 카메라 상태 -----
cam_x = 800.0    # 카메라 중심 (월드 좌표)
cam_y = 450.0
zoom = 1.0       # 1.0 = 기본, >1.0 = 확대

# 배경(월드) 크기 - play_mode.init() 에서 실제 이미지 크기로 다시 설정할 거야
WORLD_W = 1600
WORLD_H = 900

# 거리 → 줌 변환용 상수
MIN_ZOOM = 1.0   # 가장 멀 때 줌(배율) 1.0 (기본 화면)
MAX_ZOOM = 1.4   # 아주 가까울 때 최대 확대

CLOSE_DIST = 250.0   # 이 거리 이하로 가까워지면 MAX_ZOOM
FAR_DIST   = 900.0   # 이 거리 이상이면 MIN_ZOOM 고정


def clamp(min_val, x, max_val):
    return max(min_val, min(x, max_val))


def update(player, enemy):

    global cam_x, cam_y, zoom, WORLD_W, WORLD_H

    # 1) 두 캐릭터의 중간 지점을 카메라 중심으로
    cx = (player.x + enemy.x) / 2.0
    cy = (player.y + enemy.y) / 2.0

    # 2) 거리 계산해서 줌 배율 정하기
    dx = abs(player.x - enemy.x)

    if dx <= CLOSE_DIST:
        t = 0.0
    elif dx >= FAR_DIST:
        t = 1.0
    else:
        t = (dx - CLOSE_DIST) / (FAR_DIST - CLOSE_DIST)

    target_zoom = MAX_ZOOM - (MAX_ZOOM - MIN_ZOOM) * t

    # 3) 줌 값을 부드럽게 보간
    zoom += (target_zoom - zoom) * 0.1

    # 4) 줌에 맞는 윈도우 사이즈 계산 후, 카메라 중심 클램프
    cw = get_canvas_width()
    ch = get_canvas_height()

    window_w = cw / zoom
    window_h = ch / zoom

    half_w = window_w / 2.0
    half_h = window_h / 2.0

    cam_x = clamp(half_w, cx, WORLD_W - half_w)
    cam_y = clamp(half_h, cy, WORLD_H - half_h)


def get_window():

    cw = get_canvas_width()
    ch = get_canvas_height()
    w = cw / zoom
    h = ch / zoom

    left = cam_x - w / 2.0
    bottom = cam_y - h / 2.0
    return left, bottom, w, h


def world_to_screen(x, y):

    cw = get_canvas_width()
    ch = get_canvas_height()
    left, bottom, w, h = get_window()

    sx = (x - left) * (cw / w)
    sy = (y - bottom) * (ch / h)
    return sx, sy


def get_zoom():
    return zoom
