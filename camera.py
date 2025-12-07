# camera.py
# - 가로 중심: 두 캐릭터 사이 중점
# - 세로: 평소엔 바닥이 고정된 높이에 보이도록, 점프할 때만 조금 위로 따라감
# - 줌(scale)은 두 캐릭터 x 거리로만 결정
# - world_to_screen() 으로 캐릭터 그리기용 좌표 변환

SCREEN_W, SCREEN_H = 1600, 900

center_x = SCREEN_W / 2
center_y = SCREEN_H / 2
scale    = 1.0

MIN_ZOOM = 1.0   # 기본 배율(처음 화면)
MAX_ZOOM = 1.6   # 최대 확대 배율 (원하면 1.4~1.8 정도로 조정 가능)

# 바닥이 화면에서 보일 y 위치 (pico2d 좌표계 기준)
GROUND_SCREEN_Y = 90.0   # 네 게임에서 캐릭터가 서 있는 y와 맞춰서 사용


def init():
    global center_x, center_y, scale
    center_x = SCREEN_W / 2
    center_y = SCREEN_H / 2
    scale    = 1.0


def update(p1, p2, background):
    """
    - 두 캐릭터 사이 x 거리로 줌 결정
    - center_x: 두 캐릭터 x 중점
    - center_y: 평소엔 '바닥이 항상 같은 화면 높이'에 오도록,
                점프할 때만 두 캐릭터 y 중점 쪽으로 살짝 올라감
    - 배경 밖으로 나가지 않게 카메라 중심을 클램프
    """
    global center_x, center_y, scale

    if p1 is None or p2 is None:
        return

    # ---------- 1) 줌 계산 (x 거리만 사용) ----------
    dx = abs(p1.x - p2.x)

    NEAR = 250.0   # 이 거리 이하 → 최대 확대
    FAR  = 1200.0  # 이 거리 이상 → 최소 확대(=1.0)

    if dx <= NEAR:
        t = 1.0
    elif dx >= FAR:
        t = 0.0
    else:
        t = 1.0 - (dx - NEAR) / (FAR - NEAR)  # 0 ~ 1

    target_scale = MIN_ZOOM + (MAX_ZOOM - MIN_ZOOM) * t

    # 부드럽게 보간
    lerp = 0.12
    scale = scale + (target_scale - scale) * lerp

    if scale < MIN_ZOOM:
        scale = MIN_ZOOM
    if scale > MAX_ZOOM:
        scale = MAX_ZOOM

    # ---------- 2) 가로 카메라 중심: 두 캐릭터 x 중점 ----------
    mid_x = (p1.x + p2.x) / 2.0
    desired_cx = mid_x

    # ---------- 3) 세로 카메라 중심 계산 ----------
    # (1) 기본: 바닥이 항상 화면 GROUND_SCREEN_Y 위치에 보이도록 하는 center_y
    ground_world_y = getattr(p1, 'ground_y', 90.0)  # 캐릭터 ground_y 사용
    base_center_y = ground_world_y - (GROUND_SCREEN_Y - SCREEN_H / 2.0) / scale

    # (2) 점프 시: 두 캐릭터 y 중점 쪽으로 약간 이동
    mid_y = (p1.y + p2.y) / 2.0

    jump_h1 = max(0.0, p1.y - ground_world_y)
    jump_h2 = max(0.0, p2.y - ground_world_y)
    max_jump_h = max(jump_h1, jump_h2)

    JUMP_MAX = 300.0  # 이 정도 높이까지 올라가면 t_jump → 1.0
    if max_jump_h <= 0:
        t_jump = 0.0
    else:
        t_jump = max(0.0, min(1.0, max_jump_h / JUMP_MAX))

    # t_jump == 0 이면 완전 바닥 기준, 1이면 두 캐릭터 y 중점 기준
    desired_cy = base_center_y * (1.0 - t_jump) + mid_y * t_jump

    # ---------- 4) 배경 안에서만 보이도록 중심 클램프 ----------
    if background:
        view_w = SCREEN_W / scale
        view_h = SCREEN_H / scale

        half_w = view_w / 2.0
        half_h = view_h / 2.0

        min_cx = half_w
        max_cx = background.w - half_w
        min_cy = half_h
        max_cy = background.h - half_h

        # 배경이 창보다 작을 수도 있으니 방어
        if min_cx > max_cx:
            min_cx = max_cx = background.w / 2.0
        if min_cy > max_cy:
            min_cy = max_cy = background.h / 2.0

        desired_cx = max(min_cx, min(desired_cx, max_cx))
        desired_cy = max(min_cy, min(desired_cy, max_cy))

    # ---------- 5) 카메라 중심 부드럽게 이동 ----------
    follow_lerp = 0.15
    center_x = center_x + (desired_cx - center_x) * follow_lerp
    center_y = center_y + (desired_cy - center_y) * follow_lerp


def world_to_screen(wx, wy):
    """
    월드 좌표 → 화면 좌표
    (카메라 중심(center_x, center_y), 배율(scale) 적용)
    """
    sx = int((wx - center_x) * scale + SCREEN_W / 2)
    sy = int((wy - center_y) * scale + SCREEN_H / 2)
    return sx, sy


def get_zoom():
    return scale


def get_center():
    return center_x, center_y
