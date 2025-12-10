# play_mode.py

from pico2d import *
import game_framework
import random
import os

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


ALL_CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']
BANNED_CHARACTERS = {'Kururu'}
CHARACTERS = [c for c in ALL_CHARACTERS if c not in BANNED_CHARACTERS]

# -------------------------------------------------
# UI 관련 전역 (체력/게이지/타이머)
# -------------------------------------------------
ui_hp_frame = None
ui_sp_frame = None
ui_hp_fill  = None
ui_sp_fill  = None
ui_timer_bg = None
digit_images = {}

# -------------------------------------------------
# 결과 화면 (WIN / LOSE / DRAW)
# -------------------------------------------------
RESULT_SHOW_TIME = 3.0
result_state = None          # None / 'WIN' / 'LOSE' / 'DRAW'
result_start_time = 0.0
img_win = None
img_lose = None
img_draw = None

# -------------------------------------------------
# ✅ BGM (전투 시작/종료에 맞춰 재생/정지)
# -------------------------------------------------
battle_bgm = None
battle_bgm_type = None        # 'music' or 'wav'

# ✅ 여기에 있는 이름 중 "프로젝트 폴더에 실제로 존재하는 파일"을 자동으로 찾아서 재생
BATTLE_BGM_CANDIDATES = [
    "battle.wav",       # 추천 (진짜 wav)
    "battle.mp3",       # mp3면 이 이름 추천
    "battle.ogg",
    "battle.wav.mp3",   # (지금 네 파일명 형태)도 일단 후보로 포함
]

BGM_VOLUME = 90                # 0~128


# -------------------------------------------------
# 라운드 / UI 상수
# -------------------------------------------------
ROUND_TIME = 120.0
round_start_time = 0.0

# ================= HP 프레임 위치/크기 =================
HP_FRAME_Y   = H - 150
HP_FRAME_H   = 120

LEFT_HP_FRAME_W  = 600
RIGHT_HP_FRAME_W = 600

LEFT_HP_X  = 290
RIGHT_HP_X = W - 230

HP_INNER_MARGIN_X = 5
HP_INNER_MARGIN_Y = 12

# ================ HP 채우기(주황 바) 크기 ================
LEFT_HP_FILL_W_MAX  = 880
RIGHT_HP_FILL_W_MAX = 880

HP_FILL_H = 30

# ================= HP 주황바(채우기) 위치 미세조정 =================
# ✅ 이 값으로 "주황바 위치만" 이동 가능
LEFT_HP_FILL_OFFSET_X  = -110
RIGHT_HP_FILL_OFFSET_X = 180
HP_FILL_OFFSET_Y = 0

# ================= SP 프레임/바 위치/크기 =================
SP_OFFSET_Y = 22

LEFT_SP_X  = 255
RIGHT_SP_X = W - 200

LEFT_SP_FRAME_W  = 500
RIGHT_SP_FRAME_W = 500

SP_FRAME_H = 120

SP_INNER_MARGIN_X = 10
SP_INNER_MARGIN_Y = 4

LEFT_SP_FILL_W_MAX  = 380
RIGHT_SP_FILL_W_MAX = 480

SP_FILL_H = 60

# 타이머
TIMER_SCALE     = 0.35
TIMER_Y         = H - 120
TIMER_DIGIT_W   = 34
TIMER_DIGIT_H   = 52
TIMER_DIGIT_GAP = 4

# -------------------------------------------------
# 전투/게이지 상수
# -------------------------------------------------
DAMAGE_ATTACK  = 5
DAMAGE_SKILL1  = 20
DAMAGE_SKILL2  = 35
DAMAGE_SKILL3  = 50

SP_GAIN_ON_HIT = 10

SKILL1_COST = 20
SKILL2_COST = 35
SKILL3_COST = 50


def set_selected_index(index):
    global selected_character
    selected_character = index


# -------------------------------------------------
# 유틸
# -------------------------------------------------
ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

def _to_number(v, default=0.0):
    try:
        return float(v)
    except:
        return float(default)

def _get_attr_any(obj, names, default=None):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default

def _set_attr_any(obj, names, value):
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return True
    return False

