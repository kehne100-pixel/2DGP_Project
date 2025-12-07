# camera.py
# - 가로(x) 방향만 카메라/줌 적용
# - y는 바닥(ground_y)을 기준으로 앵커, 점프할 때만 scale 영향
# - world_to_screen() 으로 캐릭터 그리기용 좌표 변환

SCREEN_W, SCREEN_H = 1600, 900

center_x = SCREEN_W / 2
center_y = SCREEN_H / 2   # 배경 그릴 때만 사용
scale    = 1.0

# 줌 범위 (너무 크지 않게 줄였음)
MIN_ZOOM = 0.9   # 처음 화면은 약간 멀리
MAX_ZOOM = 1.2   # 최대 확대도 과하지 않게

# 캐릭터 월드 기준 바닥 y
CHR_GROUND_Y    = 90.0
# 화면에서 캐릭터 발이 닿을 y (이 값만 바꾸면 위/아래로 전체 이동)
GROUND_SCREEN_Y = 90.0


def init():
    global center_x, center_y, scale
    center_x = SCREEN_W / 2
    center_y = SCREEN_H / 2
    scale    = 1.0




def update(p1, p2, background, player_moved=False):

    """
    - 두 캐릭터 사이 x 거리로 줌 계산
    - center_x 는 두 캐릭터 x 중점
    - 세로는 고정 (배경 중앙 기준)
    """
    global center_x, center_y, scale

    if p1 is None or p2 is None:
        return

    # ---------- 1) 줌 계산 (x 거리만) ----------
    dx = abs(p1.x - p2.x)

    NEAR = 250.0   # 이 거리 이하 → 최대 확대
    FAR  = 1200.0  # 이 거리 이상 → 최소 줌 (멀리)

    if dx <= NEAR:
        t = 1.0
    elif dx >= FAR:
        t = 0.0
    else:
        t = 1.0 - (dx - NEAR) / (FAR - NEAR)   # 0 ~ 1

    target_scale = MIN_ZOOM + (MAX_ZOOM - MIN_ZOOM) * t

    # 부드럽게 보간
    lerp = 0.12
    scale = scale + (target_scale - scale) * lerp
    scale = max(MIN_ZOOM, min(scale, MAX_ZOOM))

    # ---------- 2) 가로 카메라 중심 : 두 캐릭터 x 중점 ----------
    desired_cx = (p1.x + p2.x) / 2.0

    # ---------- 3) 배경 안에서만 보이도록 center_x 클램프 ----------
    if background:
        view_w = SCREEN_W / scale
        half_w = view_w / 2.0

        min_cx = half_w
        max_cx = background.w - half_w

        # 배경이 창보다 작을 경우 방어
        if min_cx > max_cx:
            min_cx = max_cx = background.w / 2.0

        desired_cx = max(min_cx, min(desired_cx, max_cx))

        # 세로 중심은 배경 중앙(위아래로는 이제 안 움직임)
        center_y = background.h / 2.0
    else:
        center_y = SCREEN_H / 2.0

    # 부드럽게 따라감
    follow_lerp = 0.15
    center_x = center_x + (desired_cx - center_x) * follow_lerp


def world_to_screen(wx, wy):
    """
    월드 좌표 -> 화면 좌표
    - x : center_x, scale 적용 (카메라/줌 영향 O)
    - y : ground_y 기준으로 고정, 점프 높이만 scale 영향
    """
    # ▶ 가로는 카메라/줌 그대로
    sx = int((wx - center_x) * scale + SCREEN_W / 2)

    # ▶ 세로는 "바닥" 기준으로 고정
    dy = wy - CHR_GROUND_Y              # 바닥에서 얼만큼 올라갔는지
    sy = int(GROUND_SCREEN_Y + dy * scale)

    return sx, sy


def get_zoom():
    return scale


def get_center():
    return center_x, center_y
