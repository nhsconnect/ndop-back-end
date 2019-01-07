""" Puts (saves in redis) a current state_model for the session_id """
import os
import json
import logging

import aws_encryption_sdk
from rediscluster import StrictRedisCluster
from state_model_common_utils import configure_logger, handle_exception
from constants import EVENT_SESSION_ID_FIELD, EVENT_STATE_MODEL_FIELD, STATE_MODEL_EXPIRY_TIME_KEY

LOGGER = logging.getLogger()

LOG_LEVEL = os.environ.get('LOG_LEVEL')
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
    state_model = event.get(EVENT_STATE_MODEL_FIELD)
    if not state_model:
        LOGGER.error('error '
                     '| failed_task=get_session_id '
                     '| error_message="No session_id provided to retrieve state model" '
                     '| lambda_progress=error ')
        raise AttributeError('No session_id provided')

    put_state_model(session_id, state_model)
    LOGGER.info('finished_lambda | lambda_progress=finished')


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
                     '| error_message="No session_id provided to retrieve state model"')
        raise AttributeError('No session_id provided')

    configure_logger(context, session_id)
    LOGGER.info('starting_lambda | lambda_progress=started')

    return session_id


def put_state_model(session_id, state_model):
    """ Encrypts the provided state model and stores it against the provided ID.

    Args:
        session_id (str): ID to store the model against
        state_model (dict): Simple state model to be encrypted and stored.
    """
    LOGGER.info('put_state_model_start | lambda_progress=in-progress')
    expires_at_timestamp = state_model[STATE_MODEL_EXPIRY_TIME_KEY]
    encrypted_model = _kms_encrypt_dict(state_model)
    startup_nodes = [{"host": REDIS_HOST, "port": REDIS_PORT}]
    redis_connection = StrictRedisCluster(startup_nodes=startup_nodes,
                                          decode_responses=False,
                                          skip_full_coverage_check=True)
    redis_connection.set(session_id, encrypted_model)
    redis_connection.expireat(session_id, expires_at_timestamp)
    LOGGER.info('put_state_model_finish | lambda_progress=in-progress')

def _get_kms_provider():
    return aws_encryption_sdk.KMSMasterKeyProvider(key_ids=[CMK_KEY_ARN])


def _kms_encrypt_text(plaintext):
    """ Encrypts provided plaintext with KMS. """
    provider = _get_kms_provider()
    ciphertext, _ = aws_encryption_sdk.encrypt(source=plaintext, key_provider=provider)
    return ciphertext


def _kms_encrypt_dict(plaintext_dict):
    """ Converts provided dictionary into JSON and encrypts it with KMS. """
    plaintext_json = json.dumps(plaintext_dict)
    return _kms_encrypt_text(plaintext_json)
