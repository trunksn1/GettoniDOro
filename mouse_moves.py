from pynput import mouse
from cf import mult, x_finale, y_finale_domande, y_finale_risposte, y_iniziale_risposte

cords = []

def on_click(x, y, button, pressed):
    """Funzione che prende le coordinate del puntatore del mouse prima quando clicchi e poi quando rilasci"""
    global cords
    if pressed:
        print('Pressed at {0}'.format((x,y)))
        cords.append((x, y))
        #cords.append(x)
        #cords.append(y)
       #return False
    else:
        print('Released at {0}'.format((x, y)))
        cords.append((x, y))
        return False


def get_cords_new():
    """Si attiva dopo aver premuto F6"""
    #restituisce una lista
    global cords
    cords = []
    print('Clicca tasto sinistro nell\'angolo in alto a sinistra della domanda.')
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

        cord_domande, cord_risposte = calcolo_spazi_domande_e_risposte(cords[0])
        lista_dom_lista_risp = [cord_domande] + [cord_risposte]
        return lista_dom_lista_risp


def calcolo_spazi_domande_e_risposte(cords):
    #prende una tupla e restituisce una lista
    print(cords, type(cords)) # Tupla
    fine_domande = [cords[0] + x_finale, cords[1] + y_finale_domande]
    coordinate_domande = list(cords) + fine_domande

    inizio_risposte = [cords[0], cords[1] + y_iniziale_risposte]
    fine_risposte = [cords[0] + x_finale, inizio_risposte[1] + y_finale_risposte]
    coordinate_risposte = inizio_risposte + fine_risposte
    print(coordinate_domande)
    print(coordinate_risposte)
    return coordinate_domande, coordinate_risposte


def get_cords_old():
    """Si attiva dopo aver premuto F4"""
    #restituisce una tupla
    global cords
    cords = []
    print('Clicca il bottone sinistro e trascina il mouse per selezionare l\'area del quiz')
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        #Da una lista di due tuple, ottengo una lista di singoli elementi
        c = [el for tupla in cords for el in tupla]
        return tuple(c)