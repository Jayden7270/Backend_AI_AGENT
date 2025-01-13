import requests
from urllib.parse import urlencode
import os
from .storage_service import FileStorageService

class GitHubAuthService:
    def __init__(self):
        self.client_id = os.getenv('GITHUB_CLIENT_ID')
        self.client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GITHUB_REDIRECT_URI')
        self.storage = FileStorageService()

    def get_oauth_url(self, state: str) -> str:
        """GitHub OAuth URL을 생성합니다"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'repo',
            'state': state
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code: str, slack_user_id: str) -> str:
        """Authorization Code를 Access Token으로 교환하고 저장합니다"""
        response = requests.post(
            'https://github.com/login/oauth/access_token',
            headers={'Accept': 'application/json'},
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code
            }
        )
        
        token = response.json().get('access_token')
        if token:
            self.storage.save_github_token(slack_user_id, token)
        return token

    def get_user_token(self, slack_user_id: str) -> str:
        """사용자의 GitHub 토큰을 조회합니다"""
        return self.storage.get_github_token(slack_user_id) 