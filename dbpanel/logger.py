import logging


class Logger:
    LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'

    def __init__(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        # log_handler = logging.FileHandler('dbpanel.log', 'a')
        log_formatter = logging.Formatter(self.LOG_FORMAT)
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)
        self.logger = logger

    def get_logger(self):
        return self.logger

    def log_info(self, message, *args):
        if len(args):
            self.logger.info(message, *args)
        else:
            self.logger.info(message)

    def log_debug(self, message, *args):
        if len(args):
            self.logger.debug(message, *args)
        else:
            self.logger.debug(message)

    def log_error(self, message, *args):
        if len(args):
            self.logger.error(message, *args)
        else:
            self.logger.error(message)
