import json, os
from log.logger import logger as log

def read_data():
    data = []
    try:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"data.json"), "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                log.info("data file is empty or cannot decode, reseted.")
                pass
    except FileNotFoundError:
        log.info("data file not exist, created one.")
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"data.json"), "w") as f:
            pass
    return data

def write_data(data):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"data.json"), "w") as f:
        f.write(json.dumps(data))
        log.info("data written, current length is {}".format(len(data)))

if __name__=="__main__":
    r = read_data()
    print(r)