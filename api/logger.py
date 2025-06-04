import logging

def setup_logger():
    logger = logging.getLogger("mlflow_api")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("mlflow_api.log")
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger

logger = setup_logger()

