# camera.py
# 화면 중심을 기준으로 카메라를 움직이고,
# 두 캐릭터 거리로 줌인/줌아웃 하는 단순한 버전

SCREEN_W, SCREEN_H = 1600, 900

# 카메라 중심(world 좌표)
camera_x = SCREEN_W / 2
camera_y = SCREEN_H / 2

# 줌 배율 (1.0 = 원래 크기)
scale = 1.0

# 가까울 때 최대 줌인 배율
MAX_ZOOM_IN = 1.6   # 너무 크면 배경이 많이 깨져 보임
MIN_ZOOM     = 1.0  # 처음엔 1.0(원래 상태)


def init():
    """플레이 모드 들어올 때 초기화"""
    global camera_x, camera_y, scale
    camera_x = SCREEN_W / 2
    camera_y = SCREEN_H / 2
    scale = 1.0


def get_zoom():
    return scale


def world_to_screen(wx, wy):
    """월드 좌표 → 화면 좌표"""
    sx = int((wx - camera_x) * scale + SCREEN_W / 2)
    sy = int((wy - camera_y) * scale + SCREEN_H / 2)
    return sx, sy


def update_camera(player, enemy, background):
    """
    - 두 캐릭터의 중간을 따라감
    - 두 캐릭터 거리로 줌인/줌아웃
    - 배경 이미지 범위를 절대 넘지 않게 클램프
    """
    global camera_x, camera_y, scale
    if player is None or enemy is None or background is None:
        return

    bg_w, bg_h = background.w, background.h

    # ----------------- 1) 거리 기반 줌 -----------------
    dx = abs(player.x - enemy.x)

    # 이 값들은 직접 조금씩 조절해서 느낌 맞춰도 됨
    NEAR = 300.0   # 이 거리 이하로 가까워지면 최대 줌인
    FAR  = 1200.0  # 이 거리 이상 멀어지면 줌아웃(1.0)

    # 0~1 로 정규화
    t = (dx - NEAR) / (FAR - NEAR)
    if t < 0.0:
        t = 0.0
    if t > 1.0:
        t = 1.0

    # 멀리 있을 때: scale = 1.0
    # 가까울 때:   scale = MAX_ZOOM_IN
    target_scale = MAX_ZOOM_IN - (MAX_ZOOM_IN - MIN_ZOOM) * t

    if target_scale < MIN_ZOOM:
        target_scale = MIN_ZOOM
    if target_scale > MAX_ZOOM_IN:
        target_scale = MAX_ZOOM_IN

    # 부드럽게 보간
    scale += (target_scale - scale) * 0.10

    # ----------------- 2) 카메라 중심 -----------------
    # 두 캐릭터 중간
    desired_cx = (player.x + enemy.x) / 2.0

    # 세로는 거의 고정(무대 중앙 기준)
    desired_cy = bg_h / 2.0

    # 현재 줌에서 화면에 보이는 영역 크기
    view_w = SCREEN_W / scale
    view_h = SCREEN_H / scale
    half_w = view_w / 2.0
    half_h = view_h / 2.0

    # 배경 범위를 넘지 않게 카메라 중심 클램프
    min_cx = half_w
    max_cx = bg_w - half_w
    if min_cx > max_cx:   # 배경이 화면보다 좁을 때 대비
        min_cx = max_cx = bg_w / 2.0

    if desired_cx < min_cx:
        desired_cx = min_cx
    if desired_cx > max_cx:
        desired_cx = max_cx

    min_cy = half_h
    max_cy = bg_h - half_h
    if min_cy > max_cy:
        min_cy = max_cy = bg_h / 2.0

    if desired_cy < min_cy:
        desired_cy = min_cy
    if desired_cy > max_cy:
        desired_cy = max_cy

    # 부드럽게 따라가기
    camera_x += (desired_cx - camera_x) * 0.15
    camera_y += (desired_cy - camera_y) * 0.15


def get_view_rect(background):
    """
    현재 카메라/줌 상태에서
    배경 이미지의 어떤 부분을 잘라서 그릴지 반환.
    (left, bottom, width, height)
    """
    bg_w, bg_h = background.w, background.h

    vw = int(SCREEN_W / scale)
    vh = int(SCREEN_H / scale)

    if vw > bg_w:
        vw = bg_w
    if vh > bg_h:
        vh = bg_h

    left = int(camera_x - vw / 2)
    bottom = int(camera_y - vh / 2)

    if left < 0:
        left = 0
    if bottom < 0:
        bottom = 0
    if left + vw > bg_w:
        left = bg_w - vw
    if bottom + vh > bg_h:
        bottom = bg_h - vh

    return left, bottom, vw, vh
