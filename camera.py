# camera.py
from pico2d import *

# 화면 크기 (play_mode와 동일)
W, H = 1600, 900

# 카메라 상태 (모듈 전역 변수)
camera_x = 0.0      # 월드 좌표에서 '화면 왼쪽' 위치
camera_y = 0.0      # 월드 좌표에서 '화면 아래' 위치
scale    = 1.0      # 줌 배율 (1.0 = 기본)
max_zoom_in = 2.0   # 최대 줌인 배율 (친구 코드용)

def init():
    """모드 진입시 카메라 초기화"""
    global camera_x, camera_y, scale
    camera_x = 0.0
    camera_y = 0.0
    scale = 1.0      # ★ 처음엔 원래 화면 크기 그대로


def get_zoom():
    """현재 줌 배율 리턴 (play_mode에서 사용)"""
    return scale


def world_to_screen(x, y):
    """
    월드 좌표 (x, y)를 화면 좌표로 변환.
    화면 좌표 (0,0)은 왼쪽 아래, (W,H)는 오른쪽 위.
    """
    sx = (x - camera_x) * scale
    sy = (y - camera_y) * scale
    return sx, sy


def update_camera_zoom(p1, p2, background):
    """
    친구가 보내준 줌 로직을
    p1, p2(플레이어, 적)를 인자로 받도록 수정한 버전.
    play_mode.update() 에서 매 프레임 호출됨.
    """
    global camera_x, camera_y, scale, max_zoom_in

    # ----------------- 1. 카메라 중심점 계산 -----------------
    # 두 캐릭터 중간을 중심으로 잡기
    center_x = (p1.x + p2.x) / 2.0
    center_y = (p1.y + p2.y) / 2.0

    # 배경 크기
    if background is not None:
        bg_w = background.w
        bg_h = background.h
    else:
        bg_w = W
        bg_h = H

    # 현재 줌 기준으로 봤을 때, 화면에 담기 위한 카메라 위치(왼쪽 아래)
    desired_camera_x = center_x - (W / (2 * scale))
    # 격투게임 느낌으로 위아래는 거의 고정 (약간만 위쪽 여유)
    desired_camera_y = 0.0

    # 카메라가 움직일 수 있는 최대 범위
    max_camera_x = bg_w - (W / scale)
    max_camera_y = bg_h - (H / scale)

    # 범위 제한
    if desired_camera_x < 0:
        desired_camera_x = 0
    if desired_camera_y < 0:
        desired_camera_y = 0
    if desired_camera_x > max_camera_x:
        desired_camera_x = max_camera_x
    if desired_camera_y > max_camera_y:
        desired_camera_y = max_camera_y

    # 부드럽게 보간해서 이동
    camera_x += (desired_camera_x - camera_x) * 0.15
    camera_y += (desired_camera_y - camera_y) * 0.15

    # ----------------- 2. 줌(Scale) 계산 -----------------
    # 두 캐릭터 사이 거리
    distance_x = abs(p1.x - p2.x)
    distance_y = abs(p1.y - p2.y)

    # x 거리 기준값
    distance_max = 1200.0  # 멀리 떨어졌을 때
    distance_min = 150.0   # 매우 가까울 때

    # 0~1 로 정규화
    t = (distance_x - distance_min) / (distance_max - distance_min)
    if t < 0.0:
        t = 0.0
    if t > 1.0:
        t = 1.0

    # 기본 시작 줌 (1.0 = 원래 화면 그대로)
    fixed_scale = 1.0

    # 1) 기본 줌 계산
    if distance_x < 320:
        base_target_scale = fixed_scale
    else:
        # 1.0 ~ max_zoom_in 사이에서 변화
        base_target_scale = max_zoom_in - (max_zoom_in - 1.0) * t

    # 2) 점프 차이에 따른 추가 줌아웃 보정
    max_y_gap = 300.0
    y_t = distance_y / max_y_gap
    if y_t > 1.0:
        y_t = 1.0

    # x 거리가 가까울수록 extra 줌아웃 크게
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

    # 최종 목표 줌
    target_scale = base_target_scale - extra_zoom_out

    # 1.0 아래로는 내려가지 않게
    if target_scale < 1.0:
        target_scale = 1.0

    # 부드럽게 줌 보간
    scale += (target_scale - scale) * 0.12
