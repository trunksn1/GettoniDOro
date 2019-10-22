import win32gui, win32api, win32con
import os, time
from Quiz import Quiz
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
from ScreenGrabber import ScreenGrab
from cf import mult
from collections import OrderedDict

    #TODO capisco dove si trova il quiz ed ottengo lo screenshot del quiz
    #TODO con la funzione di fabrizio vedo se trovo i box delle risposte
    #TODO se le trovo avvio la funzione che ottiene la domanda e fa la ricerca ottenendo i punteggi
    # a questo punto clicco sulla risposta con il punteggio più alto
    #TODO servirà quindi avere le coordinate delle singole risposte
    #TODO servirà capire come cliccarci
    # se più risposte hanno lo stesso punteggio clicco su una a random
    # se la domanda contiene un NON/Falso/Falsa clicco sulla risposta con meno punti, se pari si fa a random
    # fine, invio uno screenshot col risultato finale al telefono

"""
def callback(hwnd, extra):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    print("Window %s:" % win32gui.GetWindowText(hwnd))
    print("\tLocation: (%d, %d)" % (x, y))
    print("\t    Size: (%d, %d)" % (w, h))
"""

def get_bluestacks_coords():
    #win32gui.EnumWindows(callback, None)
    win2find = "BlueStacks"
    whnd = win32gui.FindWindowEx(None, None, None, win2find)
    if not (whnd == 0):
        print('FOUND!')
        rect = win32gui.GetWindowRect(whnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        print("\tLocation: (%d, %d)" % (x, y))
        print("\t    Size: (%d, %d)" % (w, h))
        return rect
    else:
        print('PROGRAM NOT FOUND!')
        return

def get_cords_risposte_da_cliccare(posizione_finestra_bluestacks, coords_elaboratore):
    """Usa solo le coordinate delle risposte!
    Ottengo il punto centrale della casella delle tre risposte!"""
    lista_coord_risp_wnd_bluestack = []
    print(posizione_finestra_bluestacks)
    print(coords_elaboratore)
    for coord in coords_elaboratore:
        #Prima ottengo le coordinate del punto posto al centro di ciascuna delle tre caselle delle risposte dall'
        # immagine rielaborata (e ingrandita di tante volte quanto è il valore di mult)
        x_media = (coord[0] + coord[2]) // 2
        y_media = (coord[1] + coord[3]) // 2
        # Calcolo adesso il punto centrale delle caselle delle risposte sul quiz!
        x_da_cliccare = (x_media // mult) + posizione_finestra_bluestacks[0]
        y_da_cliccare = (y_media // mult) + posizione_finestra_bluestacks[1]
        # Aggiungo il risultato come una tupla. La lista che compongo alla fine conterrà tre tuple,
        lista_coord_risp_wnd_bluestack.append((x_da_cliccare, y_da_cliccare))
    return lista_coord_risp_wnd_bluestack

def clicka_risposta(x,y):
    print('Cliccato {}, {}'.format(x,y))
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def are_valid_coords_for_risposte(coords):
    if (coords[0] - coords[1] < 400) or (coords[2] - coords[3] < 400) or (coords[4] - coords[5] < 400):
        print('qualche problema a trovare una casella risposte')
        return False
    return True

def trova_risposta_esatta(diz_risp_e_key_punteggi, lista_coord_click_su_risposte, str_domanda):
    keyword = ["NON", "FALSO", "FALSA"]
    #if not keyword in str_domanda:

    for k in diz_risp_e_key_punteggi:
        somma = diz_risp_e_key_punteggi[k]['_d_R_'] + diz_risp_e_key_punteggi[k]['_dr_R_']
        diz_risp_e_key_punteggi[k].update({"TOT": somma})


    if keyword not in str_domanda:
        """Indica la risposta col punteggio più alto"""

        pass
    else:
        pass


if __name__ == '__main__':
    quiz = Quiz()
    while True:
        cords = get_bluestacks_coords()
        if not cords:
            time.sleep(2)
            continue
        quiz.coordinate_bluestacks = cords
        screen_grabber = ScreenGrab(cords)
        screen_grabber.screen_grab('prova')
        el = Elaboratore(screen_grabber.screenshot_name)

        if not are_valid_coords_for_risposte(el.y):
            print('Non trovo una casella di risposte!')
            time.sleep(2)
            os.remove(el.screenshot_name)
            continue

        el.salva_i_pezzi()
        lista_tuple_coord_risposte = get_cords_risposte_da_cliccare(cords[:2], el.cords[1:])

        id = Identificatore(el.pezzi)
        pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda)
        diz_risposte_ordinato = OrderedDict(pp.dizionario_di_risposte_e_key_punteggi)
        print(pp.dizionario_di_risposte_e_key_punteggi)
        print(diz_risposte_ordinato)
        print(id.risposte)
        break

        #clicka_risposta(*lista_tuple_coord_risposte[0])
        #break