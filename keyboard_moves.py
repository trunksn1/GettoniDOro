from pynput.keyboard import Key, Listener
from mouse_moves import get_cords_old, get_cords_new
from helpers import ocr_test


cords = []

def on_press(key):
    global cords
    print('{0} pressed'.format(key))
    if key == Key.f4:
        cords = []
        cords = get_cords_old()
        return False
    if key == Key.f6:
        cords = []
        cords = get_cords_new() # in realtà ho creato get_cords_old()
        return False
    if key == Key.f9:
        if cords:
            return False
    if key == Key.f7:
        ocr_test()
        return False



def start_screen_grab():
    print('Clicca il bottone sinistro e trascina il mouse per selezionare l\'area del quiz')
    with Listener(on_press=on_press) as listener:
        listener.join()
    return cords
