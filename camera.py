# camera.py
# - 캐릭터 좌표는 그대로 화면 좌표로 사용 (world_to_screen = 그대로 리턴)
# - 카메라는 배경만 스크롤/줌
# - 줌은 두 캐릭터의 x 거리만 보고 결정

SCREEN_W, SCREEN_H = 1600, 900

center_x = SCREEN_W / 2   # 배경용 카메라 중심 x
center_y = SCREEN_H / 2   # 배경용 카메라 중심 y (항상 배경 가운데 근처)
scale    = 1.0            # 배경 줌 배율 (1.0 = 기본)

# 줌 범위 (원하면 숫자만 바꿔서 조절 가능)
MIN_ZOOM = 1.0    # 가장 멀리 (처음 상태)
MAX_ZOOM = 1.2    # 최대 확대 (너무 크게 느껴지면 1.15 정도로 줄이기)


def init():
    """게임 시작 시 기본 카메라 상태"""
    global center_x, center_y, scale
    center_x = SCREEN_W / 2
    center_y = SCREEN_H / 2
    scale    = MIN_ZOOM


def update(p1, p2, background):
    """
    - p1, p2 : 플레이어 두 명 (화면 좌표)
    - background : 배경 이미지 (play_mode 에서 넘겨줌)
    - 배경만 스크롤/줌, 캐릭터는 화면 좌표 그대로 사용
    """
    global center_x, center_y, scale

    if p1 is None or p2 is None:
        return

    # ---------------- 1) 줌 계산 (x 거리만 사용) ----------------
    dx = abs(p1.x - p2.x)

    # 거리 기준값
    NEAR = 300.0    # 이 거리 이하 → 최대 확대
    FAR  = 1200.0   # 이 거리 이상 → 가장 멀리 (MIN_ZOOM)

    if dx <= NEAR:
        t = 1.0
    elif dx >= FAR:
        t = 0.0
    else:
        # 0 ~ 1 사이
        t = 1.0 - (dx - NEAR) / (FAR - NEAR)

    target_scale = MIN_ZOOM + (MAX_ZOOM - MIN_ZOOM) * t

    # 부드럽게 보간
    lerp = 0.12
    scale += (target_scale - scale) * lerp

    # 범위 클램프
    if scale < MIN_ZOOM:
        scale = MIN_ZOOM
    if scale > MAX_ZOOM:
        scale = MAX_ZOOM

    # ---------------- 2) 배경 카메라 중심 x ----------------
    # 두 캐릭터의 중간 x 기준
    desired_cx = (p1.x + p2.x) / 2.0

    if background:
        # 줌이 적용된 상황에서 화면이 보는 "원본 배경" 폭
        view_w = SCREEN_W / scale
        half_w = view_w / 2.0

        # center_x 가 배경 밖으로 나가지 않도록
        min_cx = half_w
        max_cx = background.w - half_w

        if min_cx > max_cx:
            min_cx = max_cx = background.w / 2.0

        desired_cx = max(min_cx, min(desired_cx, max_cx))

        # 세로는 배경 가운데에 고정
        center_y = background.h / 2.0
    else:
        center_y = SCREEN_H / 2.0

    # 부드럽게 카메라 이동
    follow_lerp = 0.15
    center_x += (desired_cx - center_x) * follow_lerp


def world_to_screen(wx, wy):
    """
    캐릭터 좌표용 변환.
    지금은 '카메라가 캐릭터를 건드리지 않게' 하기 위해
    그대로 리턴만 한다.
    """
    return int(wx), int(wy)


def get_zoom():
    """배경 그릴 때만 사용하는 줌 값"""
    return scale


def get_center():
    """배경 그릴 때 사용할 카메라 중심 좌표"""
    return center_x, center_y
