import unittest
import logging
from mock import MagicMock
from state_model.common import state_model_common_utils


class TestStateModelCommonUtils(unittest.TestCase):

    def test__state_model_common_utils__configure_logger__WillReturnConfiguredLogger__WhenCalledWithValidMetaData(self):
        state_model_common_utils.LOG_LEVEL = 'INFO'
        message = {"session_id": "1234"}
        expected_logger = state_model_common_utils.configure_logger(MagicMock(), message)
        self.assertIsInstance(expected_logger, logging.Logger)

    def test__state_model_common_utils__handle_exception__WillRaiseAGivenException__WhenAnExceptionOccursThatIsThrownOrUnhandled(self):

        try:
            raise RuntimeError
        except:
            with self.assertRaises(RuntimeError):
                state_model_common_utils.handle_exception()