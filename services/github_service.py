from github import Github
import os
from typing import List
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.github = None
        self.token = None

    def has_token(self) -> bool:
        """GitHub 토큰 존재 여부 확인"""
        return bool(self.token)

    def set_token(self, token: str):
        """GitHub 토큰 설정"""
        self.token = token
        self.github = Github(token)

    def get_oauth_url(self) -> str:
        """GitHub OAuth URL 생성"""
        client_id = os.environ.get("GITHUB_CLIENT_ID")
        return f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo"

    def get_repositories(self) -> List:
        """사용자의 레포지토리 목록 조회"""
        if not self.github:
            raise Exception("GitHub 토큰이 설정되지 않았습니다.")
        return list(self.github.get_user().get_repos())

    def get_potential_files(self, repo_name: str, feature_description: str) -> List:
        """기능이 구현되어 있을 만한 파일 목록 조회"""
        if not self.github:
            raise Exception("GitHub 토큰이 설정되지 않았습니다.")

        repo = self.github.get_repo(repo_name)
        contents = repo.get_contents("")
        potential_files = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                if self._is_potential_file(file_content.name, feature_description):
                    potential_files.append(file_content)

        return potential_files[:20]  # 최대 20개 파일만 반환

    def _is_potential_file(self, filename: str, feature_description: str) -> bool:
        """파일이 해당 기능을 포함할 가능성이 있는지 확인"""
        # 파일 확장자 체크
        valid_extensions = ['.py', '.js', '.java', '.cpp', '.cs', '.php']
        if not any(filename.endswith(ext) for ext in valid_extensions):
            return False

        # 파일명과 기능 설명의 연관성 체크
        keywords = feature_description.lower().split()
        filename_lower = filename.lower()
        
        return any(keyword in filename_lower for keyword in keywords) 