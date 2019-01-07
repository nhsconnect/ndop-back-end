""" Gets a current state_model for the session_id from redis """
import os
import json
import logging

import aws_encryption_sdk
from rediscluster import StrictRedisCluster
from state_model_common_utils import configure_logger, handle_exception
from constants import EVENT_SESSION_ID_FIELD

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOGGER = logging.getLogger()

CMK_KEY_ARN = os.environ.get('CMK_KEY_ARN')
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
    state_model = get_state_model(session_id=session_id)
    LOGGER.info('finished_lambda | lambda_progress=finished')
    return state_model


def setup_lambda(event, context):
    """ This function performs setup actions for the lambda. It will configure the
    logger to be used by the lambda and cache a list of Consent templates globally to be
    used by further invocations of the lambda.

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


def get_state_model(session_id):
    """ Gets the state model from storage and decrypts it presenting it as a dictionary.

    Args:
        session_id (str): ID of the model to retrieve

    Return:
        state_model (dict)
    """
    LOGGER.info('getting_state_model | lambda_progress=in-progress')
    startup_nodes = [{"host": REDIS_HOST, "port": REDIS_PORT}]
    redis_connection = StrictRedisCluster(startup_nodes=startup_nodes,
                                          decode_responses=False,
                                          skip_full_coverage_check=True)
    encrypted_model = redis_connection.get(session_id)

    if not encrypted_model:
        LOGGER.info('no_state_model_stored_against_session | lambda_progress=in_progress')
        return None

    decoded_model = _kms_decrypt_dict(encrypted_model)
    LOGGER.info('got_state_model | lambda_progress=in-progress')
    return decoded_model


def _get_kms_provider():
    return aws_encryption_sdk.KMSMasterKeyProvider(key_ids=[CMK_KEY_ARN])


def _kms_decrypt_text(ciphertext):
    provider = _get_kms_provider()
    plaintext, _ = aws_encryption_sdk.decrypt(source=ciphertext, key_provider=provider)
    return plaintext


def _kms_decrypt_dict(ciphertext):
    plaintext_json = _kms_decrypt_text(ciphertext)
    return json.loads(plaintext_json)
