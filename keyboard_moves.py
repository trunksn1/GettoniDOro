from pynput.keyboard import Key, Listener
from mouse_moves import get_cords_old, get_cords_new
from helpers import ocr_test


cords = []

def on_press(key):
    global cords
    print('{0} pressed'.format(key))
    if key == Key.f4:
        """Cliccando col mouse inizi a selezionare lo schermo, rilasci per terminare"""
        cords = []
        cords = get_cords_old()
        return False
    if key == Key.f6:
        cords = []
        cords = get_cords_new()
        return False
    if key == Key.f9:
        """Riprende le coordinate dell'ultima schermata catturata"""
        if cords:
            return False
    if key == Key.f7:
        """Per testare"""
        ocr_test()
        return False



def start_screen_grab():
    print('Adesso premi F4, F9 o F6 (quest\'ultimo è ancora in fase di test)')
    with Listener(on_press=on_press) as listener:
        listener.join()
    return cords

