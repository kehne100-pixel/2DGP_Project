# camera.py
from pico2d import *

# 화면 해상도 (네가 쓰는 창 크기 기준)
W, H = 1600, 900

# 카메라 상태
camera_x = 0.0
camera_y = 0.0
scale = 1.0        # 현재 줌 값
max_zoom_in = 2.0  # 최대 줌인 정도 (필요하면 2.5, 3.0 등으로 조절 가능)

# 연출용 단계 (지금은 항상 2: 둘 다 보이게)
start_phase = 2


def init():
    global camera_x, camera_y, scale, start_phase
    camera_x = 0.0
    camera_y = 0.0
    scale = 1.0
    start_phase = 2   # 0,1 연출 안 쓰고 바로 둘 다 보이게


def update_camera_zoom(p1, p2, background):
    global camera_x, camera_y, scale, max_zoom_in, start_phase

    # -------------------------------
    # 1. 카메라 중심 잡기
    # -------------------------------
    if start_phase == 0:
        # 1P 연출
        center_x = p1.x
        center_y = p1.y
    elif start_phase == 1:
        # 2P 연출
        center_x = p2.x
        center_y = p2.y
    else:
        # 둘 사이 중간점
        center_x = (p1.x + p2.x) / 2.0
        center_y = (p1.y + p2.y) / 2.0

    # -------------------------------
    # 2. 타겟 카메라 위치 계산
    #    (world 기준 카메라 좌상단)
    # -------------------------------
    # 친구 코드 로직 그대로 사용
    desired_camera_x = center_x - (W / (2 * scale))
    desired_camera_y = (center_y - (H / (2 * scale))) * 2

    # 배경 크기
    if background is not None:
        bg_w = background.w
        bg_h = background.h
    else:
        # 혹시 배경 없으면 화면 크기와 같다고 가정
        bg_w = W
        bg_h = H

    # 카메라 이동 가능한 최대 범위 (줌 고려)
    max_camera_x = bg_w - ((W - 1) / scale)
    max_camera_y = bg_h - ((H - 1) / scale)

    # Clamp
    if max_camera_x < 0:
        max_camera_x = 0
    if max_camera_y < 0:
        max_camera_y = 0

    desired_camera_x = max(0.0, min(desired_camera_x, max_camera_x))
    desired_camera_y = max(0.0, min(desired_camera_y, max_camera_y))

    # 부드럽게 따라가기
    camera_x += (desired_camera_x - camera_x) * 0.15
    camera_y += (desired_camera_y - camera_y) * 0.15

    # -------------------------------
    # 3. ZOOM 계산
    # -------------------------------
    distance_x = abs(p1.x - p2.x)
    distance_y = abs(p1.y - p2.y)

    distance_max = 1200.0  # 멀리 떨어졌을 때
    distance_min = 150.0   # 매우 가까울 때

    t = (distance_x - distance_min) / (distance_max - distance_min)
    t = max(0.0, min(1.0, t))  # 0~1로 클램프

    fixed_scale = 2.0

    # 기본 줌 (친구 로직)
    if distance_x < 320:
        base_target_scale = fixed_scale
    else:
        # 1.0 ~ max_zoom_in 사이
        base_target_scale = max_zoom_in - (max_zoom_in - 1.0) * t

    # 점프에 의한 추가 줌아웃
    max_y_gap = 300.0
    y_t = min(1.0, distance_y / max_y_gap)

    # x 거리별 추가 줌아웃 상한
    if distance_x < 0:
        max_extra_zoom_out = 0.6
    elif distance_x < 25:
        max_extra_zoom_out = 0.5
    elif distance_x < 50:
        max_extra_zoom_out = 0.4
    elif distance_x < 75:
        max_extra_zoom_out = 0.3
    elif distance_x < 100:
        max_extra_zoom_out = 0.2
    elif distance_x < 125:
        max_extra_zoom_out = 0.1
    else:
        max_extra_zoom_out = 0.0

    extra_zoom_out = max_extra_zoom_out * y_t

    target_scale = base_target_scale - extra_zoom_out

    # 1.0 아래로 내려가지 않게
    if target_scale < 1.0:
        target_scale = 1.0

    # 부드럽게 보간
    scale += (target_scale - scale) * 0.12


def world_to_screen(wx, wy):
    """
    월드 좌표(wx, wy)를 화면 좌표로 변환.
    이걸 캐릭터 draw()에서 써서 화면에 그리면 됨.
    """
    sx = (wx - camera_x) * scale
    sy = (wy - camera_y) * scale
    return sx, sy


def get_zoom():
    """현재 줌 값 (캐릭터 크기 조절용)"""
    return scale
