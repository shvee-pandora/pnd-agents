"""
MS Teams API Tool

Provides integration with Microsoft Teams using Microsoft Graph API.
Supports reading/sending messages, listing channels, and team operations.

Required Environment Variables:
- MS_TEAMS_CLIENT_ID: Azure AD Application (client) ID
- MS_TEAMS_CLIENT_SECRET: Azure AD Application secret
- MS_TEAMS_TENANT_ID: Azure AD Tenant ID
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class MSTeamsAuthError(Exception):
    """Raised when authentication with MS Teams fails."""
    pass


class MSTeamsAPIError(Exception):
    """Raised when an API call to MS Teams fails."""
    pass


@dataclass
class MSTeamsConfig:
    """Configuration for MS Teams API."""
    client_id: str
    client_secret: str
    tenant_id: str
    graph_api_base: str = "https://graph.microsoft.com/v1.0"

    @classmethod
    def from_env(cls) -> "MSTeamsConfig":
        """Create config from environment variables."""
        client_id = os.environ.get("MS_TEAMS_CLIENT_ID", "")
        client_secret = os.environ.get("MS_TEAMS_CLIENT_SECRET", "")
        tenant_id = os.environ.get("MS_TEAMS_TENANT_ID", "")

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )

    def is_configured(self) -> bool:
        """Check if all required config is present."""
        return bool(self.client_id and self.client_secret and self.tenant_id)


@dataclass
class TeamInfo:
    """Information about a Teams team."""
    id: str
    display_name: str
    description: Optional[str] = None
    visibility: Optional[str] = None
    created_datetime: Optional[str] = None


@dataclass
class ChannelInfo:
    """Information about a Teams channel."""
    id: str
    display_name: str
    description: Optional[str] = None
    membership_type: Optional[str] = None
    web_url: Optional[str] = None


@dataclass
class MessageInfo:
    """Information about a Teams message."""
    id: str
    created_datetime: str
    body_content: str
    body_content_type: str
    from_user: Optional[str] = None
    from_user_id: Optional[str] = None
    subject: Optional[str] = None
    importance: Optional[str] = None
    web_url: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    mentions: List[Dict[str, Any]] = field(default_factory=list)
    reactions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MSTeamsConnectionStatus:
    """Status of MS Teams connection."""
    connected: bool
    message: str
    user_info: Optional[Dict[str, Any]] = None
    teams_count: int = 0


class MSTeamsAPI:
    """
    MS Teams API client using Microsoft Graph API.

    Provides methods to:
    - Check connection status
    - List teams and channels
    - Read messages from channels
    - Send messages to channels
    - Reply to messages
    """

    def __init__(self, config: Optional[MSTeamsConfig] = None):
        """
        Initialize the MS Teams API client.

        Args:
            config: Optional MSTeamsConfig. If not provided, loads from environment.
        """
        self.config = config or MSTeamsConfig.from_env()
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    def _get_access_token(self) -> str:
        """
        Get or refresh the access token using client credentials flow.

        Returns:
            Access token string

        Raises:
            MSTeamsAuthError: If authentication fails
        """
        # Check if we have a valid cached token
        if self._access_token and self._token_expires:
            if datetime.now() < self._token_expires - timedelta(minutes=5):
                return self._access_token

        if not self.config.is_configured():
            raise MSTeamsAuthError(
                "MS Teams not configured. Please set environment variables: "
                "MS_TEAMS_CLIENT_ID, MS_TEAMS_CLIENT_SECRET, MS_TEAMS_TENANT_ID"
            )

        try:
            import requests
        except ImportError:
            raise MSTeamsAuthError("requests library not installed. Run: pip install requests")

        token_url = f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/token"

        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }

        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires = datetime.now() + timedelta(seconds=expires_in)

            return self._access_token

        except requests.exceptions.RequestException as e:
            raise MSTeamsAuthError(f"Failed to authenticate with MS Teams: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise MSTeamsAuthError(f"Invalid token response: {str(e)}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Graph API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., /teams)
            data: Optional request body
            params: Optional query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            MSTeamsAPIError: If the API call fails
        """
        try:
            import requests
        except ImportError:
            raise MSTeamsAPIError("requests library not installed")

        token = self._get_access_token()
        url = f"{self.config.graph_api_base}{endpoint}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )

            if response.status_code == 204:  # No content
                return {"success": True}

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except:
                pass
            raise MSTeamsAPIError(f"API request failed: {error_msg}")

    def verify_connection(self) -> MSTeamsConnectionStatus:
        """
        Verify connection to MS Teams and return status.

        Returns:
            MSTeamsConnectionStatus with connection details
        """
        if not self.config.is_configured():
            return MSTeamsConnectionStatus(
                connected=False,
                message="MS Teams not configured. Required environment variables: "
                        "MS_TEAMS_CLIENT_ID, MS_TEAMS_CLIENT_SECRET, MS_TEAMS_TENANT_ID"
            )

        try:
            # Try to get list of teams to verify connection
            teams = self.list_teams()
            return MSTeamsConnectionStatus(
                connected=True,
                message="Successfully connected to MS Teams",
                teams_count=len(teams)
            )
        except MSTeamsAuthError as e:
            return MSTeamsConnectionStatus(
                connected=False,
                message=f"Authentication failed: {str(e)}"
            )
        except MSTeamsAPIError as e:
            return MSTeamsConnectionStatus(
                connected=False,
                message=f"API error: {str(e)}"
            )
        except Exception as e:
            return MSTeamsConnectionStatus(
                connected=False,
                message=f"Connection failed: {str(e)}"
            )

    def list_teams(self) -> List[TeamInfo]:
        """
        List all teams the app has access to.

        Returns:
            List of TeamInfo objects
        """
        response = self._make_request("GET", "/teams")
        teams = []

        for team_data in response.get("value", []):
            teams.append(TeamInfo(
                id=team_data["id"],
                display_name=team_data.get("displayName", ""),
                description=team_data.get("description"),
                visibility=team_data.get("visibility"),
                created_datetime=team_data.get("createdDateTime")
            ))

        return teams

    def get_team(self, team_id: str) -> TeamInfo:
        """
        Get information about a specific team.

        Args:
            team_id: The team ID

        Returns:
            TeamInfo object
        """
        response = self._make_request("GET", f"/teams/{team_id}")

        return TeamInfo(
            id=response["id"],
            display_name=response.get("displayName", ""),
            description=response.get("description"),
            visibility=response.get("visibility"),
            created_datetime=response.get("createdDateTime")
        )

    def list_channels(self, team_id: str) -> List[ChannelInfo]:
        """
        List all channels in a team.

        Args:
            team_id: The team ID

        Returns:
            List of ChannelInfo objects
        """
        response = self._make_request("GET", f"/teams/{team_id}/channels")
        channels = []

        for channel_data in response.get("value", []):
            channels.append(ChannelInfo(
                id=channel_data["id"],
                display_name=channel_data.get("displayName", ""),
                description=channel_data.get("description"),
                membership_type=channel_data.get("membershipType"),
                web_url=channel_data.get("webUrl")
            ))

        return channels

    def get_channel(self, team_id: str, channel_id: str) -> ChannelInfo:
        """
        Get information about a specific channel.

        Args:
            team_id: The team ID
            channel_id: The channel ID

        Returns:
            ChannelInfo object
        """
        response = self._make_request("GET", f"/teams/{team_id}/channels/{channel_id}")

        return ChannelInfo(
            id=response["id"],
            display_name=response.get("displayName", ""),
            description=response.get("description"),
            membership_type=response.get("membershipType"),
            web_url=response.get("webUrl")
        )

    def list_channel_messages(
        self,
        team_id: str,
        channel_id: str,
        top: int = 20,
        order_by: str = "createdDateTime desc"
    ) -> List[MessageInfo]:
        """
        List messages in a channel.

        Args:
            team_id: The team ID
            channel_id: The channel ID
            top: Maximum number of messages to return (default 20)
            order_by: Sort order (default newest first)

        Returns:
            List of MessageInfo objects
        """
        params = {
            "$top": top,
            "$orderby": order_by
        }

        response = self._make_request(
            "GET",
            f"/teams/{team_id}/channels/{channel_id}/messages",
            params=params
        )

        messages = []
        for msg_data in response.get("value", []):
            from_data = msg_data.get("from", {})
            user_data = from_data.get("user", {})

            messages.append(MessageInfo(
                id=msg_data["id"],
                created_datetime=msg_data.get("createdDateTime", ""),
                body_content=msg_data.get("body", {}).get("content", ""),
                body_content_type=msg_data.get("body", {}).get("contentType", "text"),
                from_user=user_data.get("displayName"),
                from_user_id=user_data.get("id"),
                subject=msg_data.get("subject"),
                importance=msg_data.get("importance"),
                web_url=msg_data.get("webUrl"),
                attachments=msg_data.get("attachments", []),
                mentions=msg_data.get("mentions", []),
                reactions=msg_data.get("reactions", [])
            ))

        return messages

    def get_message(
        self,
        team_id: str,
        channel_id: str,
        message_id: str
    ) -> MessageInfo:
        """
        Get a specific message from a channel.

        Args:
            team_id: The team ID
            channel_id: The channel ID
            message_id: The message ID

        Returns:
            MessageInfo object
        """
        response = self._make_request(
            "GET",
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}"
        )

        from_data = response.get("from", {})
        user_data = from_data.get("user", {})

        return MessageInfo(
            id=response["id"],
            created_datetime=response.get("createdDateTime", ""),
            body_content=response.get("body", {}).get("content", ""),
            body_content_type=response.get("body", {}).get("contentType", "text"),
            from_user=user_data.get("displayName"),
            from_user_id=user_data.get("id"),
            subject=response.get("subject"),
            importance=response.get("importance"),
            web_url=response.get("webUrl"),
            attachments=response.get("attachments", []),
            mentions=response.get("mentions", []),
            reactions=response.get("reactions", [])
        )

    def send_channel_message(
        self,
        team_id: str,
        channel_id: str,
        content: str,
        content_type: str = "html",
        subject: Optional[str] = None,
        importance: str = "normal"
    ) -> MessageInfo:
        """
        Send a message to a channel.

        Args:
            team_id: The team ID
            channel_id: The channel ID
            content: Message content (can be HTML or text)
            content_type: Content type ("html" or "text")
            subject: Optional message subject
            importance: Message importance ("normal", "high", "urgent")

        Returns:
            MessageInfo of the created message
        """
        data = {
            "body": {
                "contentType": content_type,
                "content": content
            },
            "importance": importance
        }

        if subject:
            data["subject"] = subject

        response = self._make_request(
            "POST",
            f"/teams/{team_id}/channels/{channel_id}/messages",
            data=data
        )

        from_data = response.get("from", {})
        user_data = from_data.get("user", {})

        return MessageInfo(
            id=response["id"],
            created_datetime=response.get("createdDateTime", ""),
            body_content=response.get("body", {}).get("content", ""),
            body_content_type=response.get("body", {}).get("contentType", "text"),
            from_user=user_data.get("displayName"),
            from_user_id=user_data.get("id"),
            subject=response.get("subject"),
            importance=response.get("importance"),
            web_url=response.get("webUrl")
        )

    def reply_to_message(
        self,
        team_id: str,
        channel_id: str,
        message_id: str,
        content: str,
        content_type: str = "html"
    ) -> MessageInfo:
        """
        Reply to a message in a channel.

        Args:
            team_id: The team ID
            channel_id: The channel ID
            message_id: The parent message ID to reply to
            content: Reply content
            content_type: Content type ("html" or "text")

        Returns:
            MessageInfo of the reply message
        """
        data = {
            "body": {
                "contentType": content_type,
                "content": content
            }
        }

        response = self._make_request(
            "POST",
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies",
            data=data
        )

        from_data = response.get("from", {})
        user_data = from_data.get("user", {})

        return MessageInfo(
            id=response["id"],
            created_datetime=response.get("createdDateTime", ""),
            body_content=response.get("body", {}).get("content", ""),
            body_content_type=response.get("body", {}).get("contentType", "text"),
            from_user=user_data.get("displayName"),
            from_user_id=user_data.get("id")
        )

    def list_message_replies(
        self,
        team_id: str,
        channel_id: str,
        message_id: str,
        top: int = 20
    ) -> List[MessageInfo]:
        """
        List replies to a message.

        Args:
            team_id: The team ID
            channel_id: The channel ID
            message_id: The parent message ID
            top: Maximum number of replies to return

        Returns:
            List of MessageInfo objects
        """
        params = {"$top": top}

        response = self._make_request(
            "GET",
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies",
            params=params
        )

        replies = []
        for reply_data in response.get("value", []):
            from_data = reply_data.get("from", {})
            user_data = from_data.get("user", {})

            replies.append(MessageInfo(
                id=reply_data["id"],
                created_datetime=reply_data.get("createdDateTime", ""),
                body_content=reply_data.get("body", {}).get("content", ""),
                body_content_type=reply_data.get("body", {}).get("contentType", "text"),
                from_user=user_data.get("displayName"),
                from_user_id=user_data.get("id")
            ))

        return replies


