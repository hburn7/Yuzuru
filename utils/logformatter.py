import logging

class LogFormatter(logging.Formatter):
    grey = "\x1b[38;2;170;170;170m"
    white = "\x1b[38;2;236;236;236m"
    yellow = "\x1b[38;2;200;200;50;1m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_fmt = "%(asctime)s - %(name)s - [%(levelname)s]: %(message)s @(%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + log_fmt + reset,
        logging.INFO: white + log_fmt + reset,
        logging.WARNING: yellow + log_fmt + reset,
        logging.ERROR: red + log_fmt + reset,
        logging.CRITICAL: bold_red + log_fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)