def _load_image_candidates(base_name):
    candidates = [
        base_name + ".png",
        base_name,
        base_name.upper() + ".png",
        base_name.upper(),
        base_name.capitalize() + ".png",
        base_name.capitalize(),
    ]
    for name in candidates:
        path = os.path.join(ASSET_DIR, name)
        try:
            img = load_image(path)
            print(f"✅ IMAGE LOADED: {path}")
            return img
        except:
            pass
    print(f"❌ IMAGE LOAD FAIL: {base_name} (경로={ASSET_DIR}, 파일명 확인)")
    return None

# -------------------------------------------------
# ✅ BGM 유틸 (여기만 확실히 동작하도록 강화)
# -------------------------------------------------
def _start_bgm():
    global battle_bgm, battle_bgm_type
    if not battle_bgm:
        return

    try:
        battle_bgm.set_volume(BGM_VOLUME)
    except:
        pass

    # music이면 반복 재생이 거의 확실
    if battle_bgm_type == 'music':
        try:
            battle_bgm.repeat_play()
            return
        except:
            try:
                battle_bgm.play()
                return
            except:
                return

    # wav(Chunk)인 경우: 구현체에 따라 repeat_play가 없을 수 있음 -> 있으면 사용, 없으면 play라도
    try:
        battle_bgm.repeat_play()
    except:
        try:
            battle_bgm.play()
        except:
            pass

def _stop_bgm():
    global battle_bgm
    if not battle_bgm:
        return
    try:
        battle_bgm.stop()
    except:
        pass

def _load_and_play_bgm():
    """
    ✅ 핵심:
    - 후보 파일명들을 순회하면서 '존재하는 파일'을 먼저 찾고
    - load_music 우선 시도(반복재생 안정적)
    - 실패하면 load_wav로 재시도
    """
    global battle_bgm, battle_bgm_type

    battle_bgm = None
    battle_bgm_type = None

    # battle 관련 파일이 뭐가 있는지 디버그로 찍어주기
    try:
        files = os.listdir(ASSET_DIR)
        battle_like = [f for f in files if "battle" in f.lower()]
        print("🔎 ASSET_DIR battle files:", battle_like)
    except:
        pass

    for fname in BATTLE_BGM_CANDIDATES:
        path = os.path.join(ASSET_DIR, fname)
        if not os.path.exists(path):
            continue

        # 1) music로 먼저(반복재생 안정적)
        try:
            battle_bgm = load_music(path)
            battle_bgm_type = 'music'
            print(f"✅ BGM LOADED as MUSIC: {path}")
            _start_bgm()
            return
        except:
            battle_bgm = None
            battle_bgm_type = None

        # 2) wav로 재시도
        try:
            battle_bgm = load_wav(path)
            battle_bgm_type = 'wav'
            print(f"✅ BGM LOADED as WAV: {path}")
            _start_bgm()
            return
        except:
            battle_bgm = None
            battle_bgm_type = None
            print(f"⚠️ load_music/load_wav 둘 다 실패: {path}")

    print("❌ BGM LOAD FAIL: 파일명/경로/포맷 확인 필요")


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

    MARGIN_X = 200
    if is_left:
        c.x = MARGIN_X
        c.face_dir = 1
    else:
        c.x = W - MARGIN_X
        c.face_dir = -1

    c.dir = 0

    # 공격 히트 1회 제한 플래그
    c.attack_hit_done = False
    c._skill_paid_state = None

    return c


# -------------------------------------------------
# 몸통 충돌
# -------------------------------------------------
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
        overlap = min_distance - distance
        push = overlap / 2.0
        if dx > 0:
            player.x -= push
            enemy.x += push
        else:
            player.x += push
            enemy.x -= push


# -------------------------------------------------
# 스테이지 한계
# -------------------------------------------------
def clamp_fighters():
    STAGE_LEFT = 60
    STAGE_RIGHT = W - 60
    if player:
        player.x = max(STAGE_LEFT, min(STAGE_RIGHT, player.x))
    if enemy:
        enemy.x = max(STAGE_LEFT, min(STAGE_RIGHT, enemy.x))


# -------------------------------------------------
# AABB 충돌
# -------------------------------------------------
def aabb_intersect(box1, box2):
    l1, b1, r1, t1 = box1
    l2, b2, r2, t2 = box2
    if r1 < l2: return False
    if r2 < l1: return False
    if t1 < b2: return False
    if t2 < b1: return False
    return True


