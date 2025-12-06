from pico2d import *
import game_framework
import random

from Keroro import Keroro
from Dororo import Dororo
from Tamama import Tamama
from Giroro import Giroro
from Kururu import Kururu

from fighter_ai import FighterAI  # ✅ 방금 만든 AI 클래스

background = None
player = None
enemy = None
enemy_ai = None

selected_character = 0  # 플레이어 선택 인덱스


# ✅ select_mode에서 전달받을 캐릭터 인덱스
def set_selected_index(index):
    global selected_character
    selected_character = index


# 캐릭터 이름 목록 (선택창 인덱스 순서)
CHARACTERS = ['Dororo', 'Tamama', 'Keroro', 'Giroro', 'Kururu']


def _create_character_by_name(name):
    if name == 'Keroro':
        return Keroro()
    elif name == 'Dororo':
        return Dororo()
    elif name == 'Tamama':
        return Tamama()
    elif name == 'Giroro':
        return Giroro()
    elif name == 'Kururu':
        return Kururu()
    else:
        print("⚠️ 알 수 없는 캐릭터 이름:", name)
        return None


def init():
    global background, player, enemy, enemy_ai

    try:
        background = load_image('Keroro_background.png')
    except:
        print("⚠️ 'Keroro_background.png' 파일이 없습니다. 기본 회색 배경으로 대체합니다.")
        background = None

    # ✅ 1) 플레이어 캐릭터 생성 (선택된 인덱스 기반)
    player_name = CHARACTERS[selected_character]
    player = _create_character_by_name(player_name)
    if player is None:
        print("⚠️ 잘못된 캐릭터 인덱스입니다. 기본 Dororo로 설정합니다.")
        player = Dororo()
        player_name = 'Dororo'

    # 위치 지정 (왼쪽)
    player.x, player.y = 400, 90

    # ✅ 2) 적 캐릭터 랜덤 생성
    enemy_name = random.choice(CHARACTERS)
    enemy = _create_character_by_name(enemy_name)

    # 위치 지정 (오른쪽)
    if enemy:
        enemy.x, enemy.y = 1200, 90




def finish():
    global background, player, enemy, enemy_ai
    if background:
        del background
    if player:
        del player
    if enemy:
        del enemy
    enemy_ai = None


def update():



def draw():
    clear_canvas()

    # 배경 그리기
    if background:
        background.draw(800, 450, 1600, 900)
    else:
        set_clear_color(0.5, 0.5, 0.5, 1.0)
        clear_canvas()

    # 캐릭터 애니메이션 그리기
    if player:
        player.draw()
    if enemy:
        enemy.draw()

    update_canvas()


def handle_events():



def pause(): pass
def resume(): pass
