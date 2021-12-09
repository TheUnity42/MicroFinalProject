import threading
import time
import logging
import numpy as np
import matplotlib.pyplot as plt

class AtomicArray:
    def __init__(self, size):
        self.size = size
        self.array = np.zeros(size)
        self._lock = threading.Lock()
    def set(self, value):
        with self._lock:
            self.array = value
    def get(self):
        with self._lock:
            return self.array

def thread_function(name, raise_except, var: AtomicArray, count=5):
    for i in range(count):
        logging.info("Thread {}: {}".format(name, i))
        var.set(np.sin(np.arange(var.get().shape[0]) * i))
        if raise_except():
            raise Exception("InteruptException in thread {}".format(name))
        time.sleep(0.25)



if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO)

    var = AtomicArray(100)

    fig, ax = plt.subplots()
    plot_points = ax.plot(np.arange(var.get().shape[0]), var.get(), 'b-')[0]
    ax.set_xlim(0, var.get().shape[0])
    ax.set_ylim(-1, 1)

    plt.ion()
    plt.show()
    plt.pause(0.001)

    stop_threads = False
    def handle_close_event(event):
        global stop_threads
        stop_threads = True

    fig.canvas.mpl_connect('close_event', handle_close_event)

    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,lambda: stop_threads, var,25), daemon=True)
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")

    sample_rate = 0.1
    try:
        while x.is_alive():            
                plot_points.set_data(np.arange(var.get().shape[0]), var.get())
                plt.draw()
                plt.pause(0.001)
                time.sleep(sample_rate)
    except KeyboardInterrupt:
        logging.info("Main    : received keyboard interrupt")
        stop_threads = True
        x.join()
        

    x.join()
    logging.info("Main    : all done")
