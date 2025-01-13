import json
import os
from typing import Optional, Dict
from datetime import datetime
import threading

class FileStorageService:
    def __init__(self, storage_file: str = "data/tokens.json"):
        self.storage_file = storage_file
        self.lock = threading.Lock()  # 동시성 제어를 위한 락
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """저장소 파일과 디렉토리가 존재하는지 확인하고 생성합니다"""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        if not os.path.exists(self.storage_file):
            self._save_data({})
    
    def _load_data(self) -> Dict:
        """저장소에서 데이터를 로드합니다"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_data(self, data: Dict):
        """데이터를 저장소에 저장합니다"""
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_github_token(self, slack_user_id: str, github_token: str):
        """GitHub 토큰을 저장합니다"""
        with self.lock:
            data = self._load_data()
            data[slack_user_id] = {
                'github_token': github_token,
                'updated_at': datetime.utcnow().isoformat()
            }
            self._save_data(data)
    
    def get_github_token(self, slack_user_id: str) -> Optional[str]:
        """GitHub 토큰을 조회합니다"""
        with self.lock:
            data = self._load_data()
            user_data = data.get(slack_user_id)
            return user_data.get('github_token') if user_data else None
    
    def delete_github_token(self, slack_user_id: str):
        """GitHub 토큰을 삭제합니다"""
        with self.lock:
            data = self._load_data()
            if slack_user_id in data:
                del data[slack_user_id]
                self._save_data(data) 