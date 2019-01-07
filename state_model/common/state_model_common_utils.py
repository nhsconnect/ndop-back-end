""" This module contains common utils for use by other Python modules. """
import os
import datetime
import logging
import sys
import traceback
from constants import EMPTY_STRING, DOUBLE_QUOTE, SINGLE_QUOTE, NEW_LINE

LOG_LEVEL = os.environ.get('LOG_LEVEL')
ENVIRONMENT_NAME = os.environ.get('ENV_NAME')
LOGGER = logging.getLogger()


def configure_logger(context, session_id=None):
    """ default logger configuration with default timestamp handling """

    meta_data = {
        'function_name': context.function_name,
        'function_version': context.function_version,
        'invocation_id': context.aws_request_id,
        'session_id': session_id
    }

    LOGGER.setLevel(LOG_LEVEL)
    handler = DefaultStreamHandler(meta_data)

    LOGGER.handlers = []
    LOGGER.addHandler(handler)

    return LOGGER


class MyFormatter(logging.Formatter):
    """ Provides consistent formatting of timestamps """
    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        created = self.converter(record.created)
        if datefmt:
            result = created.strftime(datefmt)
        else:
            time = created.strftime("%Y-%m-%d %H:%M:%S")
            result = "%s,%03d" % (time, record.msecs)
        return result


class DefaultStreamHandler(logging.StreamHandler):
    """This class is the default log handler for when the service starts up."""

    def __init__(self, meta_data):
        super().__init__()
        meta_data = meta_data

        self.stream = sys.stdout

        format_str = 'time=%(asctime)s '\
                     '| log_level=%(levelname)s '\
                     '| message=%(message)s ' \
                     '| environment={environment} ' \
                     '| function_name={function_name} ' \
                     '| function_version={function_version} ' \
                     '| invocation_id={invocation_id} ' \
                     '| session_id={session_id} '

        formatter = MyFormatter(
            fmt=format_str.format(environment=ENVIRONMENT_NAME,
                                  function_name=meta_data['function_name'],
                                  function_version=meta_data['function_version'],
                                  invocation_id=meta_data['invocation_id'],
                                  session_id=meta_data['session_id']),
            datefmt="%d-%m-%Y %H:%M:%S.%f %z")
        self.setFormatter(formatter)


def handle_exception():
    """ This utility function is used to process an exception. It will get the information of the
        exception thrown. This information includes the exceptions type, message (if present)
        as well as the associated stack trace. It will then produce a log containing this
        information.
    """
    exc_type, exc_message, exc_traceback = sys.exc_info()

    stack_trace = traceback.format_tb(exc_traceback)
    formatted_stack_trace = EMPTY_STRING.join(
        [line.replace(DOUBLE_QUOTE, SINGLE_QUOTE).replace(NEW_LINE, EMPTY_STRING) for line in
         stack_trace]
    )

    LOGGER.error('exception '
                 '| lambda_progress=error '
                 '| exception_type="%s" '
                 '| exception_message="%s" '
                 '| stacktrace="%s"', exc_type, exc_message, formatted_stack_trace)

    raise exc_type(exc_message)
