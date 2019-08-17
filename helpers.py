import json, os
from selenium import webdriver
import jsonpickle
from cf import STATE_JSON, WEBDRIVER_PATH, coordinate_browser, dimensioni_browser, USER_AGENT

def save(coordinate_screengrab=(), lista_drivers=[]):
    # Il momento peggiore è quando il programma si fotte, perchè per incominciare ha bisogno di molto tempo
    # con questa funzione cerco di salvare alcuni parametri da poter riciclare subito all'avvio del programma
    # i parametri che voglio salvare sono:
    # le coordinate da cui stavo salvando gli screenshot
    # i driver, si spera ancora attivi per l'apertura del browser
    # I parametri vengono salvati in un file json da ricaricare all'inizio, con un check per vedere se è tutto corretto
    nuova_lista_driver_encoded = []
    print(lista_drivers)
    for n, el in enumerate(lista_drivers):
        print("PRE", el)
        lista_drivers[n] = jsonpickle.encode(el)
        print("POST", el)
    print(lista_drivers)


    data = {
        'coordinate_screengrab': coordinate_screengrab,
        'lista_drivers': lista_drivers,
        }
    with open(STATE_JSON, 'w') as f:
        json.dump(data, f)

def load():
    if os.path.exists(STATE_JSON):
        with open(STATE_JSON, 'r') as f:
            data = json.load(f)
            print('dati')
            print(data)
            for n, el in enumerate(data['lista_drivers']):
                #print(data['lista_drivers'][n])
                #print(el)
                data['lista_drivers'][n] = jsonpickle.decode(el)
                #print(el)
            print(data)
        """
        data = {
            'coordinate_screengrab': (xx, xx)
            'lista_drivers': [...]
        }
        """

    return data


if __name__ == '__main__':
    if not os.path.isfile(STATE_JSON):

        driver1 = webdriver.Chrome(WEBDRIVER_PATH)
        driver1.set_window_size(*dimensioni_browser)
        driver1.set_window_position(*coordinate_browser)
        print('driver1: \n')
        print('cotniua: ', type(driver1))   # <class 'selenium.webdriver.chrome.webdriver.WebDriver'>
        driver2 = webdriver.Chrome(WEBDRIVER_PATH)
        driver2.set_window_size(*dimensioni_browser)
        driver2.set_window_position(*coordinate_browser)
        drivers = [driver1, driver2]
        coordinate = (600,0)
        save(coordinate, drivers)
    else:
        try:
            data = load()
        except Exception as e:
            print(e)
            os.remove(STATE_JSON)
            exit()
        driver3 = data['lista_drivers'][0]
        print(type(driver3))    # <class 'selenium.webdriver.chrome.webdriver.WebDriver'>
        driver3.get('www.bing.com') #, headers=USER_AGENT)
        cord = data['coordinate_screegrab']
        print(cord)
