"""Gateway errors must never trigger a payment or an automatic retry."""
import io
import json
from unittest.mock import patch
from urllib.error import HTTPError
import pytest
from hirepulse_tools.gateway import GatewayClient, GatewayError, PaymentRequired

def test_gateway_sends_exact_body_and_preserves_response():
    response = io.BytesIO(b'{"status":"ok","domain":"linear.app"}')
    with patch('hirepulse_tools.gateway.urlopen', return_value=response) as send:
        assert GatewayClient().hiring_intent('linear.app')['status'] == 'ok'
    request = send.call_args.args[0]
    assert request.full_url == 'https://gethirepulse.xyz/v1/company-intent'
    assert json.loads(request.data) == {'domain': 'linear.app'}
    assert send.call_count == 1

def test_402_is_exposed_without_retry_or_payment():
    error = HTTPError('https://gethirepulse.xyz', 402, 'Payment Required',
                      {'PAYMENT-REQUIRED': 'challenge'}, io.BytesIO(b'{"x402Version":2}'))
    with patch('hirepulse_tools.gateway.urlopen', side_effect=error) as send:
        with pytest.raises(PaymentRequired) as caught:
            GatewayClient().tech_stack('linear.app')
    assert caught.value.payment_required == 'challenge'
    assert caught.value.body == {'x402Version': 2}
    assert send.call_count == 1

def test_invalid_tool_never_reaches_network():
    with patch('hirepulse_tools.gateway.urlopen') as send:
        with pytest.raises(ValueError):
            GatewayClient().lookup('../admin', domain='linear.app')
    send.assert_not_called()

def test_batch_preserves_inner_tool_name():
    with patch('hirepulse_tools.gateway.urlopen', return_value=io.BytesIO(b'{"quote_id":"example"}')) as send:
        assert GatewayClient().batch('company-intent', ['linear.app'])['quote_id'] == 'example'
    assert json.loads(send.call_args.args[0].data) == {'tool': 'company-intent', 'domains': ['linear.app']}

def test_unavailable_is_not_silently_empty():
    with patch('hirepulse_tools.gateway.urlopen', side_effect=HTTPError('url', 503, 'Unavailable', {}, io.BytesIO(b'{}'))):
        with pytest.raises(GatewayError) as caught:
            GatewayClient().open_jobs('linear.app')
    assert caught.value.status == 503
