import win32gui, win32api, win32con
import csv, os, time
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
from Sarto import Sarto
from ScreenGrabber import ScreenGrab
from cf import mult, y_inizio_domanda
from random import choice


    #TODO capisco dove si trova il quiz ed ottengo lo screenshot del quiz
    #TODO con la funzione di fabrizio vedo se trovo i box delle risposte
    #TODO se le trovo avvio la funzione che ottiene la domanda e fa la ricerca ottenendo i punteggi
    # a questo punto clicco sulla risposta con il punteggio più alto
    #TODO servirà quindi avere le coordinate delle singole risposte
    #TODO servirà capire come cliccarci
    # se più risposte hanno lo stesso punteggio clicco su una a random
    # se la domanda contiene un NON/Falso/Falsa clicco sulla risposta con meno punti, se pari si fa a random
    # fine, invio uno screenshot col risultato finale al telefono


def get_bluestacks_coords():
    #win32gui.EnumWindows(callback, None)
    win2find = "BlueStacks"
    #win2find = "Cazzstacks.mkv - Lettore multimediale VLC"
    #win2find = "VLC (Direct3D output)"
    #win2find = "Stacks.png - IrfanView"
    whnd = win32gui.FindWindowEx(None, None, None, win2find)
    if not (whnd == 0):
        print('FOUND!')
        rect = win32gui.GetWindowRect(whnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        #rect = (rect[0], rect[1] + y_inizio_domanda, rect[2], rect[3])
        print("\tLocation: (%d, %d)" % (x, y))
        print("\t    Size: (%d, %d)" % (w, h))
        return rect
    else:
        print('PROGRAM NOT FOUND!')
        time.sleep(60)
        return

def callback(hwnd, extra):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    print("Window %s:" % win32gui.GetWindowText(hwnd))
    #print("\tLocation: (%d, %d)" % (x, y))
    #print("\t    Size: (%d, %d)" % (w, h))


def get_cords_risposte_da_cliccare(posizione_finestra_bluestacks, coords_elaboratore):
    """Usa solo le coordinate delle risposte!+++++
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


def get_punto_msg_errore(coords_quiz):
    altezza = coords_quiz[3] - coords_quiz[1]
    larghezza = coords_quiz[2] - coords_quiz[0]

    y_in = (0.682 * altezza) + coords_quiz[1]
    y_fin = (0.747 * altezza) + coords_quiz[1]

    x_sin = (0.139 * larghezza) + coords_quiz[0]
    x_des = (0.86 * larghezza) + coords_quiz[0]
    punto = int(((x_sin + x_des) / 2)), int(((y_in + y_fin) / 2) + 20)
    print(coords_quiz)
    print("PUNTO ERRORE\n", punto)
    return punto

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



def correggi_punto(cordinate_programma, punto_da_correggere):
    x = punto_da_correggere[0] + cordinate_programma[0]
    y = punto_da_correggere[1] + cordinate_programma[1]
    return x,y

def clicka_risposta(x, y):
    print('Cliccato {}, {}'.format(x,y))
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def sposta_mouse_dalle_palle():
    win32api.SetCursorPos((0, 0))


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
        # 1 Ottengo le coordinate del programma Bluestacks
        # coords = [x_a_sx, y_a_sx, x_b_dx, y_b_dx]
        cord_domanda = ''
        punto_errore = ''
        punto_corretto = ''

        sarto = Sarto()
        print(sarto.inizializzato)
        if sarto.inizializzato:
            #cords_programma = sarto.get_program_cords('VLC (Direct3D output)')
            cords_programma = sarto.get_program_cords('BlueStacks')
            # Se Bluestacks non viene trovato, ricercarlo tra 60 secondi
            if not cords_programma:
                sarto.inizializzato = False
                time.sleep(60)
                continue
            cord_domanda = sarto.get_cords_domande_e_risposte()
            punto_errore = sarto.get_punto_msg_errore()
            punto_corretto = sarto.correggi_punto(cords_programma, punto_errore)

        #cords = get_bluestacks_coords()

        # 2 Catturiamo la schermata di BlueStacks
        screen_grabber = ScreenGrab(cord_domanda)
        # La schermata catturata viene ristretta alla zona in cui compaiono le parti signfiicative:
        # Domanda con risposte, schermata di errore per continuare
        #screen_grabber.calcolo_spazi_domande_e_risposte(is_solitario=True)
        # Viene salvato lo screenshot della schermata ristretta
        screen_grabber.screen_grab('prova')
        # 3 Andiamo a vedere se c'è la schermata  di errore
        if screen_grabber.is_messaggio_errore(punto_errore):
            #punto_corretto = correggi_punto(cord_domanda, punto_errore)
            clicka_risposta(*punto_corretto)
            time.sleep(3)
            continue

        el = Elaboratore(screen_grabber.screenshot_name)

        if not are_valid_coords_for_risposte(el.y):
            print('SIAMO AL PRIMO IF, OVVERO DOPO LA FUNZIONE CHE VALIDA LE COORDINATE')
            try:
                print(el.y)
            except:
                print("Non stampo el.y")
            print('Non trovo una casella di risposte!')
            time.sleep(2)
            os.remove(el.screenshot_name)
            continue

        if el.cords:
            el.salva_i_pezzi()
        else:
            print('SECONDO IF')
            try:
                print(el.cords)
            except:
                pass
            time.sleep(2)
            continue

        lista_tuple_coord_risposte = get_cords_risposte_da_cliccare(screen_grabber.cords[:2], el.cords[1:])

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
        print(scelta)
        #pp.rendo_template_html()
        try:
            scrivi_diario_csv(id.domanda, pp.dizionario_di_risposte_e_key_punteggi, scelta)
        except Exception as e:
            print(e)
        time.sleep(25)
        sposta_mouse_dalle_palle()

        #clicka_risposta(*lista_tuple_coord_risposte[0])
        #break