# camera.py

# 화면 크기 (play_mode.py와 동일)
W, H = 1600, 900

# 카메라 상태
camera_x = 0.0
camera_y = 0.0
scale = 1.0

# 처음 거리(기준 거리) – 첫 프레임에서 자동으로 설정
_base_distance = None

# 최대 줌 인 배율 (가까워졌을 때)
max_zoom_in = 1.8   # 필요하면 2.0 정도로 조절해도 됨


def init():
    """게임 시작 시 카메라 초기화 - 처음은 항상 원래 시점(1.0)"""
    global camera_x, camera_y, scale, _base_distance
    camera_x = 0.0
    camera_y = 0.0
    scale = 1.0
    _base_distance = None   # 첫 update에서 현재 거리 기준으로 잡음


def get_zoom():
    return scale


def world_to_screen(wx, wy):
    """
    월드 좌표 -> 화면 좌표
    camera_x, camera_y : 화면 왼쪽 아래에 해당하는 월드 좌표
    """
    sx = (wx - camera_x) * scale
    sy = (wy - camera_y) * scale
    return sx, sy


def update_camera_zoom(p1, p2, background):
    """
    - 처음 프레임의 p1~p2 거리 = 기준거리(base_distance)
    - 그 거리에선 항상 scale 1.0 유지
    - 더 가까워지면 max_zoom_in 까지 확대
    - 더 멀어져도 1.0 밑으로는 축소 안 함
    """
    global camera_x, camera_y, scale, _base_distance

    if p1 is None or p2 is None or background is None:
        return

    # 현재 두 캐릭터 사이 x 거리
    distance_x = abs(p1.x - p2.x)

    # 첫 호출이면 이 때의 거리를 기준으로 사용
    if _base_distance is None:
        _base_distance = max(distance_x, 1.0)

    dist_far = _base_distance           # 이 거리일 때 scale = 1.0
    dist_close = max(250.0, dist_far * 0.35)   # 이 거리 이하이면 최대 확대

    # ----------------- 카메라 위치 계산 -----------------
    center_x = (p1.x + p2.x) / 2.0

    # 화면 가운데에 center_x가 오도록, 왼쪽 아래 월드좌표
    desired_camera_x = center_x - (W / (2 * scale))

    bg_w = background.w
    bg_h = background.h

    max_camera_x = max(0.0, bg_w - (W / scale))
    max_camera_y = max(0.0, bg_h - (H / scale))

    # X 범위 제한
    if desired_camera_x < 0:
        desired_camera_x = 0.0
    if desired_camera_x > max_camera_x:
        desired_camera_x = max_camera_x

    # Y는 바닥 고정
    desired_camera_y = 0.0

    # 부드럽게 카메라 이동
    camera_x += (desired_camera_x - camera_x) * 0.15
    camera_y += (desired_camera_y - camera_y) * 0.15

    # ----------------- 줌 계산 -----------------
    # 1) 멀 때 : 그냥 1.0
    if distance_x >= dist_far:
        target_scale = 1.0
    # 2) dist_close ~ dist_far 사이에서 1.0 → max_zoom_in 선형보간
    elif distance_x > dist_close:
        t = (dist_far - distance_x) / (dist_far - dist_close)  # 0~1
        target_scale = 1.0 + t * (max_zoom_in - 1.0)
    # 3) 아주 가까우면 최대 확대
    else:
        target_scale = max_zoom_in

    # 최소 배율 1.0 유지 (원래보다 더 축소는 안 함)
    if target_scale < 1.0:
        target_scale = 1.0

    # 부드럽게 줌 보간
    scale += (target_scale - scale) * 0.15
