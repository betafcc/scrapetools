from time import sleep
from multiprocessing import Process
from urllib.request import urlopen
from urllib.error import URLError

from .server import app


def start_server(retries=5, delay=0.5):
    process = Process(target=lambda: app.run(debug=False))

    process.start()
    for _ in range(retries):
        try:
            urlopen('http://localhost:5000/index.html').read()
            break
        except URLError:
            sleep(delay)
    else:
        process.terminate()
        process.join()
        raise Exception("Can't initiate test server")

    return process
