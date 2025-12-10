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

# -------------------------------------------------
# 기본 화면 크기
# -------------------------------------------------
W, H = 1600, 900

# -------------------------------------------------
# 전역 객체들
# -------------------------------------------------
background = None
player = None
enemy = None
ai = None

selected_character = 0
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']

# -------------------------------------------------
# UI 관련 전역 (체력/게이지/타이머)
# -------------------------------------------------
ui_hp_frame = None   # HP 프레임(검은 바)
ui_sp_frame = None   # SP 프레임(없으면 HP 프레임 재사용)
ui_hp_fill  = None   # HP 채우기(주황)
ui_sp_fill  = None   # SP 채우기(파랑)
ui_timer_bg = None   # 타이머 박스

digit_images = {}

# -------------------------------------------------
# 라운드 / UI 상수
# -------------------------------------------------
ROUND_TIME = 120.0        # 라운드 시간(초)
round_start_time = 0.0    # 시작 시각

# ================= HP 프레임 위치/크기 =================
HP_FRAME_Y   = H - 150    # 체력바 Y 위치
HP_FRAME_H   = 120        # 체력바 프레임 높이 (검은 바 높이)

# ★ 좌우 각각 프레임 가로 길이
LEFT_HP_FRAME_W  = 600    # 왼쪽(내 캐릭터) 검은 HP 프레임 길이
RIGHT_HP_FRAME_W = 600    # 오른쪽(적 캐릭터) 검은 HP 프레임 길이

# ★ 좌우 각각 프레임 중심 X (좌우 위치)
LEFT_HP_X  = 290          # 내 HP 프레임 중심 X
RIGHT_HP_X = W - 230      # 적 HP 프레임 중심 X

# 프레임 안쪽에서 주황바가 들어갈 여백
HP_INNER_MARGIN_X = 5    # 프레임에서 좌우로 띄울 여백 (원하면 조절)
HP_INNER_MARGIN_Y = 12    # (필요하면 사용)

# ================ HP 채우기(주황 바) 크기 ================
LEFT_HP_FILL_W_MAX  = 880
RIGHT_HP_FILL_W_MAX = 880

# ★ 주황바 세로 높이 (프레임과 독립)
HP_FILL_H = 30

# ================= HP 주황바(채우기) 위치 미세조정 =================
# +면 안쪽(가운데 방향)으로, -면 바깥쪽으로 이동
LEFT_HP_FILL_OFFSET_X  = -110
RIGHT_HP_FILL_OFFSET_X = 180

# Y도 필요하면 조절
HP_FILL_OFFSET_Y = 0

# ================= SP 프레임/바 위치/크기 =================
SP_OFFSET_Y = 22          # HP 아래로 얼마나 내릴지 (HP_FRAME_Y - SP_OFFSET_Y)

# ★ 좌우 각각 SP 프레임 중심 X (HP와 완전히 분리해서 조정 가능)
LEFT_SP_X  = 255
RIGHT_SP_X = W - 200

# ★ 좌우 각각 SP 프레임 가로 길이
LEFT_SP_FRAME_W  = 500
RIGHT_SP_FRAME_W = 500

# SP 프레임 높이
SP_FRAME_H = 120

# 프레임 안쪽 여백
SP_INNER_MARGIN_X = 10
SP_INNER_MARGIN_Y = 4

# ★ 좌우 각각 SP 채우기(파란 바) 최대 가로 길이 (프레임과 독립)
LEFT_SP_FILL_W_MAX  = 380
RIGHT_SP_FILL_W_MAX = 380

# 파란 바 높이
SP_FILL_H = 60

# 타이머 (지금 쓰는 값 유지)
TIMER_SCALE     = 0.35
TIMER_Y         = H - 120
TIMER_DIGIT_W   = 34
TIMER_DIGIT_H   = 52
TIMER_DIGIT_GAP = 4


def set_selected_index(index):
    global selected_character
    selected_character = index


# -------------------------------------------------
# 캐릭터 생성
# -------------------------------------------------
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

    # 양 끝에서 시작
    MARGIN_X = 200
    if is_left:
        c.x = MARGIN_X
        c.face_dir = 1
    else:
        c.x = W - MARGIN_X
        c.face_dir = -1

    c.dir = 0
    return c


