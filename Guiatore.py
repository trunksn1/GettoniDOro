# -- coding: utf-8 --
import PySimpleGUI as sg
import time, queue, threading
from selenium import webdriver
from cf import dimensioni_browser, WEBDRIVER_PATH, coordinate_drivers_browser

drivers = ''
driver1 = ''
driver2 = ''

class Guiatore():
    def __init__(self, lista_risposte, urls, drivers, risultati_google_per_gui):
        self.lista_risposte = lista_risposte
        self.urls = urls
        self.drivers = drivers
        self.risultati = risultati_google_per_gui

    def crea_layout_per_gui(self, dati):
        assert threading.current_thread() is threading.main_thread()
        print('Thread attivi: ', end='')
        print(threading.active_count())
        print(threading.enumerate())

        layout = [[sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')]]

        for n, risp in enumerate(self.lista_risposte):
            layout.append(
                [sg.Text(risp, size=(15, 1)),
                 sg.Text(dati[risp]['_d_R{}_'.format(n+1)], key='_d_R{}_'.format(n+1), justification='right', size=(3, 1)),
                 sg.Text(dati[risp]['_dr_R{}_'.format(n+1)], key='_dr_R{}_'.format(n+1), justification='right', size=(3, 1)),
                 sg.Text(dati[risp]['_d_R{}_'.format(n+1)] + dati[risp]['_dr_R{}_'.format(n+1)], key='_TOT_R{}_'.format(n+1), justification='right', size=(3, 1))]
            )

        window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True,
                           return_keyboard_events=True, keep_on_top=True).Layout(layout)

        start = time.time()
        browser_mostrato = False
        while True:
            dur = time.time() - start

            # Read lancia un event loop, attraverso il parametro timeout ogni X millisecondi
            # viene restituito il contenuto del parametro timeout_key
            event, _ = window.Read(timeout=1000)
            if event == 'F9:120' or event == 'Exit' or (dur >= 5):
                print('Tempo scaduto: ', dur)
                break
        window.Close()

if __name__ == '__main__':
    from collections import defaultdict, Counter
    risposte = ['tizio', 'cazio', 'sempronio']
    urls = ['https://www.google.com/search?q=come+si+chiamava+Cesare', 'https://www.google.com/search?q=come+si+chiamava+Cesare%3F+AND+%28"tizio"+OR+"caio"+OR+"sempronio"%29']
    for i in range (40):
        x = Guiatore(risposte, urls)
        punteggi = [defaultdict(int), defaultdict(int), defaultdict(int)]
        x.avvia_aggiornatori(punteggi)

        print('*** FINE DEL TENTATIVO NUMERO {} ********'.format(i+1))