# -------------------------------------------------
# ✅ 공격/스킬 상태가 끝나면 hit_done 리셋
# -------------------------------------------------
def reset_attack_flag_if_needed(f):
    if not f or not hasattr(f, 'state_machine'):
        return

    cur = getattr(f.state_machine, 'cur_state', None)

    active_states = (
        getattr(f, 'ATTACK', None),
        getattr(f, 'ATTACK2', None),
        getattr(f, 'SKILL', None),
        getattr(f, 'SKILL2', None),
        getattr(f, 'SKILL3', None),
    )

    if cur in active_states:
        return

    name = ""
    try:
        name = cur.__name__
    except:
        try:
            name = cur.__class__.__name__
        except:
            name = ""
    up = name.upper()

    if ("ATTACK" in up) or ("SKILL" in up):
        return

    f.attack_hit_done = False


# -------------------------------------------------
# ✅ 스킬 상태 진입 순간 SP 1회 차감
# -------------------------------------------------
def pay_skill_cost_on_enter(f):
    if not f or not hasattr(f, 'state_machine'):
        return

    cur = getattr(f.state_machine, 'cur_state', None)
    s1 = getattr(f, 'SKILL', None)
    s2 = getattr(f, 'SKILL2', None)
    s3 = getattr(f, 'SKILL3', None)

    is_skill = (cur in (s1, s2, s3))
    if not is_skill:
        name = ""
        try:
            name = cur.__name__
        except:
            try:
                name = cur.__class__.__name__
            except:
                name = ""
        if "SKILL" in name.upper():
            is_skill = True

    if not is_skill:
        f._skill_paid_state = None
        return

    if getattr(f, '_skill_paid_state', None) is cur:
        return

    cost = SKILL1_COST
    if cur is s2:
        cost = SKILL2_COST
    elif cur is s3:
        cost = SKILL3_COST
    else:
        name = ""
        try:
            name = cur.__name__
        except:
            try:
                name = cur.__class__.__name__
            except:
                name = ""
        up = name.upper()
        if "SKILL2" in up:
            cost = SKILL2_COST
        elif "SKILL3" in up:
            cost = SKILL3_COST

    sp = _get_attr_any(f, ['sp', 'mp', 'mana'], 0)
    sp = max(0, _to_number(sp, 0) - cost)
    _set_attr_any(f, ['sp', 'mp', 'mana'], sp)

    f._skill_paid_state = cur


# -------------------------------------------------
# 전투 판정
# -------------------------------------------------
def handle_combat(attacker, defender):
    if not hasattr(attacker, 'get_attack_hitbox'):
        return
    if not hasattr(defender, 'get_hurtbox'):
        return

    hitbox = attacker.get_attack_hitbox()
    if hitbox is None:
        return

    hurtbox = defender.get_hurtbox()
    if not aabb_intersect(hitbox, hurtbox):
        return

    if attacker.attack_hit_done:
        return

    cur_state = getattr(attacker.state_machine, 'cur_state', None)

    damage = DAMAGE_ATTACK
    gain_sp = False

    if cur_state is getattr(attacker, 'SKILL', None):
        damage = DAMAGE_SKILL1
    elif cur_state is getattr(attacker, 'SKILL2', None):
        damage = DAMAGE_SKILL2
    elif cur_state is getattr(attacker, 'SKILL3', None):
        damage = DAMAGE_SKILL3
    else:
        name = ""
        try:
            name = cur_state.__name__
        except:
            try:
                name = cur_state.__class__.__name__
            except:
                name = ""
        up = name.upper()

        if "SKILL3" in up:
            damage = DAMAGE_SKILL3
        elif "SKILL2" in up:
            damage = DAMAGE_SKILL2
        elif "SKILL" in up:
            damage = DAMAGE_SKILL1
        else:
            if cur_state in (getattr(attacker, 'ATTACK', None), getattr(attacker, 'ATTACK2', None)):
                gain_sp = True
            elif "ATTACK" in up:
                gain_sp = True

    hp_before = _to_number(_get_attr_any(defender, ['hp', 'cur_hp', 'HP'], 0), 0)

    if hasattr(defender, 'take_hit'):
        defender.take_hit(damage, attacker.face_dir)

    hp_after = _to_number(_get_attr_any(defender, ['hp', 'cur_hp', 'HP'], hp_before), hp_before)

    if hp_after == hp_before:
        new_hp = max(0, hp_before - damage)
        _set_attr_any(defender, ['hp', 'cur_hp', 'HP'], new_hp)

    if gain_sp:
        sp = _get_attr_any(attacker, ['sp', 'mp', 'mana'], None)
        max_sp = _get_attr_any(attacker, ['max_sp', 'max_mp', 'max_mana'], None)
        if sp is not None and max_sp is not None:
            sp = min(_to_number(max_sp, 0), _to_number(sp, 0) + SP_GAIN_ON_HIT)
            _set_attr_any(attacker, ['sp', 'mp', 'mana'], sp)

    attacker.attack_hit_done = True