# -------------------------------------------------
# 몸통 충돌 (서로 살짝 밀치기)
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

    # 💡 서로 너무 붙어 있을 때만 밀어낸다
    if distance < min_distance:
        overlap = min_distance - distance
        push = overlap / 2.0

        if dx > 0:   # enemy가 player 오른쪽에 있음
            player.x -= push
            enemy.x += push
        else:        # enemy가 player 왼쪽에 있음
            player.x += push
            enemy.x -= push


# -------------------------------------------------
# 스테이지 한계 (월드 기준)
# -------------------------------------------------
def clamp_fighters():
    STAGE_LEFT = 60
    STAGE_RIGHT = W - 60

    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# -------------------------------------------------
# AABB 충돌 / 전투 판정
# -------------------------------------------------
def aabb_intersect(box1, box2):
    l1, b1, r1, t1 = box1
    l2, b2, r2, t2 = box2
    if r1 < l2:
        return False
    if r2 < l1:
        return False
    if t1 < b2:
        return False
    if t2 < b1:
        return False
    return True

def _reset_attack_hit_done_if_needed(f):
    """공격 상태가 끝났는데도 attack_hit_done이 True로 남아서 다음 공격이 안맞는 문제 방지"""
    if not f or not hasattr(f, 'state_machine'):
        return
    cur = getattr(f.state_machine, 'cur_state', None)

    active = (
        getattr(f, 'ATTACK', None),
        getattr(f, 'ATTACK2', None),
        getattr(f, 'SKILL', None),
        getattr(f, 'SKILL2', None),
        getattr(f, 'SKILL3', None),
    )
    if cur not in active and hasattr(f, 'attack_hit_done'):
        f.attack_hit_done = False


def _pay_skill_cost_once(f):
    """
    스킬 상태로 '진입'했을 때 SP를 1회만 차감.
    (스킬이 빗나가도 사용한 순간 SP가 줄어야 하니까)
    """
    if not f or not hasattr(f, 'state_machine'):
        return

    cur = getattr(f.state_machine, 'cur_state', None)
    s1 = getattr(f, 'SKILL', None)
    s2 = getattr(f, 'SKILL2', None)
    s3 = getattr(f, 'SKILL3', None)

    # 스킬 코스트(원하는 값으로 바꿔도 됨)
    COST1, COST2, COST3 = 20, 35, 50

    # 스킬 상태가 아니면 "지불 완료" 표시 초기화
    if cur not in (s1, s2, s3):
        setattr(f, '_skill_paid_state', None)
        return

    # 이미 같은 스킬 상태에서 한 번 냈으면 또 내지 않음
    if getattr(f, '_skill_paid_state', None) is cur:
        return

    # 코스트 결정
    cost = COST1 if cur is s1 else COST2 if cur is s2 else COST3

    if hasattr(f, 'sp') and hasattr(f, 'max_sp'):
        # SP가 부족하면 0으로 깎지 말고 그냥 발동을 막고 싶다면,
        # 여기서 return 시키고 스킬 상태로 못가게 처리해야 함(캐릭터 handle_event쪽 수정 필요).
        f.sp = max(0, f.sp - cost)

    setattr(f, '_skill_paid_state', cur)


def handle_combat(attacker, defender):
    """
    - attacker.get_attack_hitbox() 가 None 이 아니고
      defender.get_hurtbox() 와 겹치면
      defender.take_hit(damage, attacker.face_dir) 호출
    """
    if not hasattr(attacker, 'get_attack_hitbox'):
        return
    if not hasattr(defender, 'get_hurtbox'):
        return
    if not hasattr(defender, 'take_hit'):
        return

    hitbox = attacker.get_attack_hitbox()
    if hitbox is None:
        return

    hurtbox = defender.get_hurtbox()
    if not aabb_intersect(hitbox, hurtbox):
        return

    # 공격 1번에 한 번만 맞도록 (캐릭터 쪽 flag)
    if hasattr(attacker, 'attack_hit_done') and attacker.attack_hit_done:
        return

    # --- 데미지/게이지 값 ---
    DAMAGE_ATTACK  = 5
    DAMAGE_SKILL1  = 20
    DAMAGE_SKILL2  = 35
    DAMAGE_SKILL3  = 50
    SP_GAIN_ON_HIT = 10

    cur_state = getattr(attacker.state_machine, 'cur_state', None)

    damage = DAMAGE_ATTACK
    gain_sp = False  # ★ 평타일 때만 True

    if cur_state is getattr(attacker, 'SKILL', None):
        damage = DAMAGE_SKILL1
    elif cur_state is getattr(attacker, 'SKILL2', None):
        damage = DAMAGE_SKILL2
    elif cur_state is getattr(attacker, 'SKILL3', None):
        damage = DAMAGE_SKILL3
    else:
        # ★ 일반 공격(ATTACK / ATTACK2)일 때만 게이지 증가
        if cur_state in (
            getattr(attacker, 'ATTACK', None),
            getattr(attacker, 'ATTACK2', None)
        ):
            gain_sp = True

    # 피격
    defender.take_hit(damage, attacker.face_dir)

    # 공격자 필살 게이지 증가 (평타일 때만)
    if gain_sp and hasattr(attacker, 'sp') and hasattr(attacker, 'max_sp'):
        attacker.sp += SP_GAIN_ON_HIT
        if attacker.sp > attacker.max_sp:
            attacker.sp = attacker.max_sp

    # 이 공격으로는 더 이상 맞지 않도록
    if hasattr(attacker, 'attack_hit_done'):
        attacker.attack_hit_done = True


