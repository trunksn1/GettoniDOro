import os

SCREEN_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screenshot')
TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test')
RELABOR_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rielaborazioni')
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
CSS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'main.css')



USER_AGENT = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

# Moltiplicatore per Resize dell'immagine
mult = 5

### Valido per Screenshot presi attraverso SideSync (Samsung Galaxy S6+)
### Dimensione dello screen grab
#x_finale = 500
#y_finale = 500
#taglio_x_sinistra = 120
#taglio_x_destra = 130
#taglio_y_rielab = 100

# Valido per Screeshot presi attraverso BlueStacks (sul pc di Milano) con risoluzione impostata a 960x540
# lanciando solitario.py le dimensioni della schermata che al 28/09/2019 funziona p di (499, 925)
x_finale = 500
y_finale = 550
taglio_x_sinistra = 180
taglio_x_destra = 170
taglio_y_rielab = 100
# La coordinata della y a cui parte la domanda è circa 250 pixel in basso rispetto la finestra del quiz
y_inizio_domanda = 250


#Dimensione dello screen grab x Domande
y_finale_domande = 140
#Dimensione dello screen grab x Risposte
y_iniziale_risposte = 165
y_finale_risposte = 320

#Dimensioni e posizione della finestra del browser che si apre
coordinate_browser = (1125, 0) #si apre in mezzo per lasciare al centro il quiz, il valore sul pc Milanese è 800,0

dimensioni_browser = (795, 1080) # prima era (850, 1080)

coordinate_drivers_browser = [(550, 0), (-120, 0)]

