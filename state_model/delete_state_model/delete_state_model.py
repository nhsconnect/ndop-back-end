""" Deletes a current state_model for the session_id from redis """
import os
import logging
from rediscluster import StrictRedisCluster
from state_model_common_utils import configure_logger, handle_exception
from constants import EVENT_SESSION_ID_FIELD

LOGGER = logging.getLogger()

LOG_LEVEL = os.environ.get('LOG_LEVEL')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')


def lambda_handler(event, context):
    """ This is the entry point for the lambda. It will call the main handler, which is within a
        try/catch so that we can efficiently log any unhandled exceptions to Cloudwatch/Splunk.

        Args:
            event (dictionary): contains event data passed in by AWS Lambda and
                follows the generic data structure for an AWS Lambda event.
            context (AWS Lambda Context object): contains runtime information for this handler

        Returns:
            response (dict): a dict containing the response to be sent back to the client
    """
    try:
        return handle(event, context)
    except Exception:
        handle_exception()


def handle(event, context):
    """ This function is the entry point for the Lambda. It will handle incoming
       requests.

           Args:
            event (dict): the event data passed to the lambda
            context (AWS Lambda Context object): contains runtime information
                for this handler
    """
    session_id = setup_lambda(event, context)
    delete_state_model(session_id=session_id)
    LOGGER.info('finished_lambda | lambda_progress=finished')


def setup_lambda(event, context):
    """ This function is the entry point for the Lambda. It will handle incoming
       requests.

           Args:
            event (dict): the event data passed to the lambda
            context (AWS Lambda Context object): contains runtime information
                for this handler
    """
    session_id = event.get(EVENT_SESSION_ID_FIELD)
    if not session_id:
        LOGGER.error('error '
                     '| failed_task=get_session_id '
                     '| error_message="No session_id provided to retrieve state model" '
                     '| lambda_progress=error ')
        raise AttributeError('No session_id provided')

    configure_logger(context, session_id)
    LOGGER.info('starting_lambda | lambda_progress=started')
    return session_id


def delete_state_model(session_id):
    """ Deletes the state model from storage.

    session_id (str): ID of the model to delete

    """
    LOGGER.info('deleting_state_model | lambda_progress=in-progress')
    startup_nodes = [{"host": REDIS_HOST, "port": REDIS_PORT}]
    redis_connection = StrictRedisCluster(startup_nodes=startup_nodes,
                                          decode_responses=True,
                                          skip_full_coverage_check=True)
    redis_connection.delete(session_id)
    LOGGER.info('deleted_state_model | lambda_progress=in-progress')
