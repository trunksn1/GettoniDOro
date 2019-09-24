from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore

class Quiz():
    #def __init__(self, dom='', risp='', url_dom='', url_risp='', coord_risp='', punteggi='', risultati_google='', cords=''):
    def __init__(self, screenshot_name):# elaboratore, identificatore, punteggiatore):
        """
        self.str_domanda = dom
        self.lst_3risposte = risp
        #self.dict_risposte = {r1: {p_dom: 0, p_domR: 0, coord_bluestacks: (0,0)}}
        self.url_dom = url_dom
        self.url_risp = url_risp
        self.lst_coordinate_risp = coord_risp
        self.dict_punteggi = punteggi
        self.risultati_google = risultati_google
        self.coordinate_bluestacks = cords
        """

        self.str_nome_screenshot = screenshot_name
        #el = Elaboratore(screenshot_name)
        #el.salva_i_pezzi()
        #id = Identificatore(el.pezzi)
        #self.str_domanda = id.domanda
        #self.dict_risposte = {i:0 for i in id.risposte}