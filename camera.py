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



def update(player, enemy):


def get_window():


def world_to_screen(x, y):



def get_zoom():
    return zoom
