from pynput import mouse

cords = []

def on_click(x, y, button, pressed):
    """Funzione che prende le coordinate del puntatore del mouse prima quando clicchi e poi quando rilasci"""
    global cords
    if pressed:
        print('Pressed at {0}'.format((x,y)))
        cords.append((x, y))
    else:
        print('Released at {0}'.format((x, y)))
        cords.append((x, y))
        return False


def get_cords():
    global cords
    cords = [] 
    print('Clicca il bottone sinistro e trascina il mouse per selezionare l\'area del quiz')
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        print(cords)

        #Da una lista di due tuple, ottengo una lista di singoli elementi
        c = [el for tupla in cords for el in tupla]
        return tuple(c)