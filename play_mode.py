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

W, H = 1600, 900

background = None
player = None
enemy = None
ai = None

selected_character = 0
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']

# ✅ 플레이어가 한 번이라도 움직였는지 여부
player_moved = False


def set_selected_index(index):
    global selected_character
    selected_character = index


# ---------------- 캐릭터 생성 ----------------
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
        print(f"[WARN] Unknown fighter name: {name}, use Keroro")
        c = Keroro()

    c.y = c.ground_y

    # 스샷처럼 양쪽 끝에서 출발
    MARGIN_X = 120
    if is_left:
        c.x = MARGIN_X
        c.face_dir = 1
    else:
        c.x = W - MARGIN_X
        c.face_dir = -1

    c.dir = 0
    return c


# --------- 몸통 충돌 (적은 안 밀리고, 플레이어만 밀리게) ----------
def resolve_body_collision():
    global player, enemy
    if not player or not enemy:
        return

    body_half = 35
    min_distance = body_half * 2

    dx = enemy.x - player.x
    if dx == 0:
        return

    distance = abs(dx)
    if distance < min_distance:
        # enemy가 오른쪽에 있을 때만, 그리고 플레이어가 오른쪽(적 쪽)으로
        # 파고들 때만 밀어냄
        if dx > 0:
            if player.dir > 0:   # ▶ 오른쪽으로 이동 중일 때만
                player.x = enemy.x - min_distance

        # enemy가 왼쪽에 있을 때만, 그리고 플레이어가 왼쪽(적 쪽)으로
        # 파고들 때만 밀어냄
        else:  # dx < 0
            if player.dir < 0:   # ◀ 왼쪽으로 이동 중일 때만
                player.x = enemy.x + min_distance



# --------- 캐릭터가 스테이지 밖으로 못 나가게 (월드 기준) ----------
def clamp_fighters():
    STAGE_LEFT  = 60
    STAGE_RIGHT = W - 60

    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# ---------------- 초기화 ----------------
def init():
    global background, player, enemy, ai, player_moved

    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ Keroro_background.png 를 찾지 못했습니다.")
        background = None

    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}")

    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy (AI) : {enemy_name}")

    ai = FighterAI(enemy, player)

    camera.init()   # 처음엔 배율 1.0, 화면은 기존과 동일
    player_moved = False         # ✅ 카메라 잠금 초기화
    print("✅ Camera init 완료")


def finish():
    global background, player, enemy, ai
    background = None
    player = None
    enemy = None
    ai = None


# ---------------- 매 프레임 업데이트 ----------------
def update():
    global player, enemy, ai, background, player_moved

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    # 스테이지 밖으로 못 나가게
    clamp_fighters()

    # 몸통 충돌
    resolve_body_collision()

    # ❗ 플레이어가 한 번이라도 움직였는지 체크
    if player and (player.dir != 0 or player.vy != 0):
        player_moved = True

    # 카메라 중심 & 줌 갱신 (네 번째 인자로 player_moved 전달)
    camera.update(player, enemy, background, player_moved)


# ---------------- 그리기 ----------------
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cx, cy = camera.get_center()

    # ✅ 배경은 항상 화면 전체를 덮되, 카메라 중심/줌에 맞춰 잘라 그리기
    if background:
        src_w = int(W / zoom)
        src_h = int(H / zoom)

        bx = int(cx - src_w / 2)
        by = int(cy - src_h / 2)

        if bx < 0:
            bx = 0
        if by < 0:
            by = 0
        if bx + src_w > background.w:
            bx = background.w - src_w
        if by + src_h > background.h:
            by = background.h - src_h

        src_center_x = bx + src_w // 2
        src_center_y = by + src_h // 2

        background.clip_draw(
            src_center_x, src_center_y,
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


# ---------------- 입력 처리 ----------------
def handle_events():
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()

        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
