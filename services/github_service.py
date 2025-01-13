import requests
from typing import List, Dict

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
    
    def get_oauth_url(self, state: str) -> str:
        return f"https://github.com/login/oauth/authorize?client_id={os.getenv('GITHUB_CLIENT_ID')}&state={state}&scope=repo"
    
    def exchange_code_for_token(self, code: str) -> str:
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "code": code
            }
        )
        return response.json().get("access_token")
    
    def get_relevant_files(self, repo: str, token: str, keywords: List[str]) -> List[Dict]:
        files = []
        self._traverse_repo(repo, "", token, files, keywords)
        return files[:20]  # 최대 20개 파일로 제한
    
    def _traverse_repo(self, repo: str, path: str, token: str, files: List, keywords: List[str]):
        url = f"{self.base_url}/repos/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        
        for item in response.json():
            if item["type"] == "file":
                if any(keyword in item["path"].lower() for keyword in keywords):
                    files.append(item)
            elif item["type"] == "dir":
                self._traverse_repo(repo, item["path"], token, files, keywords) 