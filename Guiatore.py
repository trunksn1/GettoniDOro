import PySimpleGUI as sg
import time, queue, threading

class Guiatore():
    def __init__(self, lista_risposte):
        self.lista_risposte = lista_risposte

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

    def gui_punteggi(self, dati):# gui_queue):
        # TODO: il programma si blocca quando mostra la GUI, bisogna sfruttrare i thread
        sg.ChangeLookAndFeel('GreenTan')

        """
        layout = [
            # [sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD', size=(15, 1)), sg.Text('+Risp', size=(15, 1)), sg.Text('TOT', size=(15, 1))],
            [sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')],
            [sg.Text(self.lista_risposte[0], size=(15, 1)), sg.Text('', key='_d_R1_', justification='right', size=(3, 1)), sg.Text('', key='_dr_R1_', justification='right', size=(3, 1)), sg.Text('', key='_TOT_R1_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[1], size=(15, 1)), sg.Text('', key='_d_R2_', justification='right', size=(3, 1)), sg.Text('', key='_dr_R2_', justification='right', size=(3, 1)), sg.Text('', key='_TOT_R2_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[2], size=(15, 1)), sg.Text('', key='_d_R3_', justification='right', size=(3, 1)), sg.Text('', key='_dr_R3_', justification='right', size=(3, 1)), sg.Text('', key='_TOT_R3_', justification='right', size=(3, 1))],
            [sg.Exit()]
        ]
        """


        layout = [
            [sg.Text('RISPOSTE', size=(15, 1)), sg.Text('SoloD'), sg.Text('+Risp'), sg.Text('TOT')],
            [sg.Text(self.lista_risposte[0], size=(15, 1)), sg.Text(dati['_d_R1_'], key='_d_R1_', justification='right', size=(3, 1)), sg.Text(dati['_dr_R1_'], key='_dr_R1_', justification='right', size=(3, 1)), sg.Text(dati['_TOT_R1_'], key='_TOT_R1_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[1], size=(15, 1)), sg.Text(dati['_d_R2_'], key='_d_R2_', justification='right', size=(3, 1)), sg.Text(dati['_dr_R2_'], key='_dr_R2_', justification='right', size=(3, 1)), sg.Text(dati['_TOT_R2_'], key='_TOT_R2_', justification='right', size=(3, 1))],
            [sg.Text(self.lista_risposte[2], size=(15, 1)), sg.Text(dati['_d_R3_'], key='_d_R3_', justification='right', size=(3, 1)), sg.Text(dati['_dr_R3_'], key='_dr_R3_', justification='right', size=(3, 1)), sg.Text(dati['_TOT_R3_'], key='_TOT_R3_', justification='right', size=(3, 1))],
            [sg.Exit()]
        ]

        window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True, return_keyboard_events=True).Layout(layout)

        start = time.time()

        event, values = window.Read(timeout=8000) # dopo otto secondi la funzione termina da sola
        if event == 'Exit' or event is None or event == 'F9:120': #altrimenti termina se premo F9
            window.Close()
        dur = time.time() - start
        print(dur)
        window.Close()

        """
        while True:

            event, values = window.Read(timeout=10)  # wait for up to 100 ms for a GUI event
            dur = time.time() - start
            if event is None or event == 'F9:120' or event == 'Exit' or (dur > 10):
                print('Tempo scaduto: ', dur)
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
        """

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