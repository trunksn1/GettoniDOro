from keyboard_moves import start_screen_grab
from helpers import screen_grab, ocr_core, ricerca

"""Per avviare la cattura dello schermo premi F4 e trascini il mouse fino a comprendere domanda e risposte;
Premendo F6 selezionerai solo l'inizio del riquadro, il programma dividerà domande e risposte. Da testare.
Per ripetere la cattura dello schermo con l'ultimo metodo selezionato premi F9"""

def main():
    while True:
        coordinate_domande_e_risposte = start_screen_grab()
        if type(coordinate_domande_e_risposte) == list: #lista che contiene 2 blocchi: uno per la domanda e uno epr la risposta
            immagine_domanda, immagine_risposta = screen_grab(coordinate_domande_e_risposte)
            testo_domanda = ocr_core(immagine_domanda)
            testo_risposta = ocr_core(immagine_risposta)
            testo_risposta = testo_risposta.split("\n")
            #ricerca(testo_domanda, testo_risposta)
        else:
            immagine = screen_grab(coordinate_domande_e_risposte)
            testo = ocr_core(immagine)
            #ricerca(testo)


if __name__ == '__main__':
    main()
