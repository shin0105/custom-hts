"""Tests for KDEVELOPERS API integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import requests
from src.integrations.kdevelopers import APIResponse, KDevelopersClient


class TestAPIResponse:
    """Tests for APIResponse class."""

    def test_api_response_success(self):
        """Test APIResponse with successful response."""
        # Mock successful response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {
            "tr_id": "FHKST01010100",
            "tr_cont": "F"
        }
        mock_response.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "SUCCESS",
            "msg1": "조회 성공",
            "output": {"test": "data"}
        }

        api_resp = APIResponse(mock_response)

        assert api_resp.is_ok() is True
        assert api_resp.get_res_code() == 200
        assert api_resp.get_error_code() == "SUCCESS"
        assert api_resp.get_error_message() == "조회 성공"

    def test_api_response_error(self):
        """Test APIResponse with error response."""
        # Mock error response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {
            "tr_id": "FHKST01010100"
        }
        mock_response.json.return_value = {
            "rt_cd": "1",
            "msg_cd": "EGW00123",
            "msg1": "조회 실패"
        }

        api_resp = APIResponse(mock_response)

        assert api_resp.is_ok() is False
        assert api_resp.get_res_code() == 200
        assert api_resp.get_error_code() == "EGW00123"
        assert api_resp.get_error_message() == "조회 실패"

    def test_api_response_malformed(self):
        """Test APIResponse with malformed JSON."""
        # Mock malformed response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.side_effect = ValueError("Invalid JSON")

        api_resp = APIResponse(mock_response)

        # Should not crash, should handle gracefully
        assert api_resp.is_ok() is False
        assert api_resp.get_res_code() == 200


class TestKDevelopersClient:
    """Tests for KDevelopersClient class."""

    @patch('src.integrations.kdevelopers.settings')
    def test_client_initialization(self, mock_settings):
        """Test client initialization."""
        mock_settings.HANTU_API_KEY = "test_key"
        mock_settings.HANTU_API_SECRET = "test_secret"
        mock_settings.HANTU_BASE_URL = "https://api.test.com"

        client = KDevelopersClient()

        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.base_url == "https://api.test.com"
        assert client.access_token is None

    @patch('src.integrations.kdevelopers.settings')
    @patch('src.integrations.kdevelopers.requests.post')
    def test_get_access_token_success(self, mock_post, mock_settings):
        """Test successful token retrieval."""
        mock_settings.HANTU_API_KEY = "test_key"
        mock_settings.HANTU_API_SECRET = "test_secret"
        mock_settings.HANTU_BASE_URL = "https://api.test.com"

        # Mock token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token_12345",
            "access_token_token_expired": "2024-02-05 12:00:00"
        }
        mock_post.return_value = mock_response

        client = KDevelopersClient()
        token = client._get_access_token()

        assert token == "test_token_12345"
        assert client.access_token == "test_token_12345"
        mock_post.assert_called_once()

    @patch('src.integrations.kdevelopers.settings')
    @patch('src.integrations.kdevelopers.requests.post')
    def test_get_access_token_failure(self, mock_post, mock_settings):
        """Test token retrieval failure."""
        mock_settings.HANTU_API_KEY = "test_key"
        mock_settings.HANTU_API_SECRET = "test_secret"
        mock_settings.HANTU_BASE_URL = "https://api.test.com"

        # Mock failed response
        mock_post.side_effect = requests.RequestException("Connection error")

        client = KDevelopersClient()
        token = client._get_access_token()

        assert token is None

    @patch('src.integrations.kdevelopers.settings')
    def test_get_access_token_no_credentials(self, mock_settings):
        """Test token retrieval with missing credentials."""
        mock_settings.HANTU_API_KEY = None
        mock_settings.HANTU_API_SECRET = None
        mock_settings.HANTU_BASE_URL = "https://api.test.com"

        client = KDevelopersClient()
        token = client._get_access_token()

        assert token is None

    @patch('src.integrations.kdevelopers.settings')
    @patch('src.integrations.kdevelopers.KDevelopersClient._get_access_token')
    @patch('src.integrations.kdevelopers.requests.get')
    @patch('src.integrations.kdevelopers.time.sleep')  # Mock sleep to speed up tests
    def test_get_quote_success(self, mock_sleep, mock_get, mock_get_token, mock_settings):
        """Test successful quote retrieval."""
        mock_settings.HANTU_API_KEY = "test_key"
        mock_settings.HANTU_API_SECRET = "test_secret"
        mock_settings.HANTU_BASE_URL = "https://api.test.com"

        mock_get_token.return_value = "test_token"

        # Mock quote response - make output a dictionary
        output_data = {
            "stck_prpr": "70000",
            "stck_sdpr": "69000",
            "prdy_vrss": "1000",
            "prdy_ctrt": "1.45",
            "acml_vol": "10000000",
            "hts_kor_isnm": "삼성전자",
            "stck_hgpr": "71000",
            "stck_lwpr": "69000",
            "stck_oprc": "69500"
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"tr_cont": "F"}
        mock_response.json.return_value = {
            "rt_cd": "0",
            "msg_cd": "SUCCESS",
            "msg1": "조회 성공",
            "output": output_data
        }
        mock_get.return_value = mock_response

        client = KDevelopersClient()
        quote = client.get_quote("005930")

        assert quote is not None
        assert quote.symbol == "005930"
        assert quote.name == "삼성전자"
        assert quote.current_price == 70000.0
        assert quote.change == 1000.0
        assert quote.change_percent == 1.45

    @patch('src.integrations.kdevelopers.settings')
    @patch('src.integrations.kdevelopers.KDevelopersClient._get_access_token')
    def test_get_quote_no_token(self, mock_get_token, mock_settings):
        """Test quote retrieval without token."""
        mock_settings.HANTU_API_KEY = "test_key"
        mock_settings.HANTU_API_SECRET = "test_secret"
        mock_settings.HANTU_BASE_URL = "https://api.test.com"

        mock_get_token.return_value = None

        client = KDevelopersClient()
        
        # Should return None when token retrieval fails
        quote = client.get_quote("005930")
        assert quote is None


def test_api_response_header_parsing():
    """Test APIResponse header parsing."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.headers = {
        "tr_id": "FHKST01010100",
        "tr_cont": "F"
    }
    mock_response.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "SUCCESS",
        "msg1": "Success"
    }

    api_resp = APIResponse(mock_response)
    header = api_resp.get_header()

    # Check that lowercase headers are parsed
    assert hasattr(header, 'tr_id')
    assert header.tr_id == "FHKST01010100"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