# -------------------------------------------------
# 타이머 보조 함수
# -------------------------------------------------
def get_remaining_time():
    """0~ROUND_TIME 초 사이 정수 반환"""
    global round_start_time
    elapsed = get_time() - round_start_time
    remain = ROUND_TIME - elapsed
    if remain < 0:
        remain = 0
    return int(remain)


# -------------------------------------------------
# 초기화
# -------------------------------------------------
def init():
    global background, player, enemy, ai
    global ui_hp_frame, ui_sp_frame, ui_hp_fill, ui_sp_fill, ui_timer_bg
    global digit_images, round_start_time

    # 배경
    try:
        background = load_image('Keroro_background.png')
        print("✅ Keroro_background.png 로드 완료")
    except:
        print("⚠️ Keroro_background.png 를 찾지 못했습니다.")
        background = None

    # 캐릭터 생성
    player_name = CHARACTERS[selected_character]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}")

    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy (AI) : {enemy_name}")

    # AI
    ai = FighterAI(enemy, player)

    # 카메라
    camera.init()
    print("✅ Camera init 완료")

    # ----- UI 이미지 로드 -----
    try:
        ui_hp_frame = load_image('ui_hp_frame.png')
        ui_sp_frame = ui_hp_frame   # SP 프레임도 같은 이미지 사용
    except:
        ui_hp_frame = None
        ui_sp_frame = None
        print("⚠️ ui_hp_frame.png 로드 실패")

    try:
        ui_hp_fill = load_image('ui_hp_fill.png')
    except:
        ui_hp_fill = None
        print("⚠️ ui_hp_fill.png 로드 실패")

    try:
        ui_sp_fill = load_image('ui_sp_fill.png')
    except:
        ui_sp_fill = None
        print("⚠️ ui_sp_fill.png 로드 실패")

    try:
        ui_timer_bg = load_image('ui_timer.png')
    except:
        ui_timer_bg = None
        print("⚠️ ui_timer.png 로드 실패")

    # 숫자 이미지(0~9, :)
    digit_images = {}
    for ch in '0123456789':
        fname = f'timer{ch}.png'
        try:
            digit_images[ch] = load_image(fname)
        except:
            digit_images[ch] = None
            print(f"⚠️ {fname} 로드 실패")

    # 콜론 이미지
    try:
        digit_images[':'] = load_image('timer_colon.png')
    except:
        digit_images[':'] = None
        print("⚠️ timer_colon.png 로드 실패 (없으면 그냥 건너뜀)")

    # 라운드 타이머 시작 시각
    round_start_time = get_time()


def finish():
    global background, player, enemy, ai
    global ui_hp_frame, ui_sp_frame, ui_hp_fill, ui_sp_fill, ui_timer_bg, digit_images
    background = None
    player = None
    enemy = None
    ai = None
    ui_hp_frame = None
    ui_sp_frame = None
    ui_hp_fill = None
    ui_sp_fill = None
    ui_timer_bg = None
    digit_images = {}


# -------------------------------------------------
# 매 프레임 업데이트
# -------------------------------------------------
def update():
    global player, enemy, ai, background

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    clamp_fighters()
    resolve_body_collision()

    if player and enemy:
        handle_combat(player, enemy)
        handle_combat(enemy, player)

    camera.update(player, enemy, background)


