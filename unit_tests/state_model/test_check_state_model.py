import unittest
from mock import MagicMock, patch
from state_model.check_state_model import check_state_model


class TestCheckStateModel(unittest.TestCase):

    @patch('state_model.check_state_model.check_state_model.check_state_model')
    @patch('state_model.check_state_model.check_state_model.setup_lambda')
    def test__check_state_model__lambda_handler__WillReturnExistsTrue__WhenSessionIdExistsInStateModel(self,
                                                                                                       mock_setup_lambda,
                                                                                                       mock_check_state_model):
        mock_check_state_model.return_value = True
        actual_response = check_state_model.lambda_handler({}, MagicMock)
        self.assertEqual(actual_response, '{"exists": true}')

    @patch('state_model.check_state_model.check_state_model.check_state_model')
    @patch('state_model.check_state_model.check_state_model.setup_lambda')
    def test__check_state_model__lambda_handler__WillReturnExistsFalse__WhenSessionIdDoesntExistsInStateModel(self,
                                                                                                              mock_setup_lambda,
                                                                                                              mock_check_state_model):
        mock_check_state_model.return_value = False
        actual_response = check_state_model.lambda_handler({}, MagicMock)
        self.assertEqual(actual_response, '{"exists": false}')

    @patch('state_model.check_state_model.check_state_model.handle')
    def test__check_state_model__lambda_handler__WillRaiseAGivenException__WhenAnExceptionOccursThatIsThrownOrUnhandled(self,
                                                                                                                        mock_handle):
        mock_handle.side_effect = RuntimeError('Example message')

        with self.assertRaises(RuntimeError):
            check_state_model.lambda_handler({}, MagicMock)

    @patch('state_model.check_state_model.check_state_model.configure_logger')
    def test__check_state_model__setup_lambda__WillReturnSessionId__WhenEventContainsAValidSessionId(self,
                                                                                                     mock_configure_logger):
        actual = check_state_model.setup_lambda({'session_id': '12345'}, {})
        self.assertEqual(actual, '12345')

    @patch('state_model.check_state_model.check_state_model.configure_logger')
    def test__check_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsNoSessionIdField(self,
                                                                                                          mock_configure_logger):

        with self.assertRaises(AttributeError):
            check_state_model.setup_lambda({}, {})

    @patch('state_model.check_state_model.check_state_model.configure_logger')
    def test__check_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsAnEmptySessionId(self,
                                                                                                          mock_configure_logger):

        with self.assertRaises(AttributeError):
            check_state_model.setup_lambda({'session_id': ''}, {})

    @patch('state_model.check_state_model.check_state_model.StrictRedisCluster')
    def test__check_state_model__check_state_model__WillReturnTrue__WhenStateModelExistsForAGivenSessionId(self,
                                                                                                           mock_strict_redis_cluster):
        mock_state_model = {
            'session_id': '12345',
            'get_preference_result': 'success',
            'existing_preference': {
                'is_present': True,
                'id': '12345',
                'status': 'active'
            },
            'contact_centre': False
        }

        class MockRedisConnection():
            def get(self, session_id):
                return mock_state_model

        mock_strict_redis_cluster.return_value = MockRedisConnection()

        self.assertTrue(check_state_model.check_state_model('12345'))

    @patch('state_model.check_state_model.check_state_model.StrictRedisCluster')
    def test__check_state_model__check_state_model__WillReturnFalse__WhenNoStateModelExistsForAGivenSessionId(self,
                                                                                                           mock_strict_redis_cluster):
        mock_state_model = {}

        class MockRedisConnection():
            def get(self, session_id):
                return mock_state_model

        mock_strict_redis_cluster.return_value = MockRedisConnection()

        self.assertFalse(check_state_model.check_state_model('12345'))