# Convenience functions for direct tool usage

def verify_msteams_connection() -> Dict[str, Any]:
    """
    Verify MS Teams connection status.

    Returns:
        Dictionary with connection status and details
    """
    api = MSTeamsAPI()
    status = api.verify_connection()

    return {
        "connected": status.connected,
        "message": status.message,
        "teams_count": status.teams_count
    }


def list_msteams_teams() -> Dict[str, Any]:
    """
    List all accessible Teams.

    Returns:
        Dictionary with list of teams
    """
    api = MSTeamsAPI()
    teams = api.list_teams()

    return {
        "teams": [
            {
                "id": t.id,
                "display_name": t.display_name,
                "description": t.description,
                "visibility": t.visibility
            }
            for t in teams
        ],
        "count": len(teams)
    }


def list_msteams_channels(team_id: str) -> Dict[str, Any]:
    """
    List channels in a team.

    Args:
        team_id: The team ID

    Returns:
        Dictionary with list of channels
    """
    api = MSTeamsAPI()
    channels = api.list_channels(team_id)

    return {
        "channels": [
            {
                "id": c.id,
                "display_name": c.display_name,
                "description": c.description,
                "membership_type": c.membership_type,
                "web_url": c.web_url
            }
            for c in channels
        ],
        "count": len(channels)
    }


