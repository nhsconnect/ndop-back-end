import unittest
from mock import MagicMock, patch
from state_model.put_state_model import put_state_model


def get_mock_event():
    return {
            'session_id': '12345',
            'state_model': {
            'session_id': '12345',
                'get_preference_result': 'success',
                'existing_preference': {
                    'is_present': True,
                    'id': '12345',
                    'status': 'active'
                },
                'contact_centre': False,
                'expiry_time_key': '12345'
            }
        }


class TestPutStateModel(unittest.TestCase):

    @patch('state_model.put_state_model.put_state_model._kms_encrypt_dict')
    @patch('state_model.put_state_model.put_state_model.StrictRedisCluster')
    @patch('state_model.put_state_model.put_state_model.setup_lambda')
    def test__put_state_model__lambda_handler__WillPutSateModel__WhenCalledWithAnEventContainingAValidSessionId(self,
                                                                                                                mock_setup_lambda,
                                                                                                                mock_strict_redis_cluster,
                                                                                                                mock_kms_encrypt):
        mock_redis = MagicMock()
        mock_strict_redis_cluster.return_value = mock_redis
        mock_setup_lambda.return_value = '12345'
        mock_state_model = get_mock_event()
    
        put_state_model.lambda_handler(mock_state_model, MagicMock)
    
        mock_redis.expireat.assert_called_with('12345', '12345')

    @patch('state_model.put_state_model.put_state_model.handle')
    def test__put_state_model__lambda_handler__WillRaiseAGivenException__WhenAnExceptionOccursThatIsThrownOrUnhandled(self,
                                                                                                                      mock_handle):
        mock_handle.side_effect = RuntimeError('Example message')

        with self.assertRaises(RuntimeError):
            put_state_model.lambda_handler({}, MagicMock)

    @patch('state_model.put_state_model.put_state_model.put_state_model')
    @patch('state_model.put_state_model.put_state_model.setup_lambda')
    def test__put_state_model__handle__WillCallPutStateModel__WhenCalledWithAnEventContainingAValidStateModel(self,
                                                                                                              mock_setup_lambda,
                                                                                                              mock_put_state_model):

        mock_setup_lambda.return_value = '12345'
        mock_state_model = get_mock_event()
        put_state_model.handle(mock_state_model, MagicMock)

        mock_put_state_model.assert_called_with(
            '12345',
            {
                'session_id': '12345',
                'get_preference_result': 'success',
                'existing_preference': {
                    'is_present': True,
                    'id': '12345',
                    'status': 'active'
                },
                'contact_centre': False,
                'expiry_time_key': '12345'
            })

    @patch('state_model.put_state_model.put_state_model.setup_lambda')
    def test__put_state_model__lambda_handler__WillRaiseAtributeErrpr__WhenCalledWithAnEventContainingNoStateModel(self,
                                                                                                                   mock_setup_lambda):
        mock_setup_lambda.return_value = '12345'

        with self.assertRaises(AttributeError):
            put_state_model.handle({'session_id': '12345'}, MagicMock)

    @patch('state_model.put_state_model.put_state_model.configure_logger')
    def test__put_state_model__setup_lambda__WillReturnSessionId__WhenEventContainsAValidSessionId(
            self,
            mock_configure_logger):
        actual = put_state_model.setup_lambda({'session_id': '12345'}, {})
        self.assertEqual(actual, '12345')

    @patch('state_model.put_state_model.put_state_model.configure_logger')
    def test__put_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsNoSessionIdField(
            self,
            mock_configure_logger):
        with self.assertRaises(AttributeError):
            put_state_model.setup_lambda({}, {})

    @patch('state_model.put_state_model.put_state_model.configure_logger')
    def test__put_state_model__setup_lambda__WillRaiseAttributeError__WhenEventContainsAnEmptySessionId(
            self,
            mock_configure_logger):
        with self.assertRaises(AttributeError):
            put_state_model.setup_lambda({'session_id': ''}, {})