from pico2d import *
import game_framework
import play_mode

image = None
start_image = None
exit_image = None
controls_image = None
controls_key_image = None
select_image = None  # ✅ 캐릭터 선택창 이미지 추가

menu_index = 0  # 0: Start, 1: Controls, 2: Exit


def init():
    global image, start_image, exit_image, controls_image, controls_key_image, select_image
    image = load_image('Keroro_title.png')
    start_image = load_image('logo_start.png')
    controls_image = load_image('logo_controls.png')
    exit_image = load_image('logo_exit.png')
    controls_key_image = load_image('controls_key.png')  # Controls 설명 이미지
    select_image = load_image('Keroro_select.png')      


def finish():
    global image, start_image, exit_image, controls_image, controls_key_image, select_image
    del image, start_image, exit_image, controls_image, controls_key_image, select_image


def update():
    pass


def draw():
    clear_canvas()
    image.draw(800, 450, 1600, 900)

    # 기본 크기
    normal_w, normal_h = 400, 150
    big_w, big_h = 500, 190  # 선택된 항목 크기

    # Start
    if menu_index == 0:
        start_image.draw(800, 450, big_w, big_h)
        # ✅ Start가 선택되면 캐릭터 선택창 표시
        select_image.draw(800, 300, 1000, 600)
    else:
        start_image.draw(800, 450, normal_w, normal_h)

    # Controls
    if menu_index == 1:
        controls_image.draw(800, 300, big_w, big_h)
        # Controls가 선택된 경우 키 설명 표시
        controls_key_image.draw(1350, 150, 400, 250)
    else:
        controls_image.draw(800, 300, normal_w, normal_h)

    # Exit
    if menu_index == 2:
        exit_image.draw(800, 150, big_w, big_h)
    else:
        exit_image.draw(800, 150, normal_w, normal_h)

    update_canvas()


def handle_events():
    global menu_index
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_DOWN:
                menu_index = (menu_index + 1) % 3  # 아래로 이동
            elif event.key == SDLK_UP:
                menu_index = (menu_index - 1) % 3  # 위로 이동
            elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                if menu_index == 0:
                    # 캐릭터 선택창을 표시 (지금은 draw()에서 자동 표시)
                    print("Start 선택됨 - 캐릭터 선택창 표시")
                elif menu_index == 1:
                    print("Controls 선택됨")
                elif menu_index == 2:
                    game_framework.quit()


def pause():
    pass


def resume():
    pass
