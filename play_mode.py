# play_mode.py

from pico2d import *
import game_framework

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu
from fighter_ai import FighterAI   # ✅ 적 인공지능

background = None
player = None
enemy = None
enemy_ai = None

# select_mode에서 넘겨주는 인덱스
selected_character = 0

# 선택 화면 인덱스 기준 캐릭터 이름
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


def set_selected_index(index):
    """select_mode에서 호출해서 플레이어 캐릭터 인덱스 설정"""
    global selected_character
    selected_character = index


def create_character_by_name(name, x, y, face_dir=1):
    """문자열 이름으로 캐릭터 객체 생성 + 위치/방향 설정"""
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
        # 혹시 이상한 이름 들어오면 기본 Dororo
        c = Dororo()

    c.x = x
    c.y = y
    c.face_dir = face_dir
    return c


def init():
    global background, player, enemy, enemy_ai

    # 배경 이미지 로드
    try:
        background = load_image('Keroro_background.png')
    except:
        print("⚠️ 'Keroro_background.png' 파일이 없습니다. 기본 회색 배경으로 대체합니다.")
        background = None

    # ✅ 플레이어 캐릭터 생성 (select_mode에서 선택한 캐릭터)
    player_name = CHARACTERS[selected_character]
    player_start_x = 400
    player_start_y = 90
    player_face_dir = 1  # 오른쪽을 보도록

    player_char = create_character_by_name(player_name,
                                           x=player_start_x,
                                           y=player_start_y,
                                           face_dir=player_face_dir)

    # 전역 변수에 넣기
    globals()['player'] = player_char

    # ✅ 적 캐릭터 랜덤 생성 (플레이어와 다른 캐릭터 중에서)
    import random
    enemy_candidates = [n for n in CHARACTERS if n != player_name]
    enemy_name = random.choice(enemy_candidates)

    enemy_start_x = 1200
    enemy_start_y = 90
    enemy_face_dir = -1  # 왼쪽을 보도록

    enemy_char = create_character_by_name(enemy_name,
                                          x=enemy_start_x,
                                          y=enemy_start_y,
                                          face_dir=enemy_face_dir)

    globals()['enemy'] = enemy_char

    # ✅ 적 인공지능 생성 (enemy가 player를 보고 행동)
    globals()['enemy_ai'] = FighterAI(enemy_char, player_char)

    print(f"✅ Player: {player_name}, Enemy: {enemy_name} 로드 완료 — 전투 시작!")


def finish():
    """게임 모드 종료 시 정리"""
    global background, player, enemy, enemy_ai
    background = None
    player = None
    enemy = None
    enemy_ai = None


def update():
    """게임 한 프레임 업데이트"""
    global player, enemy, enemy_ai

    # 🟢 플레이어는 키보드 입력으로 상태가 바뀌고, 여기서 애니메이션/위치 갱신
    if player:
        player.update()

    # 🔴 적은 AI가 행동 결정 → 그 다음에 적 캐릭터 업데이트
    if enemy:
        if enemy_ai:
            enemy_ai.update()    # 여기서 enemy.dir, 공격 상태, 가드 상태 등 변경
        enemy.update()

    # ⚠️ 아직은 충돌처리 잠깐 끈 상태 (움직임 확인 먼저)
    # 이후에 다시 넣을 예정
    # resolve_body_collision(player, enemy)
    # resolve_attack_collision(player, enemy)
    # resolve_attack_collision(enemy, player)


def draw():
    """화면 그리기"""
    clear_canvas()

    # 배경
    if background:
        background.draw(800, 450, 1600, 900)
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    # 캐릭터 그리기
    if player:
        player.draw()
    if enemy:
        enemy.draw()

    update_canvas()


def handle_events():
    """입력 처리: 플레이어에게만 키 입력 전달, 적은 AI가 알아서"""
    global player
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()

        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()

        # ✅ 키보드 입력은 플레이어에게만 전달
        if player:
            player.handle_event(e)


def pause():
    pass


def resume():
    pass
