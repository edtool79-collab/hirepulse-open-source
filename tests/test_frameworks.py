"""Optional framework adapters dispatch to the same gateway boundary."""
import json
from unittest.mock import Mock
import pytest
from hirepulse_tools.gateway import GatewayClient, PaymentRequired

@pytest.mark.parametrize('framework', ['langchain', 'crewai'])
def test_eight_framework_tools_dispatch_without_losing_names(framework):
    pytest.importorskip('langchain_core' if framework == 'langchain' else 'crewai')
    from hirepulse_tools.frameworks import get_langchain_tools, get_crewai_tools
    client = Mock(spec=GatewayClient)
    client.lookup.return_value = {'status': 'ok'}
    tools = (get_langchain_tools if framework == 'langchain' else get_crewai_tools)(client)
    assert len(tools) == 8
    assert len({t.name for t in tools}) == 8
    if framework == 'langchain':
        result = tools[0].invoke({'domain': 'linear.app'})
    else:
        result = tools[0].run(domain='linear.app')
    assert json.loads(result) == {'status': 'ok'}
    client.lookup.assert_called_once_with('tech-stack', domain='linear.app')

@pytest.mark.parametrize('framework', ['langchain', 'crewai'])
def test_payment_required_is_never_hidden(framework):
    pytest.importorskip('langchain_core' if framework == 'langchain' else 'crewai')
    from hirepulse_tools.frameworks import get_langchain_tools, get_crewai_tools
    client = Mock(spec=GatewayClient)
    client.lookup.side_effect = PaymentRequired({}, 'challenge')
    tool = (get_langchain_tools if framework == 'langchain' else get_crewai_tools)(client)[0]
    with pytest.raises(PaymentRequired):
        if framework == 'langchain': tool.invoke({'domain': 'linear.app'})
        else: tool.run(domain='linear.app')
    assert client.lookup.call_count == 1

def test_quote_flow_requires_unambiguous_input():
    from hirepulse_tools.frameworks import BatchInput, ScanInput
    from pydantic import ValidationError
    with pytest.raises(ValidationError): BatchInput(domains=['linear.app'])
    with pytest.raises(ValidationError): ScanInput(domains=['linear.app', 'ramp.com'], quote_id='example')
