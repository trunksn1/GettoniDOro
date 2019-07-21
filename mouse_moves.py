from pynput import mouse
from cf import mult

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
    global cords
    cords = []
    print('Clicca il bottone sinistro e trascina il mouse per selezionare l\'area del quiz')
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

        cord_domande, cord_risposte = calcolo_spazi_domande_e_risposte(cords[0])
        lista_dom_lista_risp = [cord_domande] + [cord_risposte]
        return lista_dom_lista_risp
        #Da una lista di due tuple, ottengo una lista di singoli elementi
        #c = [el for tupla in cords for el in tupla]
        #return tuple(c)

def get_cords_old():
    global cords
    cords = []
    print('Clicca il bottone sinistro e trascina il mouse per selezionare l\'area del quiz')
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        #Da una lista di due tuple, ottengo una lista di singoli elementi
        c = [el for tupla in cords for el in tupla]
        return tuple(c)

def calcolo_spazi_domande_e_risposte(cords):
    print(cords, type(cords[0]))
    fine_domande = [cords[0] + 470, cords[1] + 140]
    spazio_domande = list(cords) + fine_domande

    inizio_risposte = [cords[0], cords[1] + 165]
    fine_risposte = [cords[0] + 470, inizio_risposte[1] + 290]
    spazio_risposte = inizio_risposte + fine_risposte
    print(spazio_domande)
    print(spazio_risposte)
    return spazio_domande, spazio_risposte