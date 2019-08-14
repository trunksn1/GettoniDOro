from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import requests
from cf import USER_AGENT
from multiprocessing.dummy import Pool as ThreadPool
import PySimpleGUI as sg
import time, queue, threading

class Mostratore():
    def __init__(self, urls, lista_risposte):
        self.start = time.time()
        self.lista_url = urls
        #self.gui_punteggi()
        self.lista_risposte = lista_risposte
        self.avvia_ricerca()

    def avvia_ricerca(self):

        pool = ThreadPool(4)
        self.punteggi = pool.map(self.cerca_risposte, self.lista_url)
        pool.close()
        pool.join()
        self.punteggio_totale = Counter(self.punteggi[0]) + Counter(self.punteggi[1])  # 0 è solo dom, 1 è dom + risp
        print('Punteggio totale:\n')
        print(self.punteggio_totale)
        self.avvia_aggiornatori()

    def cerca_risposte(self, url):
        # l'obiettivo è quello di analizzare nei due URL che apro, quante volte compaiono ciascuna delle risposte!!!
        # E' necessario quindi analizzare con BS4 i due url, contare quante volte compaiono le singole risposte
        # TODO: Le singole rispsote andrebbero analizzate in modo da rimuovere parole inutili e cercare solo il succo.
        # e inviare questi dati a pysimplegui per mostrarli
        r = requests.get(url, headers=USER_AGENT)
        r.raise_for_status()
        print(r)
        html_doc = r.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        risultati_google = soup.select('.rc')

        punteggio = defaultdict(int)

        for risultato in risultati_google:
            print(str(risultato))
            for risposta in self.lista_risposte:
                if risposta.lower() in str(risultato).lower():
                    print('Trovato {}'.format(risposta.lower()))

                    punteggio[risposta] += 1
        print('singolo puneggio: \n')
        print(punteggio)
        return punteggio

    def avvia_aggiornatori(self):
        # -- Create a Queue to communicate with GUI --
        gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads
        # -- Start worker threads, one runs twice as often as the other
        threading.Thread(target=self.aggiornatore_GUI, args=(gui_queue, self.punteggi[0], '_d_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_GUI, args=(gui_queue, self.punteggi[1], '_dr_RX_',), daemon=True).start()
        threading.Thread(target=self.aggiornatore_GUI, args=(gui_queue, self.punteggio_totale, '_TOT_RX_',), daemon=True).start()
        # -- Start the GUI passing in the Queue --
        self.gui_punteggi(gui_queue)

    def aggiornatore_GUI(self, gui_queue, punteggio, key):
        for n, el in enumerate(self.lista_risposte):  # loop forever, keeping count in i as it loops
            if not punteggio[el]:
                punteggio[el] = 0
            key = key[:-2] + str(n+1) + key[-1:]
            gui_queue.put((key, punteggio[el]))

    def gui_punteggi(self, gui_queue):
        # TODO: il programma si blocca quando mostra la GUI, bisogna sfruttrare i thread
        print('mostra pnteggi')
        sg.ChangeLookAndFeel('GreenTan')

        layout = [
            #[sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD', size=(15, 1)), sg.Text('+Risp', size=(15, 1)), sg.Text('TOT', size=(15, 1))],
            [sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')],
            [sg.Text(self.lista_risposte[0], size=(15, 1)), sg.Text('', key='_d_R1_', justification='right', size=(3, 1)), sg.Text('', key='_dr_R1_', justification='right', size=(3, 1)), sg.Text('', key='_TOT_R1_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[1], size=(15, 1)), sg.Text('', key='_d_R2_', justification='right', size=(3, 1)), sg.Text('', key='_dr_R2_', justification='right', size=(3, 1)), sg.Text('', key='_TOT_R2_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[2], size=(15, 1)), sg.Text('', key='_d_R3_', justification='right', size=(3, 1)), sg.Text('', key='_dr_R3_', justification='right', size=(3, 1)), sg.Text('', key='_TOT_R3_', justification='right', size=(3, 1))],
            [sg.Exit()]
        ]

        window = sg.Window('Risposte', layout, default_element_size=(40, 1), grab_anywhere=False, return_keyboard_events=True)
        """
        while True:
            event, value = window.Read(timeout=100) # Aspetta 100 ms per un evento GUI

            if event == "OK" or event == 'F9:120':  # evento pari alla pressione del pulsante F9
                print(event, "exiting")
                window.Close()
                break

            text_elem.Update(event)"""
        """
        #Tagliamo la testa al toro e chiudiamo la finestra dopo 10 secondi e basta.
        event, value = window.Read(timeout=100)  # Aspetta 100 ms per un evento GUI
        time.sleep(10)
        window.Close()"""

        while True:
            event, values = window.Read(timeout=10)  # wait for up to 100 ms for a GUI event
            if event is None or event == 'F9:120' or event == 'Exit':


                print(event, 'uscendo')
                break
            # --------------- Loop through all messages coming in from threads ---------------
            while True:  # loop executes until runs out of messages in Queue
                try:  # see if something has been posted to Queue
                    message = gui_queue.get_nowait()
                except queue.Empty:  # get_nowait() will get exception when Queue is empty
                    break  # break from the loop if no more messages are queued up
                # if message received from queue, display the message in the Window
                if message:
                    window.Element(message[0]).Update(message[1])
                    window.Refresh()  # do a refresh because could be showing multiple messages before next Read

        # if user exits the window, then close the window and exit the GUI func
        window.Close()

if __name__ == '__main__':
    lista_urls = ['https://www.google.com/search?q=de+bello+gallico+roma', 'https://www.google.com/search?q=modi+di+dire',]
    lista_risp = ['Caio', 'Cesare', 'Sempronio']
    x = Mostratore(lista_urls, lista_risp)