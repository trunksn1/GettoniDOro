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

    def avvia_aggiornatori(self, punteggi):
        # -- Create a Queue to communicate with GUI --
        gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads
        # -- Start worker threads, one runs twice as often as the other
        threading.Thread(target=self.aggiornatore_guiqueue__key_punteggio, args=(gui_queue, punteggi[0], '_d_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_guiqueue__key_punteggio, args=(gui_queue, punteggi[1], '_dr_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_guiqueue__key_punteggio, args=(gui_queue, punteggi[2], '_TOT_RX_',), daemon=True).start()
        # -- Start the GUI passing in the Queue --
        dict_dati_per_gui = self.queue_to_dict(gui_queue)
        self.creatore_gui(dict_dati_per_gui)

    def aggiornatore_guiqueue__key_punteggio(self, gui_queue, punteggio, key):
        for n, el in enumerate(self.lista_risposte):  # loop forever, keeping count in i as it loops
            if not punteggio[el]:
                punteggio[el] = 0
            key = key[:-2] + str( n +1) + key[-1:]
            gui_queue.put((key, punteggio[el]))

    def queue_to_dict(self, gui_queue):
        # Il dizionario {key_della_gui: punteggio_della_risposta_corrispondente}
        key_punteggio = {}
        while True:
            try:
                message = gui_queue.get_nowait()
            except queue.Empty:
                break
            if message:
                key_punteggio[message[0]] = message[1]
        return key_punteggio

    def crea_layout_per_gui(self, dati):
        layout = [[sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')]]

        for n, risp in enumerate(self.lista_risposte):
            layout.append(
                [sg.Text(risp, size=(15, 1)),
                 sg.Text(dati[0][risp]['_d_R{}_'.format(n+1)], key='_d_R_', justification='right', size=(3, 1)),
                 sg.Text(dati[1][risp]['_dr_R{}_'.format(n+1)], key='_dr_R_', justification='right', size=(3, 1)),
                 sg.Text(dati[0][risp]['_d_R{}_'.format(n+1)] + dati[1][risp]['_dr_R{}_'.format(n+1)], key='_TOT_R_', justification='right', size=(3, 1))]
            )

        window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True,
                           return_keyboard_events=True, keep_on_top=True).Layout(layout)

        start = time.time()
        browser_mostrato = False
        while True:
            dur = time.time() - start

            # Read lancia un event loop, attraverso il parametro timeout ogni X millisecondi
            # viene restituito il contenuto del parametro timeout_key
            event, _ = window.Read(
                timeout=1000)  # , timeout_key=self.esecutori_browser(self.drivers, self.urls[0], self.urls[1])) #timeout_key=self.ottieni_drivers(coordinate_drivers_browser)) #timeout_key=self.esecutori_browser(coordinate_drivers_browser, self.urls[0], self.urls[1]))

            if event == 'F9:120' or event == 'Exit' or (dur >= 10):
                print('Tempo scaduto: ', dur)
                break

        window.Close()

    def creatore_gui(self, dati):
        # TODO: il programma si blocca quando mostra la GUI, bisogna sfruttrare i thread
        sg.ChangeLookAndFeel('GreenTan')

        layout = [
            [sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')],
            [sg.Text(self.lista_risposte[0], size=(15, 1)),
             sg.Text(dati['_d_R1_'], key='_d_R1_', justification='right', size=(3, 1)),
             sg.Text(dati['_dr_R1_'], key='_dr_R1_', justification='right', size=(3, 1)),
             sg.Text(dati['_TOT_R1_'], key='_TOT_R1_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[1], size=(15, 1)),
             sg.Text(dati['_d_R2_'], key='_d_R2_', justification='right', size=(3, 1)),
             sg.Text(dati['_dr_R2_'], key='_dr_R2_', justification='right', size=(3, 1)),
             sg.Text(dati['_TOT_R2_'], key='_TOT_R2_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[2], size=(15, 1)),
             sg.Text(dati['_d_R3_'], key='_d_R3_', justification='right', size=(3, 1)),
             sg.Text(dati['_dr_R3_'], key='_dr_R3_', justification='right', size=(3, 1)),
             sg.Text(dati['_TOT_R3_'], key='_TOT_R3_', justification='right', size=(3, 1))],
            [sg.Exit()]
        ]

        window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True, return_keyboard_events=True, keep_on_top=True).Layout(layout)

        start = time.time()
        browser_mostrato = False
        while True:
            dur = time.time() - start

            # Read lancia un event loop, attraverso il parametro timeout ogni X millisecondi
            # viene restituito il contenuto del parametro timeout_key
            event, _ = window.Read(timeout=1000) #, timeout_key=self.esecutori_browser(self.drivers, self.urls[0], self.urls[1])) #timeout_key=self.ottieni_drivers(coordinate_drivers_browser)) #timeout_key=self.esecutori_browser(coordinate_drivers_browser, self.urls[0], self.urls[1]))

            if not browser_mostrato:
                self.esecutori_browser(self.drivers, self.urls[0], self.urls[1])
                browser_mostrato = True
            print(dur)


            if event == 'F9:120' or event == 'Exit' or (dur >= 10):
                print('Tempo scaduto: ', dur)
                break

        window.Close()

    def esecutori_browser(self, coordinate_dr, domanda_url, risp_url):
        # Tutto questo è per evitare il RunTimeError che lancia Tkinter quando durante l'esecuzione della gui
        # esci dal thread principale.
        # In pratica sfrutto gli oggetti Queue, per conservarci dentro la funzione che apre il browser
        # TODO Col cazzo! L'errore continua a presentarsi, tutta fatica per niente!
        q = queue.Queue()

        # adesso sto conservando nella queue la funzione lambda, questa è in pratica la funzione open_website()
        q.put(lambda: self.open_website([domanda_url, coordinate_dr[0]])) #driver1]))
        q.put(lambda: self.open_website([risp_url, coordinate_dr[1]])) #driver2]))

        # Questo loop serve a controllare se c'è qualcosa nella queue
        while True:
            # se la queue ha qualcosa (in questo caso una funzione da lancaire) conservala in una variabile
            try:
                # metto il contenuto della queue (la funzione openwebsite) nella variabile f
                f = q.get_nowait()  # prendo il contenuto della queue e poi la svuoto
                # la funzione conservata viene lanciata adesso
                f()
            except queue.Empty:
                # se la queue è vuota (perchè l'abbiamo svuotata grazue al metodo .get_nowait()
                break

    def open_website(self, sito_e_driver):
        sito_e_driver[1].get(sito_e_driver[0])

if __name__ == '__main__':
    from collections import defaultdict, Counter
    risposte = ['tizio', 'cazio', 'sempronio']
    urls = ['https://www.google.com/search?q=come+si+chiamava+Cesare', 'https://www.google.com/search?q=come+si+chiamava+Cesare%3F+AND+%28"tizio"+OR+"caio"+OR+"sempronio"%29']
    for i in range (40):
        x = Guiatore(risposte, urls)
        punteggi = [defaultdict(int), defaultdict(int), defaultdict(int)]
        x.avvia_aggiornatori(punteggi)

        print('*** FINE DEL TENTATIVO NUMERO {} ********'.format(i+1))