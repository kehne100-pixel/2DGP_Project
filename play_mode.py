# play_mode.py

from pico2d import *
import game_framework
import random

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu

from fighter_ai import FighterAI
import camera

# 화면 크기 (네가 쓰는 창 크기)
W, H = 1600, 900

# 전역 변수
background = None
player = None        # 1P (조작하는 캐릭터)
enemy = None         # 2P (AI 캐릭터)
ai = None            # 적 인공지능

# select_mode에서 넘겨주는 플레이어 캐릭터 인덱스
selected_character = 0

# 선택창 인덱스 순서대로 캐릭터 이름
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


# -------------------------------
# 외부에서 플레이어 캐릭터 선택
# -------------------------------
def set_selected_index(index):
    global selected_character
    selected_character = index


# -------------------------------
# 캐릭터 생성 유틸 함수
# -------------------------------
def create_fighter(name, is_left=True):
    """캐릭터 이름에 따라 객체를 만들고, 좌/우 시작 위치 세팅"""

    if name == 'Keroro':
        c = Keroro()
    elif name == 'Dororo':
        c = Dororo()
    elif name == 'Tamama':
        c = Tamama()
    elif name == 'Giroro':
        c = Giroro()
    elif name == 'Kururu':
        c = Kururu()
    else:
        print(f"[WARN] 알 수 없는 캐릭터 이름: {name}, Keroro로 대체")
        c = Keroro()

    # 기본 y는 각 캐릭터 클래스에서 ground_y로 잡혀 있으니 거기에 맞춰줌
    c.y = c.ground_y

    if is_left:
        c.x = 400
        c.face_dir = 1
    else:
        c.x = 1200
        c.face_dir = -1

    c.dir = 0
    return c


# -------------------------------
# 몸통 충돌 처리 (서로 통과 X, 적은 밀리지 않게)
# -------------------------------
def resolve_body_collision():
    global player, enemy
    if not player or not enemy:
        return

    # 몸통 대략적인 반지름
    body_half = 35
    min_distance = body_half * 2

    dx = enemy.x - player.x
    if dx == 0:
        return

    distance = abs(dx)
    if distance < min_distance:
        # 적은 그대로 두고, 플레이어만 적과 겹치지 않게 뒤로 밀기
        if dx > 0:
            # 적이 오른쪽에 있음 → 플레이어를 왼쪽으로
            player.x = enemy.x - min_distance
        else:
            # 적이 왼쪽에 있음 → 플레이어를 오른쪽으로
            player.x = enemy.x + min_distance

        # 스테이지 가장자리 클램프 (각 캐릭터 코드와 맞춰줌)
        player.x = max(50, min(1550, player.x))


# -------------------------------
# 초기화
# -------------------------------
def init():
    global background, player, enemy, ai

    # 배경 이미지 로드 (전투 배경 그대로 사용)
    try:
        background = load_image('Keroro_background.png')  # 네가 쓰는 파일명 그대로
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ 'Keroro_background.png' 파일을 찾지 못했습니다. 회색 배경 사용")
        background = None

    # 1P 플레이어 캐릭터
    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ 플레이어 캐릭터: {player_name}")

    # 2P 적 캐릭터 (플레이어와 다른 캐릭터로 랜덤 선택)
    enemy_candidates = [name for name in CHARACTERS if name != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ 적 캐릭터: {enemy_name}")

    # 적 인공지능 생성 (enemy가 행동, player를 목표로)
    ai = FighterAI(enemy, player)
    print("✅ FighterAI 초기화 완료")

    # 카메라 초기화
    camera.init()
    print("✅ Camera 초기화 완료")


# -------------------------------
# 마무리
# -------------------------------
def finish():
    global background, player, enemy, ai
    if background:
        del background
        background = None
    if player:
        del player
        player = None
    if enemy:
        del enemy
        enemy = None
    if ai:
        del ai
        ai = None


# -------------------------------
# 매 프레임 업데이트
# -------------------------------
def update():
    global player, enemy, ai, background

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()  # AI가 enemy를 조작

    # 몸통 충돌 처리 (서로 통과 X)
    if player and enemy:
        resolve_body_collision()

        # 카메라 위치 & 줌 업데이트 (친구 코드 기반 camera.py)
        camera.update_camera_zoom(player, enemy, background)


# -------------------------------
# 화면 그리기
# -------------------------------
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cam_x = camera.camera_x
    cam_y = camera.camera_y

    # ✅ 배경 그리기 (스크롤 + 줌 반영)
    if background:
        # 화면에 보여줄 소스 영역 크기 (줌에 따라 변함)
        src_w = int(W / zoom)
        src_h = int(H / zoom)

        # 카메라 좌표를 소스 영역의 왼쪽 아래로 사용
        bx = int(cam_x)
        by = int(cam_y)

        # 소스 크기가 배경보다 크지 않게 조정
        if src_w > background.w:
            src_w = background.w
        if src_h > background.h:
            src_h = background.h

        # 배경 범위 넘어가지 않도록 클램프
        if bx + src_w > background.w:
            bx = background.w - src_w
        if by + src_h > background.h:
            by = background.h - src_h
        if bx < 0:
            bx = 0
        if by < 0:
            by = 0

        # clip_draw는 중심 기준이므로 + src_w/2, src_h/2
        background.clip_draw(
            bx + src_w / 2, by + src_h / 2,
            src_w, src_h,
            W / 2, H / 2,
            W, H
        )
    else:
        # 배경이 없으면 그냥 회색 화면
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    # ✅ 캐릭터 그리기 (각 캐릭터 draw()에서 camera.world_to_screen, zoom 적용해야 함)
    if player:
        player.draw()
    if enemy:
        enemy.draw()

    update_canvas()


# -------------------------------
# 입력 처리
# -------------------------------
def handle_events():
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()

        # 플레이어에게만 키 입력 전달 (적은 AI가 조작)
        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
