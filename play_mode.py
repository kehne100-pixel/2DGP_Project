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

# ✔ 스테이지 양 끝(플레이어가 움직일 수 있는 최소/최대 x)
STAGE_LEFT  = 60
STAGE_RIGHT = W - 60   # = 1540


# ---------- 공격 충돌(AABB) ----------
def aabb(box1, box2):
    l1, b1, r1, t1 = box1
    l2, b2, r2, t2 = box2
    if r1 < l2: return False
    if r2 < l1: return False
    if t1 < b2: return False
    if t2 < b1: return False
    return True


def handle_attack_collisions():
    global player, enemy
    if not player or not enemy:
        return

    # 1) 플레이어 공격 → 적 피격
    if hasattr(player, 'get_attack_hitbox') and hasattr(enemy, 'get_hurtbox') and hasattr(enemy, 'take_hit'):
        atk_box = player.get_attack_hitbox()
        hurt_box = enemy.get_hurtbox()
        if atk_box and hurt_box and aabb(atk_box, hurt_box):
            # 한 번의 공격 애니메이션 동안 한 번만 때리게
            if hasattr(player, 'attack_hit_done'):
                if not player.attack_hit_done:
                    enemy.take_hit(5, player.face_dir)  # 데미지 5 예시
                    player.attack_hit_done = True
            else:
                enemy.take_hit(5, player.face_dir)

    # 2) 적 공격 → 플레이어 피격 (원하면 켜기)
    if hasattr(enemy, 'get_attack_hitbox') and hasattr(player, 'get_hurtbox') and hasattr(player, 'take_hit'):
        atk_box = enemy.get_attack_hitbox()
        hurt_box = player.get_hurtbox()
        if atk_box and hurt_box and aabb(atk_box, hurt_box):
            if hasattr(enemy, 'attack_hit_done'):
                if not enemy.attack_hit_done:
                    player.take_hit(5, enemy.face_dir)
                    enemy.attack_hit_done = True
            else:
                player.take_hit(5, enemy.face_dir)


def set_selected_index(index):
    global selected_character
    selected_character = index


# ---------------- 캐릭터 생성 ----------------
def create_fighter(name, is_left=True):
    """캐릭터 이름에 따라 객체 생성 + 양쪽 끝 리스폰"""
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

    # 각 캐릭터가 가진 ground_y에 맞춰 발 위치 세팅
    c.y = c.ground_y

    # ✔ 양쪽 끝에서 리스폰 (STAGE_LEFT / STAGE_RIGHT 사용)
    if is_left:
        c.x = STAGE_LEFT
        c.face_dir = 1
    else:
        c.x = STAGE_RIGHT
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
        # enemy 위치는 고정, player 만 밀기
        if dx > 0:
            player.x = enemy.x - min_distance
        else:
            player.x = enemy.x + min_distance


# --------- 캐릭터가 스테이지 밖으로 못 나가게 (월드 기준) ----------
def clamp_fighters():
    # ✔ 플레이어와 적 모두 STAGE_LEFT ~ STAGE_RIGHT 안에만 있게
    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# ---------------- 초기화 ----------------
def init():
    global background, player, enemy, ai

    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ Keroro_background.png 를 찾지 못했습니다.")
        background = None

    # 1P (왼쪽 끝)
    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}, spawn x = {player.x}")

    # 2P (오른쪽 끝)
    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy(AI) : {enemy_name}, spawn x = {enemy.x}")

    ai = FighterAI(enemy, player)

    # ✔ 카메라 초기화 + 두 캐릭터 기준으로 한 번 갱신
    camera.init()
    camera.update(player, enemy, background)
    print("✅ Camera init & first update 완료")



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

    # 플레이어/적 몸통 충돌 처리
    resolve_body_collision()

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

        # 배경 범위를 벗어나지 않게 클램프
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

    # 캐릭터 그리기 (각 캐릭터 draw() 안에서 world_to_screen 사용)
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
