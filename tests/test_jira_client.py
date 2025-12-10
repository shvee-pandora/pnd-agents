"""
Unit tests for the JIRA Client.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.jira_client import JiraClient, JiraConfig, JiraIssue, generate_custom_fields_readme


class TestJiraConfig:
    """Tests for JiraConfig dataclass."""
    
    def test_from_dict(self):
        """Test JiraConfig from_dict creation."""
        data = {
            "base_url": "https://test.atlassian.net",
            "email": "test@example.com",
            "api_token": "test-token",
            "cloud_id": "test-cloud-id",
            "field_ai_used": "customfield_10001",
        }
        
        config = JiraConfig.from_dict(data)
        
        assert config.base_url == "https://test.atlassian.net"
        assert config.email == "test@example.com"
        assert config.api_token == "test-token"
        assert config.cloud_id == "test-cloud-id"
        assert config.field_ai_used == "customfield_10001"
    
    def test_from_env(self):
        """Test JiraConfig from_env creation."""
        with patch.dict(os.environ, {
            "JIRA_BASE_URL": "https://env.atlassian.net",
            "JIRA_EMAIL": "env@example.com",
            "JIRA_API_TOKEN": "env-token",
        }):
            config = JiraConfig.from_env()
            
            assert config.base_url == "https://env.atlassian.net"
            assert config.email == "env@example.com"
            assert config.api_token == "env-token"
    
    def test_to_dict(self):
        """Test JiraConfig to_dict conversion (without sensitive data)."""
        config = JiraConfig(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="secret-token",
        )
        
        result = config.to_dict()
        
        assert result["base_url"] == "https://test.atlassian.net"
        assert result["email"] == "test@example.com"
        assert "api_token" not in result  # Should not include sensitive data


class TestJiraIssue:
    """Tests for JiraIssue dataclass."""
    
    def test_from_api_response(self):
        """Test JiraIssue from_api_response creation."""
        api_response = {
            "key": "EPA-123",
            "id": "12345",
            "fields": {
                "summary": "Test Issue",
                "status": {"name": "In Progress"},
                "issuetype": {"name": "Task"},
                "description": "Test description",
                "assignee": {"displayName": "John Doe"},
                "priority": {"name": "High"},
                "labels": ["ai", "automation"],
            },
        }
        
        issue = JiraIssue.from_api_response(api_response)
        
        assert issue.key == "EPA-123"
        assert issue.id == "12345"
        assert issue.summary == "Test Issue"
        assert issue.status == "In Progress"
        assert issue.issue_type == "Task"
        assert issue.assignee == "John Doe"
        assert issue.priority == "High"
        assert issue.labels == ["ai", "automation"]
    
    def test_from_api_response_minimal(self):
        """Test JiraIssue from_api_response with minimal data."""
        api_response = {
            "key": "EPA-456",
            "id": "67890",
            "fields": {
                "summary": "Minimal Issue",
                "status": {"name": "Open"},
                "issuetype": {"name": "Bug"},
            },
        }
        
        issue = JiraIssue.from_api_response(api_response)
        
        assert issue.key == "EPA-456"
        assert issue.summary == "Minimal Issue"
        assert issue.assignee is None
        assert issue.priority is None
        assert issue.labels == []


class TestJiraClient:
    """Tests for JiraClient class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock JiraConfig."""
        return JiraConfig(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test-token",
        )
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a JiraClient with mock config."""
        return JiraClient(config=mock_config)
    
    def test_init(self, mock_config):
        """Test JiraClient initialization."""
        client = JiraClient(config=mock_config)
        
        assert client.config == mock_config
        assert client._client is None
    
    def test_get_api_base_url(self, client):
        """Test API base URL construction."""
        url = client._get_api_base_url()
        
        assert url == "https://test.atlassian.net/rest/api/3/"
    
    def test_markdown_to_adf_paragraph(self, client):
        """Test markdown to ADF conversion for paragraphs."""
        markdown = "This is a test paragraph."
        
        adf = client._markdown_to_adf(markdown)
        
        assert adf["type"] == "doc"
        assert adf["version"] == 1
        assert len(adf["content"]) == 1
        assert adf["content"][0]["type"] == "paragraph"
    
    def test_markdown_to_adf_list(self, client):
        """Test markdown to ADF conversion for lists."""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        
        adf = client._markdown_to_adf(markdown)
        
        assert adf["type"] == "doc"
        assert len(adf["content"]) == 1
        assert adf["content"][0]["type"] == "bulletList"
        assert len(adf["content"][0]["content"]) == 3
    
    def test_markdown_to_adf_bold(self, client):
        """Test markdown to ADF conversion for bold text."""
        markdown = "This is **bold** text."
        
        adf = client._markdown_to_adf(markdown)
        
        assert adf["type"] == "doc"
        content = adf["content"][0]["content"]
        bold_found = any(
            item.get("marks", [{}])[0].get("type") == "strong"
            for item in content
            if "marks" in item
        )
        assert bold_found
    
    @patch("httpx.Client")
    def test_get_issue(self, mock_client_class, client):
        """Test get_issue method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "key": "EPA-123",
            "id": "12345",
            "fields": {
                "summary": "Test Issue",
                "status": {"name": "Open"},
                "issuetype": {"name": "Task"},
            },
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = MagicMock()
        mock_http_client.get.return_value = mock_response
        mock_client_class.return_value = mock_http_client
        
        client._client = mock_http_client
        issue = client.get_issue("EPA-123")
        
        assert issue is not None
        assert issue.key == "EPA-123"
        mock_http_client.get.assert_called_once()
    
    @patch("httpx.Client")
    def test_add_comment(self, mock_client_class, client):
        """Test add_comment method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "comment-123"}
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = MagicMock()
        mock_http_client.post.return_value = mock_response
        mock_client_class.return_value = mock_http_client
        
        client._client = mock_http_client
        result = client.add_comment("EPA-123", "Test comment")
        
        assert result["id"] == "comment-123"
        mock_http_client.post.assert_called_once()
    
    @patch("httpx.Client")
    def test_update_fields(self, mock_client_class, client):
        """Test update_fields method."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = MagicMock()
        mock_http_client.put.return_value = mock_response
        mock_client_class.return_value = mock_http_client
        
        client._client = mock_http_client
        result = client.update_fields("EPA-123", {"summary": "Updated"})
        
        assert result is True
        mock_http_client.put.assert_called_once()
    
    @patch("httpx.Client")
    def test_update_ai_fields(self, mock_client_class, client):
        """Test update_ai_fields method."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = MagicMock()
        mock_http_client.put.return_value = mock_response
        mock_client_class.return_value = mock_http_client
        
        client._client = mock_http_client
        result = client.update_ai_fields(
            "EPA-123",
            ai_used=True,
            agent_name="Test Agent",
            efficiency_score=95.0,
            duration_ms=5000,
        )
        
        assert result is True
    
    @patch("httpx.Client")
    def test_test_connection(self, mock_client_class, client):
        """Test test_connection method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"displayName": "Test User"}
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = MagicMock()
        mock_http_client.get.return_value = mock_response
        mock_client_class.return_value = mock_http_client
        
        client._client = mock_http_client
        result = client.test_connection()
        
        assert result is True
    
    def test_context_manager(self, mock_config):
        """Test JiraClient as context manager."""
        with JiraClient(config=mock_config) as client:
            assert client is not None
            assert client.config == mock_config


class TestGenerateCustomFieldsReadme:
    """Tests for generate_custom_fields_readme function."""
    
    def test_generate_readme(self):
        """Test README generation."""
        readme = generate_custom_fields_readme()
        
        assert "JIRA Custom Fields Setup" in readme
        assert "AI Used" in readme
        assert "Agent Name" in readme
        assert "AI Efficiency Score" in readme
        assert "AI Duration" in readme
        assert "customfield_" in readme
