import PySimpleGUI as sg
import time, queue, threading
import concurrent.futures
from selenium import webdriver
from cf import dimensioni_browser, WEBDRIVER_PATH, coordinate_drivers_browser

drivers = ''
driver1 = ''
driver2 = ''

class Guiatore():
    def __init__(self, lista_risposte, urls):
        self.lista_risposte = lista_risposte
        self.urls = urls

    def avvia_aggiornatori(self, punteggi):
        # -- Create a Queue to communicate with GUI --
        gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads
        # -- Start worker threads, one runs twice as often as the other
        threading.Thread(target=self.aggiornatore_gui, args=(gui_queue, punteggi[0], '_d_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_gui, args=(gui_queue, punteggi[1], '_dr_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_gui, args=(gui_queue, punteggi[2], '_TOT_RX_',), daemon=True).start()
        # -- Start the GUI passing in the Queue --
        dict_dati_per_gui = self.queue_to_dict(gui_queue)
        self.gui_punteggi(dict_dati_per_gui)

    def aggiornatore_gui(self, gui_queue, punteggio, key):
        for n, el in enumerate(self.lista_risposte):  # loop forever, keeping count in i as it loops
            if not punteggio[el]:
                punteggio[el] = 0
            key = key[:-2] + str( n +1) + key[-1:]
            gui_queue.put((key, punteggio[el]))

    def queue_to_dict(self, gui_queue):
        key_punteggio = {}
        while True:
            try:
                message = gui_queue.get_nowait()
            except queue.Empty:
                break
            if message:
                key_punteggio[message[0]] = message[1]
        print('lista creata dalla Queu: \n')
        print(key_punteggio)
        return key_punteggio

    def gui_punteggi(self, dati):
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

        window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True, return_keyboard_events=True).Layout(layout)

        start = time.time()
        browser_mostrato = False
        while True:
            dur = time.time() - start
            if not browser_mostrato:
# Read lancia un event loop, attraverso il parametro timeout viene restituito il param timeout_key  ogni x millisecondi
                event, _ = window.Read(timeout=1000, timeout_key=self.esecutori_browser(coordinate_drivers_browser, self.urls[0], self.urls[1]))
                browser_mostrato = True

            if event == 'F9:120' or event == 'Exit' or (dur >= 4):
                print('Tempo scaduto: ', dur)
                break

        window.Close()



    def esecutori_browser(self, coordinate_dr, domanda_url, risp_url):
        """ Funziona ma ho bisogno di sapere
        print('allinterno dell esecutori')
        print(domanda_url, risp_url)
        global driver1, driver2

        if not driver1 or not driver2:
            driver1 = self.set_driver(coordinate_dr[0])
            driver2 = self.set_driver(coordinate_dr[1])
        """

        global drivers
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            if not drivers:
                drivers = list(executor.map(self.set_driver, coordinate_dr))

        # Tutto questo è per evitare il RunTimeError che lancia Tkinter quando durante l'esecuzione della gui
        # esci dal thread principale.
        # In pratica sfrutto gli oggetti Queue, per conservarci dentro la funzione che apre il browser
        q = queue.Queue()

        # adesso sto conservando nella queue, la funzione lambda che è pari a quella definita dopo di open_website()
        q.put(lambda: self.open_website([domanda_url, drivers[0]])) #driver1]))
        q.put(lambda: self.open_website([risp_url, drivers[1]])) #driver2]))

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

    def esecutori_browser_old(self, coordinate_dr, domanda_url, risp_url):
        global drivers
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            if not drivers:
                drivers = list(executor.map(self.set_driver, coordinate_dr))
            self.start = time.time()
            executor.map(self.open_website, [(domanda_url, drivers[0]), (risp_url, drivers[1])]) # modo per usare la funzione map con due iterabili diversi

            # Esperimento, risultato identico. Lascio per futura memoria
            #threading.Thread(target=self.open_website, args=([(domanda_url, drivers[0])]), daemon=True).start()
            #threading.Thread(target=self.open_website, args=([(risp_url, drivers[1])]), daemon=True).start()
            dur = time.time() - self.start
            print('Tempo per aprire il browser: ', dur)

    def set_driver(self, coordinate_browser):
        driver = webdriver.Chrome(WEBDRIVER_PATH)
        driver.set_window_size(*dimensioni_browser)
        driver.set_window_position(*coordinate_browser)
        return driver

    def open_website(self, sito_e_driver):
        print('sito e driver')
        print(sito_e_driver[1], sito_e_driver[0])
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