import sys
import json
import boto3


def restart_stub_fhir_server():
    """ This function uses the boto3 library to invoke a wrapper lambda to trigger a restart of
        the Vonk FHIR server stub.
    """
    environment = sys.argv[1]
    lambda_client = boto3.client('lambda')
    wrapper_function_name = '{}-fhir-stub-wrapper'.format(environment)

    print('Restarting Vonk FHIR server stub using {}'.format(wrapper_function_name))

    encoded_payload = json.dumps({}).encode('utf-8')

    invoke_resp = lambda_client.invoke(
        FunctionName=wrapper_function_name,
        InvocationType='RequestResponse',
        Payload=encoded_payload)

    status_code = invoke_resp['StatusCode']
    if status_code != 200:
        print('Unable to restart Vonk FHIR server stub using. Status code: {}'
              .format(status_code))

    print('Successfully restarted Vonk FHIR server stub')

if __name__ == "__main__":
    restart_stub_fhir_server()
