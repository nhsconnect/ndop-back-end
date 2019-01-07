import unittest
from mock import MagicMock, patch
from state_model.get_state_model import get_state_model


class TestGetStateModel(unittest.TestCase):
    @patch('state_model.get_state_model.get_state_model.get_state_model')
    @patch('state_model.get_state_model.get_state_model.setup_lambda')
    def test__get_state_model__lambda_handler__WillReturnStateModel__WhenCalledWithAnEventContainingAValidSessionId(self,
                                                                                                                   mock_setup_lambda,
                                                                                                                   mock_get_state_model):
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
        mock_get_state_model.return_value = mock_state_model
        actual_response = get_state_model.lambda_handler({}, MagicMock)
        self.assertEqual(
            actual_response,
            {
                'session_id': '12345',
                'get_preference_result': 'success',
                'existing_preference': {
                    'is_present': True,
                    'id': '12345',
                    'status': 'active'
                },
                'contact_centre': False
            })

    @patch('state_model.get_state_model.get_state_model.handle')
    def test__get_state_model__lambda_handler__WillRaiseAGivenException__WhenAnExceptionOccursThatIsThrownOrUnhandled(
            self,
            mock_handle):
        mock_handle.side_effect = RuntimeError('Example message')

        with self.assertRaises(RuntimeError):
            get_state_model.lambda_handler({}, MagicMock)
    
    @patch('state_model.get_state_model.get_state_model.configure_logger')
    def test__get_state_model__setup_lambda__WillReturnSessionId__WhenEventContainsAValidSessionId(self,
                                                                                                     mock_configure_logger):
        actual = get_state_model.setup_lambda({'session_id': '12345'}, {})
        self.assertEqual(actual, '12345')

    @patch('state_model.get_state_model.get_state_model.configure_logger')
    def test__get_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsNoSessionIdField(self,
                                                                                                          mock_configure_logger):

        with self.assertRaises(AttributeError):
            get_state_model.setup_lambda({}, {})

    @patch('state_model.get_state_model.get_state_model.configure_logger')
    def test__get_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsAnEmptySessionId(self,
                                                                                                          mock_configure_logger):

        with self.assertRaises(AttributeError):
            get_state_model.setup_lambda({'session_id': ''}, {})

    @patch('state_model.get_state_model.get_state_model._kms_decrypt_dict')
    @patch('state_model.get_state_model.get_state_model.StrictRedisCluster')
    def test__get_state_model__get_state_model__WillReturnModel__WhenStateModelExistsForAGivenSessionId(self,
                                                                                                       mock_strict_redis_cluster,
                                                                                                       mock_kms_decrypt):

        mock_kms_decrypt.return_value = {'decrypted_state': True}
        actual = get_state_model.get_state_model('12345')

        self.assertEqual(actual, {'decrypted_state': True})

    @patch('state_model.get_state_model.get_state_model.StrictRedisCluster')
    def test__get_state_model__get_state_model__WillReturnNone__WhenEmptyStateModelExistsForAGivenSessionId(self,
                                                                                                          mock_strict_redis_cluster):
        mock_state_model = {}

        class MockRedisConnection():
            def get(self, session_id):
                return mock_state_model

        mock_strict_redis_cluster.return_value = MockRedisConnection()
        actual = get_state_model.get_state_model('12345')

        self.assertEqual(actual, None)

    @patch('state_model.get_state_model.get_state_model.StrictRedisCluster')
    def test__get_state_model__get_state_model__WillReturnNone__WhenNoStateModelExistsForAGivenSessionId(
            self,
            mock_strict_redis_cluster):
        mock_state_model = None

        class MockRedisConnection():
            def get(self, session_id):
                return mock_state_model

        mock_strict_redis_cluster.return_value = MockRedisConnection()
        actual = get_state_model.get_state_model('12345')

        self.assertEqual(actual, None)