# -------------------------------------------------
# 타이머
# -------------------------------------------------
def get_remaining_time():
    global round_start_time
    elapsed = get_time() - round_start_time
    remain = ROUND_TIME - elapsed
    if remain < 0:
        remain = 0
    return int(remain)


# -------------------------------------------------
# ✅ 승패 판정
# -------------------------------------------------
def check_game_result():
    if player is None or enemy is None:
        return None

    p_hp = _to_number(_get_attr_any(player, ['hp', 'cur_hp', 'HP'], 1), 1)
    e_hp = _to_number(_get_attr_any(enemy,  ['hp', 'cur_hp', 'HP'], 1), 1)

    if p_hp <= 0 and e_hp <= 0:
        return 'DRAW'
    if e_hp <= 0:
        return 'WIN'
    if p_hp <= 0:
        return 'LOSE'

    if get_remaining_time() <= 0:
        return 'DRAW'

    return None


# -------------------------------------------------
# 초기화
# -------------------------------------------------
def init():
    global background, player, enemy, ai
    global ui_hp_frame, ui_sp_frame, ui_hp_fill, ui_sp_fill, ui_timer_bg
    global digit_images, round_start_time
    global img_win, img_lose, img_draw
    global result_state, result_start_time

    print("✅ play_mode.py init() 실행됨")
    result_state = None
    result_start_time = 0.0

    # 배경
    background = _load_image_candidates("Keroro_background")
    if background is None:
        try:
            background = load_image(os.path.join(ASSET_DIR, "Keroro_background.png"))
        except:
            background = None

    # 캐릭터 생성
    player_name = CHARACTERS[selected_character % len(CHARACTERS)]
    player = create_fighter(player_name, is_left=True)
    print(f"✅ Player1 : {player_name}")

    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates) if enemy_candidates else player_name
    enemy = create_fighter(enemy_name, is_left=False)
    print(f"✅ Enemy (AI) : {enemy_name}")

    ai = FighterAI(enemy, player)

    camera.init()
    print("✅ Camera init 완료")

    # UI 이미지
    try:
        ui_hp_frame = load_image(os.path.join(ASSET_DIR, 'ui_hp_frame.png'))
        ui_sp_frame = ui_hp_frame
    except:
        ui_hp_frame = None
        ui_sp_frame = None
        print("⚠️ ui_hp_frame.png 로드 실패")

    try:
        ui_hp_fill = load_image(os.path.join(ASSET_DIR, 'ui_hp_fill.png'))
    except:
        ui_hp_fill = None
        print("⚠️ ui_hp_fill.png 로드 실패")

    try:
        ui_sp_fill = load_image(os.path.join(ASSET_DIR, 'ui_sp_fill.png'))
    except:
        ui_sp_fill = None
        print("⚠️ ui_sp_fill.png 로드 실패")

    try:
        ui_timer_bg = load_image(os.path.join(ASSET_DIR, 'ui_timer.png'))
    except:
        ui_timer_bg = None
        print("⚠️ ui_timer.png 로드 실패")

    # 타이머 숫자 이미지
    digit_images = {}
    for ch in '0123456789':
        fname = f'timer{ch}.png'
        try:
            digit_images[ch] = load_image(os.path.join(ASSET_DIR, fname))
        except:
            digit_images[ch] = None

    try:
        digit_images[':'] = load_image(os.path.join(ASSET_DIR, 'timer_colon.png'))
    except:
        digit_images[':'] = None

    # 결과 이미지 로드
    img_win  = _load_image_candidates('win')
    img_lose = _load_image_candidates('lose')
    img_draw = _load_image_candidates('draw')

    # ✅ BGM 로드 & 재생 (전투 시작되면 바로 재생)
    _load_and_play_bgm()

    round_start_time = get_time()


