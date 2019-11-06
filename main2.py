import install_settings
from ScreenGrabber import ScreenGrab
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
#from Guiatore import Guiatore
import time




#TODO: controllare se nel file install_settings c'è il percorso di PyTesseract, se non c'è ottienilo (via GUI)
screen_grabber = ScreenGrab()
cords = ()
while True:

    print('INIZIO GRAB')
    screen_grabber.start_screen_grab()
    # Calcolo solo se ho delle coordinate nuove!
    if screen_grabber.key_pressed == 'F6':
        cords = screen_grabber.calcolo_spazi_domande_e_risposte()
    # Se riutilizzo le vecchie coordinate non ho bisogno di ricalcolare nulla
    elif screen_grabber.key_pressed == 'F9':
        pass
    screen_grabber.screen_grab()
    print('FINE GRAB\n')
    el = Elaboratore(screen_grabber.screenshot_name)
    el.salva_i_pezzi()
    id = Identificatore(el.pezzi)
    #id.prepara_url_da_ricercare(id.domanda, id.risposte)
    pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda)

    print(pp.dizionario_di_risposte_e_key_punteggi)
    pp.rendo_template_html()