def read_msteams_messages(
    team_id: str,
    channel_id: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Read messages from a channel.

    Args:
        team_id: The team ID
        channel_id: The channel ID
        limit: Maximum messages to return

    Returns:
        Dictionary with list of messages
    """
    api = MSTeamsAPI()
    messages = api.list_channel_messages(team_id, channel_id, top=limit)

    return {
        "messages": [
            {
                "id": m.id,
                "created_datetime": m.created_datetime,
                "from_user": m.from_user,
                "subject": m.subject,
                "body_content": m.body_content,
                "body_content_type": m.body_content_type,
                "importance": m.importance,
                "web_url": m.web_url,
                "attachments_count": len(m.attachments),
                "mentions_count": len(m.mentions),
                "reactions_count": len(m.reactions)
            }
            for m in messages
        ],
        "count": len(messages)
    }


def send_msteams_message(
    team_id: str,
    channel_id: str,
    content: str,
    subject: Optional[str] = None,
    importance: str = "normal"
) -> Dict[str, Any]:
    """
    Send a message to a channel.

    Args:
        team_id: The team ID
        channel_id: The channel ID
        content: Message content (HTML supported)
        subject: Optional message subject
        importance: Message importance

    Returns:
        Dictionary with created message details
    """
    api = MSTeamsAPI()
    message = api.send_channel_message(
        team_id=team_id,
        channel_id=channel_id,
        content=content,
        subject=subject,
        importance=importance
    )

    return {
        "success": True,
        "message_id": message.id,
        "created_datetime": message.created_datetime,
        "web_url": message.web_url
    }


def reply_to_msteams_message(
    team_id: str,
    channel_id: str,
    message_id: str,
    content: str
) -> Dict[str, Any]:
    """
    Reply to a message in a channel.

    Args:
        team_id: The team ID
        channel_id: The channel ID
        message_id: The message to reply to
        content: Reply content

    Returns:
        Dictionary with reply details
    """
    api = MSTeamsAPI()
    reply = api.reply_to_message(
        team_id=team_id,
        channel_id=channel_id,
        message_id=message_id,
        content=content
    )

    return {
        "success": True,
        "reply_id": reply.id,
        "created_datetime": reply.created_datetime
    }
