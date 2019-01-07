import unittest
from mock import MagicMock, patch
from state_model.delete_state_model import delete_state_model


class TestDeleteStateModel(unittest.TestCase):

    @patch('state_model.delete_state_model.delete_state_model.StrictRedisCluster')
    @patch('state_model.delete_state_model.delete_state_model.setup_lambda')
    def test__delete_state_model__lambda_handler__WillDeleteStateModel__WhenCalledWithAnEventContainingAValidSessionId(self,
                                                                                                                       mock_setup_lambda,
                                                                                                                       mock_strict_redis_cluster):

        mock_redis = MagicMock()
        mock_strict_redis_cluster.return_value = mock_redis
        mock_setup_lambda.return_value = '12345'

        delete_state_model.lambda_handler({'session_id': '12345'}, {})

        mock_redis.delete.assert_called_with('12345')

    @patch('state_model.delete_state_model.delete_state_model.handle')
    def test__delete_state_model__lambda_handler__WillRaiseAGivenException__WhenAnExceptionOccursThatIsThrownOrUnhandled(self,
                                                                                                                         mock_handle):
        mock_handle.side_effect = RuntimeError('Example message')

        with self.assertRaises(RuntimeError):
            delete_state_model.lambda_handler({}, MagicMock)

    @patch('state_model.delete_state_model.delete_state_model.configure_logger')
    def test__delete_state_model__setup_lambda__WillReturnSessionId__WhenEventContainsAValidSessionId(self,
                                                                                                      mock_configure_logger):
        actual = delete_state_model.setup_lambda({'session_id': '12345'}, {})
        self.assertEqual(actual, '12345')

    @patch('state_model.delete_state_model.delete_state_model.configure_logger')
    def test__delete_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsNoSessionIdField(self,
                                                                                                           mock_configure_logger):
        with self.assertRaises(AttributeError):
            delete_state_model.setup_lambda({}, {})

    @patch('state_model.delete_state_model.delete_state_model.configure_logger')
    def test__delete_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsAnEmptySessionId(self,
                                                                                                           mock_configure_logger):
        with self.assertRaises(AttributeError):
            delete_state_model.setup_lambda({'session_id': ''}, {})