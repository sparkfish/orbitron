import logging

def setup_logger(log_level=logging.DEBUG):
    # setup logging to console output
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger

from fax.storage import Storage

if __name__ == '__main__':
    log = setup_logger()

    storage = Storage()
    storage.connect()
    storage.setup_tables()
