import win32gui, win32api, win32con
import csv, os, time
from Quiz import Quiz
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
from ScreenGrabber import ScreenGrab
from cf import mult, y_inizio_domanda, tupla_coord_bottone_errore_screenshot
from random import choice
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
        rect = (rect[0], rect[1] + y_inizio_domanda, rect[2], rect[3])
        print("\tLocation: (%d, %d)" % (x, y))
        print("\t    Size: (%d, %d)" % (w, h))
        return rect
    else:
        print('PROGRAM NOT FOUND!')
        time.sleep(60)
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


def are_valid_coords_for_risposte(coords):
    if len(coords) < 6:
        print("Non trovato 6 coordinate per le caselle")
        return False
    if (coords[0] - coords[1] < 400) or (coords[2] - coords[3] < 400) or (coords[4] - coords[5] < 400):
        print('qualche problema a trovare una casella risposte')
        return False
    return True


def trova_risposta_esatta(diz_risp_coord_punteggi, str_domanda):
    keyword = ["NON", "FALSO", "FALSA"]
    domanda_negativa = any(k in str_domanda for k in keyword)
    print(domanda_negativa)
    print(str_domanda)
    risp_giusta = []
    max = 0
    min = 11
    for risp in diz_risp_coord_punteggi:
        somma = diz_risp_coord_punteggi[risp]['_d_R_'] + diz_risp_coord_punteggi[risp]['_dr_R_']
        diz_risp_coord_punteggi[risp].update({"TOT": somma})
        if not domanda_negativa:
        #if keyword not in str_domanda:
            """Indica la risposta col punteggio più alto"""
            print('MAX')
            if somma > max:
                risp_giusta = [risp]
                max = somma
            elif somma == max:
                risp_giusta.append(risp)
        else:
            """Indica la risposta col punteggio più basso"""
            print('MIN')
            if somma < min:
                risp_giusta = [risp]
                min = somma
            elif somma == min:
                risp_giusta.append(risp)
    return risp_giusta


def clicka_risposta(x,y):
    print('Cliccato {}, {}'.format(x,y))
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


def scrivi_diario_csv(domanda, diz_risposte, scelta):
    print('SCRIVERO')
    #immagini_da_studiare = glob.glob(os.path.join(PATH_DOM_RSP, '*'), recursive=True)
    with open('auto_diario.csv', 'a') as log:
        scrivente = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        mess = '****** Domanda numero: {} ******'
        scrivente.writerow([])
        scrivente.writerow([mess, '****', '****', '****'])
        scrivente.writerow([domanda, 'SoloD', '+Risp', 'TOT'])
        for k in diz_risposte:
            scrivente.writerow([k, diz_risposte[k]['_d_R_'], diz_risposte[k]['_dr_R_'], diz_risposte[k]['TOT']])
        scrivente.writerow([scelta])



if __name__ == '__main__':
    while True:
        cords = get_bluestacks_coords()
        if not cords:
            time.sleep(1)
            continue
        screen_grabber = ScreenGrab(cords)
        screen_grabber.screen_grab('prova')

        # Se è stato fatto un errore ed è comparsa la schermata da cliccare allora clicca sul bottone per proseguire
        coord_centro_risposta_errata = screen_grabber.im.getpixel(tupla_coord_bottone_errore_screenshot)
        if coord_centro_risposta_errata == (53, 204, 252):    # Trovo un pixel azzurro tipico della casella dell'erroe
            print('RISPOSTA SBAGLIATA')
            x_errore = int(cords[0] + tupla_coord_bottone_errore_screenshot[0]) #coordinate della finestra di bluestack
            y_errore = int(cords[1] + tupla_coord_bottone_errore_screenshot[1])
            clicka_risposta(x_errore, y_errore)
            time.sleep(3)
            continue

        el = Elaboratore(screen_grabber.screenshot_name)

        if not are_valid_coords_for_risposte(el.y):
            print('Non trovo una casella di risposte!')
            time.sleep(2)
            os.remove(el.screenshot_name)
            continue

        if el.cords:
            el.salva_i_pezzi()
        else:
            print('Non trovo una casella di risposte!')
            time.sleep(2)
            continue

        lista_tuple_coord_risposte = get_cords_risposte_da_cliccare(cords[:2], el.cords[1:])

        id = Identificatore(el.pezzi)
        pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda, lista_tuple_coord_risposte)

        print(pp.dizionario_di_risposte_e_key_punteggi)
        lista_risp_giusta = trova_risposta_esatta(pp.dizionario_di_risposte_e_key_punteggi, id.domanda)

        if len(lista_risp_giusta) > 1:
            scelta = choice(lista_risp_giusta)
        else:
            scelta = lista_risp_giusta[0]
        print(pp.dizionario_di_risposte_e_key_punteggi[scelta]['coord_click'])
        print(type(pp.dizionario_di_risposte_e_key_punteggi[scelta]['coord_click']))
        clicka_risposta(*pp.dizionario_di_risposte_e_key_punteggi[scelta]['coord_click'])
        #pp.rendo_template_html()
        try:
            scrivi_diario_csv(id.domanda, pp.dizionario_di_risposte_e_key_punteggi, scelta)
        except Exception as e:
            print(e)
        time.sleep(15)

        #clicka_risposta(*lista_tuple_coord_risposte[0])
        #break