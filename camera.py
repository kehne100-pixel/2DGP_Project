# camera.py

# 카메라 & 줌 관리용 모듈
# - world 좌표: 기존 캐릭터 x, y 그대로 사용 (0 ~ 1600, 0 ~ 900 느낌)
# - camera_x, camera_y : 화면에 보이는 "왼쪽 아래" 월드 좌표
# - scale : 1.0 이 기본, 값이 클수록 화면을 확대 (카메라 줌 인)

W, H = 1600, 900  # 화면 크기 (play_mode와 동일하게 맞춰야 함)

camera_x = 0.0
camera_y = 0.0
scale = 1.0

# 멀리 떨어졌을 때 최대 줌인 정도 (1.0 ~ 이 값 사이에서 움직임)
max_zoom_in = 1.8  # 필요하면 2.0, 2.2 등으로 조정 가능


def init():
    """게임 시작 시 카메라 초기 상태"""
    global camera_x, camera_y, scale
    camera_x = 0.0   # 왼쪽에서 시작 (배경 전체를 한 번에 보여줄 때와 비슷한 시점)
    camera_y = 0.0   # 바닥 기준 (Y는 고정)
    scale = 1.0      # 줌 X (원래 보던 시점)


def get_zoom():
    """현재 줌 배율 반환"""
    return scale


def world_to_screen(wx, wy):
    """
    월드 좌표 -> 화면 좌표 변환
    - camera_x, camera_y는 화면 왼쪽 아래에 해당하는 월드 좌표
    - scale만큼 확대해서 사용
    """
    sx = (wx - camera_x) * scale
    sy = (wy - camera_y) * scale
    return sx, sy


def update_camera_zoom(p1, p2, background):
    """
    카메라 위치 & 줌 업데이트
    - p1, p2 : 서로 싸우는 두 캐릭터 (player, enemy)
    - background : play_mode에서 사용하는 배경 이미지
    """
    global camera_x, camera_y, scale, max_zoom_in

    if p1 is None or p2 is None or background is None:
        return

    # ---------------------------
    # 1. 카메라 기준 x 위치 (두 캐릭터의 중간)
    # ---------------------------
    center_x = (p1.x + p2.x) / 2.0

    # "왼쪽 아래" 기준 카메라 좌표를 정함
    # - 화면 가운데에 center_x가 오도록
    desired_camera_x = center_x - (W / (2 * scale))

    # 배경 크기
    bg_w = background.w
    bg_h = background.h

    # 카메라가 움직일 수 있는 최대 범위 (배경 밖으로 나가지 않게)
    max_camera_x = max(0.0, bg_w - (W / scale))
    max_camera_y = max(0.0, bg_h - (H / scale))

    # X 좌표를 배경 범위 안으로 클램프
    if desired_camera_x < 0:
        desired_camera_x = 0.0
    if desired_camera_x > max_camera_x:
        desired_camera_x = max_camera_x

    # Y는 "옛날 시점"처럼 바닥 기준으로 고정
    desired_camera_y = 0.0

    # 부드럽게 따라가기 (0.0 ~ 1.0, 클수록 더 빠르게 따라감)
    camera_x += (desired_camera_x - camera_x) * 0.15
    camera_y += (desired_camera_y - camera_y) * 0.15

    # ---------------------------
    # 2. 줌(Scale) 계산
    #    - 멀리 떨어지면 좀 더 멀리 보기 (scale이 1.0 쪽)
    #    - 가까워지면 확대 (scale이 max_zoom_in 쪽)
    # ---------------------------
    distance_x = abs(p1.x - p2.x)
    distance_y = abs(p1.y - p2.y)

    # 거리 기준값 (너무 멀리 떨어졌을 때 / 너무 가까울 때)
    distance_max = 1200.0  # 아주 멀리 떨어졌을 때
    distance_min = 150.0   # 거의 붙었을 때

    # 0 ~ 1 로 정규화
    t = (distance_x - distance_min) / (distance_max - distance_min)
    if t < 0.0:
        t = 0.0
    if t > 1.0:
        t = 1.0

    fixed_scale = 2.0  # 진짜 엄청 붙었을 때 최대 확대 배율

    # 기본 줌:
    # - 가까우면 fixed_scale까지 확대
    # - 멀어질수록 1.0 쪽으로 내려감
    if distance_x < 320.0:
        base_target_scale = fixed_scale
    else:
        # 1.0 ~ max_zoom_in 사이에서 이동
        base_target_scale = max_zoom_in - (max_zoom_in - 1.0) * t

    # ---------------------------
    # 3. 점프에 따른 추가 줌아웃 (옵션)
    # ---------------------------
    max_y_gap = 300.0
    y_t = distance_y / max_y_gap
    if y_t > 1.0:
        y_t = 1.0

    # 너무 가까울수록 점프하면 더 많이 줌아웃
    if distance_x < 25.0:
        max_extra_zoom_out = 0.5
    elif distance_x < 50.0:
        max_extra_zoom_out = 0.4
    elif distance_x < 75.0:
        max_extra_zoom_out = 0.3
    elif distance_x < 100.0:
        max_extra_zoom_out = 0.2
    elif distance_x < 125.0:
        max_extra_zoom_out = 0.1
    else:
        max_extra_zoom_out = 0.0

    extra_zoom_out = max_extra_zoom_out * y_t

    # 최종 타겟 줌 (점프할수록 조금 멀어짐)
    target_scale = base_target_scale - extra_zoom_out

    # 1.0 아래로 내려가면 원래보다 더 멀어지니 막기
    if target_scale < 1.0:
        target_scale = 1.0

    # 부드럽게 줌 보간
    scale += (target_scale - scale) * 0.12
