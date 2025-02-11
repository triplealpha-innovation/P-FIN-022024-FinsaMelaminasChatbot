"""
utils/logger.py

Este módulo configura y devuelve loggers personalizados para el proyecto.
"""
import logging
import sys

class CustomFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    COLORS = {
        'DEBUG': '\033[94m',  # Azul
        'INFO': '\033[92m',   # Verde
        'WARNING': '\033[93m',# Amarillo
        'ERROR': '\033[91m',  # Rojo
        'CRITICAL': '\033[95m'# Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def configure_logger(name='apichatbot-finsa_Logger', level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = CustomFormatter('[%(name)s] %(levelname)s:  %(message)s')
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
