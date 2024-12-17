import logging
import json
import socket
import sys
from datetime import datetime
from logging.handlers import SocketHandler
from typing import Any, Dict
import logstash
from pythonjsonlogger import jsonlogger

class LogstashFormatter(logging.Formatter):
    def __init__(self):
        super(LogstashFormatter, self).__init__()

    def format(self, record: logging.LogRecord) -> str:
        message = {
            '@timestamp': datetime.utcnow().isoformat(),
            'type': 'fastapi',
            'service': 'fastapi-app',
            'level': record.levelname,
            'host': socket.gethostname(),
            'path': record.pathname,
            'line_number': record.lineno,
            'function': record.funcName,
            'logger': record.name,
            'message': record.getMessage()
        }

        if hasattr(record, 'props'):
            message.update(record.props)

        if record.exc_info:
            message['exception'] = self.formatException(record.exc_info)

        return json.dumps(message)

class CustomLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self.props: Dict[str, Any] = {}

    def _log(self, level: int, msg: str, args: tuple, exc_info=None, extra=None, **kwargs):
        if extra is None:
            extra = {}
        if 'props' in extra:
            props = extra.pop('props')
            if isinstance(props, dict):
                extra['props'] = {**self.props, **props}
        super()._log(level, msg, args, exc_info, extra, **kwargs)

def setup_logging():
    # Set custom logger class
    logging.setLoggerClass(CustomLogger)
    
    # Create logger
    logger = logging.getLogger('fastapi')
    logger.setLevel(logging.INFO)

    # Console handler with LogstashFormatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(LogstashFormatter())
    
    # Logstash handler
    logstash_handler = logstash.TCPLogstashHandler(
        'localhost',
        5000,
        version=1
    )
    logstash_handler.setFormatter(LogstashFormatter())

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(logstash_handler)

    return logger

# Create a singleton logger instance
logger = setup_logging()
