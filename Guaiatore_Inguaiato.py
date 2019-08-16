import PySimpleGUI as sg
import time, queue, threading
import concurrent.futures
from selenium import webdriver
from cf import dimensioni_browser, WEBDRIVER_PATH, coordinate_drivers_browser

driver1 = ''
driver2 = ''

class Guiatore():
    def __init__(self, lista_risposte, urls):
        self.lista_risposte = lista_risposte
        self.urls = urls

    def avvia_aggiornatori(self, punteggi):
        print('avvio aggiornatori')
        # -- Create a Queue to communicate with GUI --
        gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads
        # -- Start worker threads, one runs twice as often as the other

        # TODO: POSSIBILE CAUSE DEL RUNTIMEERROR?????
        threading.Thread(target=self.aggiornatore_gui, args=(gui_queue, punteggi[0], '_d_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_gui, args=(gui_queue, punteggi[1], '_dr_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_gui, args=(gui_queue, punteggi[2], '_TOT_RX_',), daemon=True).start()

        # -- Start the GUI passing in the Queue --
        dict_dati_per_gui = self.queue_to_dict(gui_queue)
        print('prima di lanciare l\'aggiornatore della gui')
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

    def gui_punteggi(self, dati):# gui_queue):
        sg.ChangeLookAndFeel('GreenTan')

        layout = [
            [sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')],
            [sg.Text(self.lista_risposte[0], size=(15, 1)), sg.Text(dati['_d_R1_'], key='_d_R1_', justification='right', size=(3, 1)), sg.Text(dati['_dr_R1_'], key='_dr_R1_', justification='right', size=(3, 1)), sg.Text(dati['_TOT_R1_'], key='_TOT_R1_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[1], size=(15, 1)), sg.Text(dati['_d_R2_'], key='_d_R2_', justification='right', size=(3, 1)), sg.Text(dati['_dr_R2_'], key='_dr_R2_', justification='right', size=(3, 1)), sg.Text(dati['_TOT_R2_'], key='_TOT_R2_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[2], size=(15, 1)), sg.Text(dati['_d_R3_'], key='_d_R3_', justification='right', size=(3, 1)), sg.Text(dati['_dr_R3_'], key='_dr_R3_', justification='right', size=(3, 1)), sg.Text(dati['_TOT_R3_'], key='_TOT_R3_', justification='right', size=(3, 1))],
            [sg.Exit()]
        ]

        window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True, return_keyboard_events=True).Layout(layout)

        start = time.time()
        browser_mostrato = False
        while True:
            try:
                if not browser_mostrato:
                    event, values = window.Read(timeout=100, timeout_key=self.esecutori_browser(coordinate_drivers_browser, self.urls[0], self.urls[1]))#timeout=100)  # wait for up to 100 ms for a GUI event
                    browser_mostrato = True
            except:
                print('ERRORE, TI PREGO SALTATI')
            dur = time.time() - start
            #print(dur)
            if event == 'F9:120' or event == 'Exit' or (dur >= 5):
                print('Tempo scaduto: ', dur)
                break
                #if not browser_mostrato:
                    # TODO: POSSIBILE CAUSE DEL RUNTIMEERROR?????
                    #try:
                    #self.esecutori_browser(coordinate_drivers_browser, self.urls[0], self.urls[1])
                #except Exception as e:
                    #print('******ERRORE******', e.args)
                    #print(e)

                browser_mostrato = True
                print("Browser caricato in: ", dur)
        window.Close()



    def esecutori_browser(self, coordinate_dr, domanda_url, risp_url):
        global driver1, driver2
        # -- Create a Queue to communicate with GUI --
        #drivers_queue = queue.Queue()
        #print("coordinate del driver: ", coordinate_dr)
        # -- Start worker threads, one runs twice as often as the other
        #x = threading.Thread(target=self.set_driver, args=(coordinate_dr[0], drivers_queue,), daemon=False).start()
        #y = threading.Thread(target=self.set_driver, args=(coordinate_dr[1], drivers_queue,), daemon=False).start()

        # -- Start the GUI passing in the Queue --
        #lista_driver_per_gui = self.driver_queue_to_list(drivers_queue)
        #print("Ecco la lista dei driver ottenuti col nuovo metodo: ")
        #print(lista_driver_per_gui)

        #with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #    executor.map(self.open_website, [(domanda_url, lista_driver_per_gui[0]), (risp_url, lista_driver_per_gui[1])])  # modo per usare la funzione map con due iterabili diversi
        if not driver1 or not driver2:
            driver1 = self.set_driver_old(coordinate_dr[0])
            driver2 = self.set_driver_old(coordinate_dr[1])
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(self.open_website, [(domanda_url, driver1), (risp_url, driver2)]) # modo per usare la funzione map con due iterabili diversi
            executor.shutdown()

        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            if drivers_queue.Empty:
                drivers_queue.put(list(executor.map(self.set_driver, coordinate_dr))) # TODO QUI. FACCUI ANCHE APRIRE IL BROWSER E VEDIAMO CHE SUCCEDE
            #self.start = time.time()
            # TODO: POSSIBILE CAUSE DEL RUNTIMEERROR?????
            #executor.map(self.open_website, [(domanda_url, drivers[0]), (risp_url, drivers[1])]) # modo per usare la funzione map con due iterabili diversi

            # Esperimento, risultato identico. Lascio per futura memoria
            # TODO: POSSIBILE CAUSE DEL RUNTIMEERROR????? PENSO CHE SIA QUI!!!!!
            y = threading.Thread(target=self.open_website, args=([(domanda_url, drivers[0])]), daemon=True).start()
            x = threading.Thread(target=self.open_website, args=([(risp_url, drivers[1])]), daemon=True).start()
           #dur = time.time() - self.start
            #print('Tempo per aprire il browser: ', dur)
        """

    def set_driver(self, coordinate_browser, driver_queue):
        print("Sono in set driver")
        print(coordinate_browser)
        while True:
            driver = webdriver.Chrome(WEBDRIVER_PATH)
            driver.set_window_size(*dimensioni_browser)
            driver.set_window_position(*coordinate_browser)
            break
        print(driver)
        driver_queue.put(driver)
        print(driver_queue)

    def driver_queue_to_list(self, driver_queue):
        drivers = []
        while True:
            try:
                driver = driver_queue.get_nowait()
                drivers.append(driver)
            except queue.Empty: # driver_queue.Empty:
                print('Queue è Empty')
                break
        print('lista di driver creata dalla Queu: \n')
        print(drivers)
        return drivers


    def set_driver_old(self, coordinate_browser):
        driver = webdriver.Chrome(WEBDRIVER_PATH)
        driver.set_window_size(*dimensioni_browser)
        driver.set_window_position(*coordinate_browser)
        return driver

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