# camera.py
# - 가로 스크롤 없이, 배경 중앙을 항상 보여줌
# - 두 캐릭터 사이 x 거리로 줌(확대/축소)만 조절
# - 캐릭터 y는 항상 같은 바닥에 서 있게 처리

SCREEN_W, SCREEN_H = 1600, 900

center_x = SCREEN_W / 2
center_y = SCREEN_H / 2

scale = 1.0
MIN_ZOOM = 1.0     # 기본 배율
MAX_ZOOM = 1.3     # 최대 확대 (너무 크지 않게 줄였음)

CHR_GROUND_Y = 90.0    # 캐릭터 월드 기준 바닥 y
GROUND_SCREEN_Y = 90.0 # 화면에서 발 위치 y (이 값만 바꾸면 됨)


def init():
    global center_x, center_y, scale
    center_x = SCREEN_W / 2
    center_y = SCREEN_H / 2
    scale = 1.0


def update(p1, p2, background):
    """
    - 배경 중앙을 항상 기준으로 삼음 (가로 스크롤 X)
    - 두 캐릭터 사이 거리만 보고 줌만 조절
    """
    global center_x, center_y, scale

    # 배경이 있으면 카메라 중심은 항상 배경 중앙
    if background:
        center_x = background.w / 2.0
        center_y = background.h / 2.0
    else:
        center_x = SCREEN_W / 2.0
        center_y = SCREEN_H / 2.0

    # 캐릭터 둘 다 있어야 줌 계산
    if p1 is None or p2 is None:
        return

    # ---------- 1) 줌 계산 (x 거리만 사용) ----------
    dx = abs(p1.x - p2.x)

    # 거리 기준
    NEAR = 250.0   # 이 이하이면 최대 확대
    FAR  = 1400.0  # 이 이상이면 최소 확대

    if dx <= NEAR:
        t = 1.0
    elif dx >= FAR:
        t = 0.0
    else:
        # 0 ~ 1
        t = 1.0 - (dx - NEAR) / (FAR - NEAR)

    target_scale = MIN_ZOOM + (MAX_ZOOM - MIN_ZOOM) * t

    # 부드러운 보간
    scale += (target_scale - scale) * 0.10
    if scale < MIN_ZOOM:
        scale = MIN_ZOOM
    if scale > MAX_ZOOM:
        scale = MAX_ZOOM


def world_to_screen(wx, wy):
    """
    월드 좌표 -> 화면 좌표
    - x : 배경 중앙(center_x) 기준으로 zoom만 적용
    - y : CHR_GROUND_Y를 기준으로, 점프 높이만 zoom에 영향
      (바닥에 서있을 땐 항상 같은 y에 보이도록)
    """
    # 가로
    sx = int((wx - center_x) * scale + SCREEN_W / 2)

    # 세로 : 바닥 기준
    dy = wy - CHR_GROUND_Y
    sy = int(GROUND_SCREEN_Y + dy * scale)

    return sx, sy


def get_zoom():
    return scale


def get_center():
    return center_x, center_y
