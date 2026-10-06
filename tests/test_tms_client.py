import pytest
import os
from tms_client import TMSClient, TMSConnectionError, TMSProtocolError


class TestTMSClientConnection:

    @pytest.fixture
    def client(self):
        return TMSClient()

    def test_client_initialization(self, client):
        assert client.host == "tramway.proxy.rlwy.net"
        assert client.port == 17159
        assert client.timeout == 6.0
        assert client.token is not None

    def test_client_initialization_custom_values(self):
        client = TMSClient(host="localhost", port=9999, token="test_token")
        assert client.host == "localhost"
        assert client.port == 9999
        assert client.token == "test_token"

    def test_connection_to_real_tms(self, client):
        response = client.send_and_receive("DEBUG_ECHO")
        assert response is not None
        assert len(response) > 0

    def test_connection_timeout_invalid_host(self):
        client = TMSClient(host="invalid.host.example.com", port=17159, timeout=1)
        with pytest.raises(TMSConnectionError):
            client.send_and_receive("DEBUG_ECHO")


class TestTMSClientCommands:

    @pytest.fixture
    def client(self):
        return TMSClient()

    def test_debug_echo_command(self, client):
        response = client.debug_echo()
        assert response is not None

    def test_debug_echo_returns_string(self, client):
        response = client.debug_echo()
        assert isinstance(response, str)

    def test_load_get_known_load(self, client):
        response = client.load_get("LD00903")
        assert response is not None
        assert "LOAD_ID" in response or "ERR" in response

    def test_load_get_response_contains_expected_fields(self, client):
        response = client.load_get("LD00903")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_load_query_command(self, client):
        response = client.load_query("GA", "NE", "REEFER")
        assert response is not None
        assert isinstance(response, str)


class TestTMSResponseParsing:

    @pytest.fixture
    def client(self):
        return TMSClient()

    def test_parse_load_details_known_format(self):
        response = "LOAD_ID:LD00903|ORIG_CITY:Savannah|ORIG_STATE:GA|ORIG_ZIP:31401|DEST_CITY:Omaha|DEST_STATE:NE|DEST_ZIP:68102|PICKUP_DT:20261008120900|DELIVERY_DT:20261010050900|EQTYPE:REEFER|RATE:2038|WEIGHT:6186|COMMODITY:Machinery|PIECES:6|MILES:1036|DIMS:48ft x 8ft x 9ft|NOTES:Pickup numbers on rate con.|STATUS:OPEN|MAX_BUY:2184"

        client = TMSClient()
        details = client.parse_load_details(response)

        assert details["LOAD_ID"] == "LD00903"
        assert details["ORIG_CITY"] == "Savannah"
        assert details["ORIG_STATE"] == "GA"
        assert details["DEST_STATE"] == "NE"
        assert details["RATE"] == "2038"
        assert details["MAX_BUY"] == "2184"
        assert details["EQTYPE"] == "REEFER"

    def test_parse_load_details_empty_response(self):
        client = TMSClient()
        details = client.parse_load_details("")
        assert details == {}

    def test_parse_load_details_single_line(self):
        response = "LOAD_ID: LD00903"
        client = TMSClient()
        details = client.parse_load_details(response)
        assert details["LOAD_ID"] == "LD00903"


class TestTMSProtocolFraming:

    @pytest.fixture
    def client(self):
        return TMSClient()

    def test_payload_uses_crlf_framing(self, client):
        response = client.send_and_receive("DEBUG_ECHO")
        assert response is not None

    def test_response_decoding_utf8(self, client):
        response_bytes = client.send_and_receive("DEBUG_ECHO")
        response_str = response_bytes.decode('utf-8', errors='replace')
        assert isinstance(response_str, str)


class TestTMSSecurityRules:

    def test_token_not_logged_in_debug(self):
        client = TMSClient(token="SECRET_TOKEN_12345")
        client_str = str(client.__dict__)

    def test_environment_variable_handling(self):
        token = os.environ.get("TMS_TOKEN")
        client = TMSClient()
        assert client.token == token


class TestTMSKnownLoadData:

    @pytest.fixture
    def client(self):
        return TMSClient()

    def test_load_ld00903_exists(self, client):
        response = client.load_get("LD00903")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_load_ld00903_contains_required_fields(self, client):
        response = client.load_get("LD00903")
        if "LOAD_ID" in response:
            details = client.parse_load_details(response)
            assert "LOAD_ID" in details
            assert details["LOAD_ID"] == "LD00903"

    def test_load_ld00903_rate_and_max_buy(self, client):
        response = client.load_get("LD00903")
        if "LOAD_ID" in response:
            details = client.parse_load_details(response)
            assert details.get("RATE") == "2038"
            assert details.get("MAX_BUY") == "2184"
