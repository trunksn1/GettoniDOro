class Quiz():
    def __init__(self, dom='', risp='', url_dom='', url_risp='', coord_risp='', punteggi='', risultati_google='', cords=''):
        self.str_domanda = dom
        self.lst_3risposte = risp
        #self.dict_risposte = {r1: {p_dom: 0, p_domR: 0, coord_bluestacks: (0,0)}}
        self.url_dom = url_dom
        self.url_risp = url_risp
        self.lst_coordinate_risp = coord_risp
        self.dict_punteggi = punteggi
        self.risultati_google = risultati_google
        self.coordinate_bluestacks = cords