import queue, threading
from selenium import webdriver
from cf import WEBDRIVER_PATH, dimensioni_browser, coordinate_drivers_browser

def set_driver_new(coordinate_browser, queue):
    driver = webdriver.Chrome(WEBDRIVER_PATH)
    driver.set_window_size(*dimensioni_browser)
    driver.set_window_position(*coordinate_browser)
    queue.put(driver)

def queue_driver_to_list( driv_queue):
        drivers = []
        while True:
            try:
                driv = driv_queue.get()
                print(driv)
            except queue.Empty:
                continue
            if driv:
                drivers.append(driv)
            if len(drivers) == 2:
                break
        return drivers

def ottieni_drivers():
    print('sono nella funzione degli helpers: ottieni drivers')
    drivers_queue = queue.Queue()
    threading.Thread(target=set_driver_new, args=(coordinate_drivers_browser[0], drivers_queue,), daemon=False).start()
    threading.Thread(target=set_driver_new, args=(coordinate_drivers_browser[1], drivers_queue,), daemon=False).start()
    drivers = queue_driver_to_list(drivers_queue)
    print(drivers)
    return drivers

