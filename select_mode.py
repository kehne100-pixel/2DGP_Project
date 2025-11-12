from pico2d import *
import game_framework
import play_mode

image = None
selected_index = 0  # 현재 선택된 캐릭터 번호 (0~4)

def init():
    global image
    image = load_image('Keroro_select.png')


def finish():
    global image
    del image


def update():
    pass


def draw():
    clear_canvas()
    image.draw(800, 450, 1600, 900)


    x_positions = [320, 640, 960, 1280, 1600]
    if selected_index < len(x_positions):
        x = x_positions[selected_index]
        draw_rectangle(x - 80, 200, x + 80, 700)

    update_canvas()


def handle_events():
    global selected_index
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(play_mode)  # 뒤로가기
            elif event.key == SDLK_RIGHT:
                selected_index = (selected_index + 1) % 5
            elif event.key == SDLK_LEFT:
                selected_index = (selected_index - 1) % 5
            elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                print(f"캐릭터 {selected_index} 선택됨")
                game_framework.change_mode(play_mode)


def pause():
    pass


def resume():
    pass