# -------------------------------------------------
# HP / SP UI 그리기
# -------------------------------------------------
def draw_hp_sp_bar(fighter, side):
    """
    - 각 사이드(왼쪽/오른쪽)에 대해
      HP프레임, HP바, SP프레임, SP바의 위치/크기를 전부 별도로 사용
    - HP바는 프레임 안쪽에서만 길이가 줄어들고, 한쪽 끝(anchor)은 고정
    - ★ 추가: HP 주황바 영역을 프레임과 분리해서 X 오프셋으로 좌우 이동 가능
    """
    global ui_hp_frame, ui_sp_frame, ui_hp_fill, ui_sp_fill

    if fighter is None:
        return

    # --- 스탯 가져오기 ---
    max_hp = getattr(fighter, 'max_hp', 100)
    hp     = getattr(fighter, 'hp', max_hp)
    max_sp = getattr(fighter, 'max_sp', 100)
    sp     = getattr(fighter, 'sp', 0)

    hp_ratio = 0.0 if max_hp <= 0 else max(0.0, min(1.0, hp / max_hp))
    sp_ratio = 0.0 if max_sp <= 0 else max(0.0, min(1.0, sp / max_sp))

    # --- 공통 Y 위치 ---
    hp_y = HP_FRAME_Y
    sp_y = HP_FRAME_Y - SP_OFFSET_Y

    # ---------- 사이드별 상수 선택 ----------
    if side == 'left':
        # HP
        hp_base_x      = LEFT_HP_X
        hp_frame_w     = LEFT_HP_FRAME_W
        hp_fill_w_max  = LEFT_HP_FILL_W_MAX

        # SP
        sp_base_x      = LEFT_SP_X
        sp_frame_w     = LEFT_SP_FRAME_W
        sp_fill_w_max  = LEFT_SP_FILL_W_MAX

        anchor_left = True   # 왼쪽 끝 고정
    else:
        hp_base_x      = RIGHT_HP_X
        hp_frame_w     = RIGHT_HP_FRAME_W
        hp_fill_w_max  = RIGHT_HP_FILL_W_MAX

        sp_base_x      = RIGHT_SP_X
        sp_frame_w     = RIGHT_SP_FRAME_W
        sp_fill_w_max  = RIGHT_SP_FILL_W_MAX

        anchor_left = False  # 오른쪽 끝 고정

    # ===================== HP 프레임(검은 바) =====================
    if ui_hp_frame:
        ui_hp_frame.draw(hp_base_x, hp_y, hp_frame_w, HP_FRAME_H)

    frame_left  = hp_base_x - hp_frame_w / 2
    frame_right = hp_base_x + hp_frame_w / 2

    # 프레임 안쪽 영역
    hp_inner_left  = frame_left  + HP_INNER_MARGIN_X
    hp_inner_right = frame_right - HP_INNER_MARGIN_X

    # ★ HP 주황바 영역(프레임과 분리) + 오프셋 적용
    if side == 'left':
        hp_bar_left  = hp_inner_left + LEFT_HP_FILL_OFFSET_X
        hp_bar_right = hp_bar_left + hp_fill_w_max
    else:
        hp_bar_right = hp_inner_right - RIGHT_HP_FILL_OFFSET_X
        hp_bar_left  = hp_bar_right - hp_fill_w_max

    # 안전 클램프
    hp_bar_left  = max(hp_inner_left, hp_bar_left)
    hp_bar_right = min(hp_inner_right, hp_bar_right)

    hp_draw_w_max = max(0, hp_bar_right - hp_bar_left)

    # ===================== HP 채우기(주황 바) =====================
    if ui_hp_fill and hp_ratio > 0.0:
        img = ui_hp_fill

        # 프레임 안쪽(보이는 영역) 경계
        clip_l = hp_inner_left
        clip_r = hp_inner_right

        # "주황바 전체(HP 100%)" 기준으로 어디에 둘지(좌/우 각각 오프셋)
        if side == 'left':
            full_left = hp_inner_left + LEFT_HP_FILL_OFFSET_X
            full_right = full_left + hp_fill_w_max
            anchor_left = True
        else:
            full_right = hp_inner_right + RIGHT_HP_FILL_OFFSET_X
            full_left = full_right - hp_fill_w_max
            anchor_left = False

        # 현재 HP 비율에 따른 "원래 그리려는" 구간(앵커 기준)
        full_w = float(hp_fill_w_max)
        cur_w = full_w * hp_ratio
        if cur_w <= 0:
            return

        if anchor_left:
            desired_l = full_left
            desired_r = full_left + cur_w
        else:
            desired_l = full_right - cur_w
            desired_r = full_right

        # 프레임 안쪽으로만 보이게 “수학적으로 클리핑”
        draw_l = max(desired_l, clip_l)
        draw_r = min(desired_r, clip_r)
        draw_w = draw_r - draw_l
        if draw_w <= 0:
            return

        # 이미지 소스(가로)도 비율만큼 자르기
        src_full_w = img.w
        src_h = img.h
        src_w = int(src_full_w * hp_ratio)
        if src_w < 1:
            src_w = 1

        # draw_l~draw_r가 desired_l~desired_r의 몇 % 구간인지(u0~u1)
        u0 = (draw_l - desired_l) / cur_w
        u1 = (draw_r - desired_l) / cur_w
        u0 = max(0.0, min(1.0, u0))
        u1 = max(0.0, min(1.0, u1))

        # 왼쪽/오른쪽 앵커에 따라 src 시작점이 달라짐
        if anchor_left:
            src_seg_left = 0
        else:
            src_seg_left = src_full_w - src_w

        src_left = int(src_seg_left + u0 * src_w)
        src_clip_w = int((u1 - u0) * src_w)
        if src_clip_w < 1:
            src_clip_w = 1

        dst_cx = (draw_l + draw_r) / 2
        dst_h = HP_FILL_H
        dst_y = hp_y + HP_FILL_OFFSET_Y

        img.clip_draw(
            int(src_left), 0,
            int(src_clip_w), int(src_h),
            int(dst_cx), int(dst_y),
            int(draw_w), int(dst_h)
        )

    # ===================== SP 프레임 =====================
    if ui_sp_frame is None:
        ui_sp_frame = ui_hp_frame

    if ui_sp_frame:
        ui_sp_frame.draw(sp_base_x, sp_y, sp_frame_w, SP_FRAME_H)

    sp_frame_left  = sp_base_x - sp_frame_w / 2
    sp_frame_right = sp_base_x + sp_frame_w / 2

    sp_inner_left  = sp_frame_left  + SP_INNER_MARGIN_X
    sp_inner_right = sp_frame_right - SP_INNER_MARGIN_X

    sp_inner_width = sp_inner_right - sp_inner_left
    sp_draw_w_max  = min(sp_fill_w_max, sp_inner_width)

    # ===================== SP 채우기(파란 바) =====================
    if ui_sp_fill and sp_ratio > 0.0:
        img = ui_sp_fill

        cur_w = sp_draw_w_max * sp_ratio
        dst_h = SP_FILL_H

        src_full_w = img.w
        src_h      = img.h
        src_w      = int(src_full_w * sp_ratio)
        if src_w < 1:
            src_w = 1

        if anchor_left:
            src_left = 0
            dst_cx = sp_inner_left + cur_w / 2
        else:
            src_left = src_full_w - src_w
            dst_cx = sp_inner_right - cur_w / 2

        img.clip_draw(
            int(src_left), 0,
            int(src_w), int(src_h),
            int(dst_cx), int(sp_y),
            int(cur_w), int(dst_h)
        )


