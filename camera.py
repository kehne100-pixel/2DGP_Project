# camera.py
from pico2d import get_canvas_width, get_canvas_height

# 화면 크기 (네가 쓰는 해상도에 맞게)
SCREEN_W = 1600
SCREEN_H = 900

# 월드 크기 (배경 이미지 크기와 맞추는 게 좋음 – Keroro_background.png가 1600x900이면 이렇게 둬도 됨)
WORLD_W = 1600
WORLD_H = 900

# 카메라 위치 & 줌
cam_x = SCREEN_W // 2
cam_y = SCREEN_H // 2
zoom = 1.0

# 보간 속도 (값이 클수록 더 빠르게 따라감)
CAMERA_LERP = 0.15
ZOOM_LERP = 0.12

# 줌 범위 (가까우면 크게, 멀어지면 작게 보여주기)
MIN_ZOOM = 0.8     # 가장 멀어졌을 때
MAX_ZOOM = 1.3     # 서로 아주 가까울 때

# "얼마나 떨어졌을 때"를 기준으로 할지
MIN_DIST = 120.0   # 이보다 가까우면 최대 줌
MAX_DIST = 600.0   # 이보다 멀어지면 최소 줌


def clamp(minv, v, maxv):
    return max(minv, min(v, maxv))


def update(player, enemy):
    """
    격투게임용 카메라:
    - x축: 두 캐릭터의 가운데를 따라감
    - y축: 지면 기준으로 거의 고정 (살짝만 위로)
    - 줌: 캐릭터 사이 거리로 결정 (가까우면 줌인, 멀면 줌아웃)
    """
    global cam_x, cam_y, zoom

    # 두 캐릭터의 중간 지점
    mid_x = (player.x + enemy.x) * 0.5
    # y는 너무 튀지 않게, 거의 바닥 기준(여유 있게 위로 조금 올려줌)
    base_y = 200

    # 카메라 목표 위치
    target_x = clamp(SCREEN_W * 0.5, mid_x, WORLD_W - SCREEN_W * 0.5)
    target_y = clamp(SCREEN_H * 0.5, base_y, WORLD_H - SCREEN_H * 0.5)

    # 부드럽게 따라가기 (LERP)
    cam_x += (target_x - cam_x) * CAMERA_LERP
    cam_y += (target_y - cam_y) * CAMERA_LERP

    # 두 캐릭터 사이 거리
    dist = abs(player.x - enemy.x)

    # 거리 -> [0,1] 정규화
    t = (dist - MIN_DIST) / (MAX_DIST - MIN_DIST)
    t = clamp(0.0, t, 1.0)

    # t가 0일 때: 아주 가까움 → MAX_ZOOM
    # t가 1일 때: 아주 멀어짐 → MIN_ZOOM
    target_zoom = MAX_ZOOM + (MIN_ZOOM - MAX_ZOOM) * t

    # 줌도 부드럽게 보간
    global zoom
    zoom += (target_zoom - zoom) * ZOOM_LERP


def world_to_screen(wx, wy):
    """
    월드 좌표(wx, wy)를 화면 좌표로 변환.
    배경은 '그냥 화면 전체에 draw' 하면 되고,
    캐릭터, 이펙트, UI 중 '월드 좌표 기반'만 이 함수를 써서 그려주면 됨.
    """
    sx = (wx - cam_x) * zoom + SCREEN_W * 0.5
    sy = (wy - cam_y) * zoom + SCREEN_H * 0.5
    return sx, sy


def get_zoom():
    return zoom
