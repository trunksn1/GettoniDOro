class Quiz():
    def __init__(self, dom='', risp='', url_dom='', url_risp='', coord_risp='', punteggi='', risultati_google=''):
        self.str_domanda = dom
        self.lst_risp = risp
        self.url_dom = url_dom
        self.url_risp = url_risp
        self.lst_coordinate_risp = coord_risp
        self.dict_punteggi = punteggi
        self.risultati_google = risultati_google