def finish():
    _stop_bgm()
    global background, player, enemy, ai
    global ui_hp_frame, ui_sp_frame, ui_hp_fill, ui_sp_fill, ui_timer_bg, digit_images
    global img_win, img_lose, img_draw
    global result_state, result_start_time
    global battle_bgm, battle_bgm_type

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

    img_win = None
    img_lose = None
    img_draw = None

    result_state = None
    result_start_time = 0.0

    battle_bgm = None
    battle_bgm_type = None


# -------------------------------------------------
# 매 프레임 업데이트
# -------------------------------------------------
def update():
    global result_state, result_start_time

    # 결과 화면 중이면 3초 후 종료
    if result_state is not None:
        if get_time() - result_start_time >= RESULT_SHOW_TIME:
            game_framework.quit()
        return

    if player:
        player.update()
    if enemy:
        enemy.update()
    if ai:
        ai.update()

    if player:
        reset_attack_flag_if_needed(player)
        pay_skill_cost_on_enter(player)
    if enemy:
        reset_attack_flag_if_needed(enemy)
        pay_skill_cost_on_enter(enemy)

    clamp_fighters()
    resolve_body_collision()

    if player and enemy:
        handle_combat(player, enemy)
        handle_combat(enemy, player)

    camera.update(player, enemy, background)

    # 승패 판정
    res = check_game_result()
    if res is not None:
        result_state = res
        result_start_time = get_time()
        _stop_bgm()  # ✅ 결과 뜨는 순간 즉시 BGM 정지
        print(f"✅ RESULT = {result_state} (3초 후 종료)")


