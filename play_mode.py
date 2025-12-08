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

    # 양쪽 끝에서 출발 (너랑 전에 맞춰둔 값)
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
        if dx > 0:
            player.x = enemy.x - min_distance
        else:
            player.x = enemy.x + min_distance


# --------- 캐릭터가 스테이지 밖으로 못 나가게 (월드 기준) ----------
def clamp_fighters():
    STAGE_LEFT  = 60
    STAGE_RIGHT = W - 60

    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# --------- AABB 충돌 ---------
def rect_overlap(a, b):
    # a, b: (left, bottom, right, top)
    if a is None or b is None:
        return False
    al, ab, ar, at = a
    bl, bb, br, bt = b
    if ar < bl:
        return False
    if br < al:
        return False
    if at < bb:
        return False
    if bt < ab:
        return False
    return True


# --------- 공격 판정 처리 ---------
def handle_attack_collisions():
    global player, enemy
    if not player or not enemy:
        return

    # 1) player → enemy
    if hasattr(player, 'get_attack_hitbox') and hasattr(player, 'is_attacking'):
        if player.is_attacking and not getattr(player, 'attack_hit_done', False):
            atk_box = player.get_attack_hitbox() if callable(player.get_attack_hitbox) else None
            hurt_box = enemy.get_hurtbox() if hasattr(enemy, 'get_hurtbox') and callable(enemy.get_hurtbox) else None

            if rect_overlap(atk_box, hurt_box):
                # 데미지 값은 일단 10으로
                if hasattr(enemy, 'take_hit') and callable(enemy.take_hit):
                    enemy.take_hit(10, player.face_dir)
                # 한 번만 맞도록 플래그
                player.attack_hit_done = True

    # 2) enemy → player
    if hasattr(enemy, 'get_attack_hitbox') and hasattr(enemy, 'is_attacking'):
        if enemy.is_attacking and not getattr(enemy, 'attack_hit_done', False):
            atk_box = enemy.get_attack_hitbox() if callable(enemy.get_attack_hitbox) else None
            hurt_box = player.get_hurtbox() if hasattr(player, 'get_hurtbox') and callable(player.get_hurtbox) else None

            if rect_overlap(atk_box, hurt_box):
                if hasattr(player, 'take_hit') and callable(player.take_hit):
                    player.take_hit(10, enemy.face_dir)
                enemy.attack_hit_done = True


# ---------------- 초기화 ----------------
def init():
    global background, player, enemy, ai

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

    camera.init()   # 처음엔 배율 1.0
    print("✅ Camera init 완료")


def finish():
    global background, player, enemy, ai
    background = None
    player = None
    enemy = None
    ai = None


# ---------------- 매 프레임 업데이트 ----------------
def update():
    global player, enemy, ai, background

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

    # ✅ 공격 판정
    handle_attack_collisions()

    # 카메라 중심 & 줌 갱신
    camera.update(player, enemy, background)


# ---------------- 그리기 ----------------
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cx, cy = camera.get_center()

    # 배경은 항상 화면 전체를 덮되, 카메라 중심/줌에 맞춰 잘라 그리기
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
