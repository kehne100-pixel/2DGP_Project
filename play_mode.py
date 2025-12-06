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

# 화면 크기
W, H = 1600, 900

# 전역
background = None
player = None     # 1P
enemy = None      # 2P (AI)
ai = None

selected_character = 0
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


def set_selected_index(index):
    global selected_character
    selected_character = index


# -------------------------------
# 캐릭터 생성 (양 끝에서 리스폰)
# -------------------------------
def create_fighter(name, is_left=True):
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

    c.y = c.ground_y

    if is_left:
        c.x = 200     # 왼쪽 끝 근처
        c.face_dir = 1
    else:
        c.x = 1400    # 오른쪽 끝 근처
        c.face_dir = -1

    c.dir = 0
    return c


# -------------------------------
# 몸통 충돌 (서로 통과 X, 적은 밀리지 않음)
# -------------------------------
def resolve_body_collision():
    global player, enemy
    if not player or not enemy:
        return

    body_half = 35
    min_distance = body_half * 2  # 70

    dx = enemy.x - player.x
    if dx == 0:
        return

    distance = abs(dx)
    if distance < min_distance:
        # 적은 고정, 플레이어만 조정
        if dx > 0:
            player.x = enemy.x - min_distance
        else:
            player.x = enemy.x + min_distance

        player.x = max(50, min(1550, player.x))


# -------------------------------
# 초기화
# -------------------------------
def init():
    global background, player, enemy, ai

    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ 'Keroro_background.png' 파일을 찾지 못했습니다. 회색 배경 사용")
        background = None

    # 1P
    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ 플레이어 캐릭터: {player_name}")

    # 2P 랜덤 (플레이어와 다른 캐릭터)
    enemy_candidates = [name for name in CHARACTERS if name != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ 적 캐릭터: {enemy_name}")

    # AI
    ai = FighterAI(enemy, player)
    print("✅ FighterAI 초기화 완료")

    # 카메라
    camera.init()
    print("✅ Camera 초기화 완료")


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
        ai.update()

    if player and enemy:
        resolve_body_collision()
        camera.update_camera_zoom(player, enemy, background)


# -------------------------------
# 그리기
# -------------------------------
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cam_x = camera.camera_x
    cam_y = camera.camera_y

    if background:
        src_w = int(W / zoom)
        src_h = int(H / zoom)

        bx = int(cam_x)
        by = int(cam_y)

        if src_w > background.w:
            src_w = background.w
        if src_h > background.h:
            src_h = background.h

        if bx + src_w > background.w:
            bx = background.w - src_w
        if by + src_h > background.h:
            by = background.h - src_h
        if bx < 0:
            bx = 0
        if by < 0:
            by = 0

        src_cx = bx + src_w // 2
        src_cy = by + src_h // 2

        background.clip_draw(
            src_cx, src_cy,
            src_w, src_h,
            W // 2, H // 2,
            W, H
        )
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

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

        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