# -------------------------------------------------
# HP / SP UI 그리기 (OFFSET으로 "위치만" 이동 가능 버전)
# -------------------------------------------------
def draw_hp_sp_bar(fighter, side):
    global ui_hp_frame, ui_sp_frame, ui_hp_fill, ui_sp_fill

    if fighter is None:
        return

    max_hp = _to_number(getattr(fighter, 'max_hp', 100), 100)
    hp     = _to_number(getattr(fighter, 'hp', max_hp), max_hp)
    max_sp = _to_number(getattr(fighter, 'max_sp', 100), 100)
    sp     = _to_number(getattr(fighter, 'sp', 0), 0)

    hp_ratio = 0.0 if max_hp <= 0 else max(0.0, min(1.0, hp / max_hp))
    sp_ratio = 0.0 if max_sp <= 0 else max(0.0, min(1.0, sp / max_sp))

    hp_y = HP_FRAME_Y
    sp_y = HP_FRAME_Y - SP_OFFSET_Y

    if side == 'left':
        hp_base_x      = LEFT_HP_X
        hp_frame_w     = LEFT_HP_FRAME_W
        hp_fill_w_max  = LEFT_HP_FILL_W_MAX

        sp_base_x      = LEFT_SP_X
        sp_frame_w     = LEFT_SP_FRAME_W
        sp_fill_w_max  = LEFT_SP_FILL_W_MAX

        offset_x = LEFT_HP_FILL_OFFSET_X
        anchor_left = True
    else:
        hp_base_x      = RIGHT_HP_X
        hp_frame_w     = RIGHT_HP_FRAME_W
        hp_fill_w_max  = RIGHT_HP_FILL_W_MAX

        sp_base_x      = RIGHT_SP_X
        sp_frame_w     = RIGHT_SP_FRAME_W
        sp_fill_w_max  = RIGHT_SP_FILL_W_MAX

        offset_x = RIGHT_HP_FILL_OFFSET_X
        anchor_left = False

    # HP 프레임
    if ui_hp_frame:
        ui_hp_frame.draw(hp_base_x, hp_y, hp_frame_w, HP_FRAME_H)

    frame_left  = hp_base_x - hp_frame_w / 2
    frame_right = hp_base_x + hp_frame_w / 2
    hp_inner_left  = frame_left  + HP_INNER_MARGIN_X
    hp_inner_right = frame_right - HP_INNER_MARGIN_X

    # ✅ OFFSET으로 주황바 "전체 기준 위치" 이동 (clamp 금지)
    if side == 'left':
        full_left  = hp_inner_left + offset_x
        full_right = full_left + hp_fill_w_max
        anchor_left = True
    else:
        full_right = hp_inner_right + offset_x
        full_left  = full_right - hp_fill_w_max
        anchor_left = False

    # ----------------- HP 채우기(주황) -----------------
    if ui_hp_fill and hp_ratio > 0.0:
        img = ui_hp_fill

        cur_w = float(hp_fill_w_max) * hp_ratio
        if cur_w <= 0:
            return

        if anchor_left:
            desired_l = full_left
            desired_r = full_left + cur_w
        else:
            desired_l = full_right - cur_w
            desired_r = full_right

        if desired_r <= hp_inner_left:
            shift = (hp_inner_left + 1) - desired_r
            desired_l += shift
            desired_r += shift
        elif desired_l >= hp_inner_right:
            shift = (hp_inner_right - 1) - desired_l
            desired_l += shift
            desired_r += shift

        draw_l = max(desired_l, hp_inner_left)
        draw_r = min(desired_r, hp_inner_right)
        draw_w = draw_r - draw_l
        if draw_w <= 0:
            return

        dst_w = max(1, int(draw_w))

        src_full_w = img.w
        src_h = img.h
        src_w = max(1, int(src_full_w * hp_ratio))

        u0 = (draw_l - desired_l) / cur_w
        u1 = (draw_r - desired_l) / cur_w
        u0 = max(0.0, min(1.0, u0))
        u1 = max(0.0, min(1.0, u1))

        if anchor_left:
            src_seg_left = 0
        else:
            src_seg_left = src_full_w - src_w

        src_left = int(src_seg_left + u0 * src_w)
        src_clip_w = max(1, int((u1 - u0) * src_w))

        dst_cx = (draw_l + draw_r) / 2
        dst_y = hp_y + HP_FILL_OFFSET_Y

        img.clip_draw(
            int(src_left), 0,
            int(src_clip_w), int(src_h),
            int(dst_cx), int(dst_y),
            int(dst_w), int(HP_FILL_H)
        )

    # ----------------- SP 프레임 -----------------
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

    # ----------------- SP 채우기(파랑) -----------------
    if ui_sp_fill and sp_ratio > 0.0:
        img = ui_sp_fill

        cur_w = sp_draw_w_max * sp_ratio
        dst_h = SP_FILL_H

        src_full_w = img.w
        src_h      = img.h
        src_w      = max(1, int(src_full_w * sp_ratio))

        if side == 'left':
            sp_anchor_left = True
        else:
            sp_anchor_left = False

        if sp_anchor_left:
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
    global result_state, img_win, img_lose, img_draw

    clear_canvas()

    zoom = camera.get_zoom()
    cx, cy = camera.get_center()

    # 배경
    if background:
        src_w = int(W / zoom)
        src_h = int(H / zoom)

        bx = int(cx - src_w / 2)
        by = int(cy - src_h / 2)

        if bx < 0: bx = 0
        if by < 0: by = 0
        if bx + src_w > background.w: bx = background.w - src_w
        if by + src_h > background.h: by = background.h - src_h

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

    # 결과 화면 오버레이(정중앙)
    if result_state is not None:
        img = None
        if result_state == 'WIN':
            img = img_win
        elif result_state == 'LOSE':
            img = img_lose
        elif result_state == 'DRAW':
            img = img_draw

        if img:
            img.draw(W // 2, H // 2)
        else:
            draw_text(W // 2 - 40, H // 2, result_state)

    update_canvas()


# -------------------------------------------------
# 입력 처리
# -------------------------------------------------
def handle_events():
    global player, result_state
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            _stop_bgm()
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            _stop_bgm()
            game_framework.quit()

        if result_state is not None:
            continue

        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
