import time
import win32gui


class Sarto():
    def __init__(self):
        self.inizializzato = True

    def get_program_cords(self, programma):
        if not programma:
            # win32gui.EnumWindows(callback, None)
            # win2find = "BlueStacks"
            # win2find = "Cazzstacks.mkv - Lettore multimediale VLC"
            win2find = "VLC (Direct3D output)"
            # win2find = "Stacks.png - IrfanView"
        win2find = programma
        whnd = win32gui.FindWindowEx(None, None, None, win2find)
        if not (whnd == 0):
            print('FOUND!')
            self.rect = win32gui.GetWindowRect(whnd)
            x = self.rect[0]
            y = self.rect[1]
            w = self.rect[2] - x
            h = self.rect[3] - y
            # rect = (rect[0], rect[1] + y_inizio_domanda, rect[2], rect[3])
            print("\tLocation: (%d, %d)" % (x, y))
            print("\t    Size: (%d, %d)" % (w, h))

            return self.rect
        else:
            print('PROGRAM NOT FOUND!')
            #time.sleep(60)
            return

    def get_cords_domande_e_risposte(self):
        # Calcola dove si trovano i rettangoli della domanda e delle risposte
        # self.cords all'inizio è una lista il cui unico elemento è una tupla con le coordinate del punto cliccato
        largh = self.rect[2] - self.rect[0]
        altezz = self.rect[3] - self.rect[1]
        self.dimensioni_originali = largh, altezz

        y_in = self.rect[1] + int(altezz * 0.265)
        y_fin = self.rect[1] + int(altezz * 0.914)
        self.cords = self.rect[0], y_in, self.rect[2], y_fin
        return self.cords

    def get_punto_msg_errore(self):
        """Questa funzione utilizza un'immagine tagliata del programma bluestacks"""
        altezza = self.cords[3] - self.cords[1]
        larghezza = self.cords[2] - self.cords[0]

        y_in = (0.637 * altezza)
        y_fin = (0.73 * altezza)

        x_sin = (0.139 * larghezza)
        x_des = (0.86 * larghezza)
        self.punto = int(((x_sin + x_des) / 2)), int(((y_in + y_fin) / 2))
        return self.punto

    def correggi_punto(self, cordinate_programma, punto_da_correggere):
        x = punto_da_correggere[0] + cordinate_programma[0]
        y = punto_da_correggere[1] + cordinate_programma[1]
        return x, y