import logging

def loggers(b):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    file_handler = logging.FileHandler("/Users/nusrat/Desktop/VSCODE/Learning-management-system/LMS/loggers/"+b, mode='w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