# -------------------------------------------------
# 타이머 UI
# -------------------------------------------------
def draw_timer_ui():
    global ui_timer_bg, digit_images

    if not ui_timer_bg:
        return

    cx = W // 2 + 15
    cy = TIMER_Y

    src_w, src_h = ui_timer_bg.w, ui_timer_bg.h
    dest_w = int(src_w * TIMER_SCALE)
    dest_h = int(src_h * TIMER_SCALE)

    ui_timer_bg.draw(cx, cy, dest_w, dest_h)

    remain = get_remaining_time()
    mm = remain // 60
    ss = remain % 60
    text = f"{mm:02}:{ss:02}"

    digit_w = TIMER_DIGIT_W
    digit_h = TIMER_DIGIT_H
    gap = TIMER_DIGIT_GAP

    total_width = len(text) * (digit_w + gap) - gap
    start_x = cx - total_width / 2
    base_y = cy - 8

    for ch in text:
        img = digit_images.get(ch, None)
        if img:
            img.draw(int(start_x + digit_w / 2), base_y, digit_w, digit_h)
        start_x += (digit_w + gap)


# -------------------------------------------------
# 그리기
# -------------------------------------------------
def draw():
    clear_canvas()

    zoom = camera.get_zoom()
    cx, cy = camera.get_center()

    # ----- 배경 (카메라/줌 반영) -----
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

    draw_hp_sp_bar(player, 'left')
    draw_hp_sp_bar(enemy, 'right')
    draw_timer_ui()

    update_canvas()


# -------------------------------------------------
# 입력 처리
# -------------------------------------------------
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
