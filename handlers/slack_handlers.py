from slack_bolt import App
import secrets
import json
import os
from datetime import datetime
from typing import Optional

class StateStore:
    def __init__(self, file_path: str = "data/states.json"):
        self.file_path = file_path
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """상태 저장 파일이 존재하는지 확인하고 생성"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._save_states({})
    
    def _load_states(self):
        """상태 데이터 로드"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_states(self, states):
        """상태 데이터 저장"""
        with open(self.file_path, 'w') as f:
            json.dump(states, f, indent=2)
    
    def set(self, state: str, user_id: str):
        """상태 토큰과 유저 ID 매핑 저장"""
        states = self._load_states()
        states[state] = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat()
        }
        self._save_states(states)
    
    def get(self, state: str) -> str:
        """상태 토큰으로 유저 ID 조회"""
        states = self._load_states()
        state_data = states.get(state)
        if state_data:
            # 사용된 상태 토큰 삭제 (일회성)
            del states[state]
            self._save_states(states)
            return state_data.get('user_id')
        return None

def create_slack_handlers(slack_app: App, github_auth_service):
    """Slack 핸들러들을 생성하고 등록합니다"""
    
    @slack_app.command("/connect-github")
    def handle_github_connect(ack, body, respond):
        ack()
        state = secrets.token_urlsafe(16)
        
        # 상태와 슬랙 유저 ID를 파일에 저장
        state_store.set(state, body["user_id"])
        
        # GitHub OAuth URL 생성
        oauth_url = github_auth_service.get_oauth_url(state)
        
        # 슬랙에 버튼 메시지 전송
        respond({
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "GitHub 계정을 연결하려면 아래 버튼을 클릭하세요:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "GitHub 연동하기"
                            },
                            "url": oauth_url,
                            "action_id": "github_connect"
                        }
                    ]
                }
            ]
        })

    @slack_app.route("/github/callback")
    def handle_github_callback(request):
        # GitHub로부터의 콜백 처리
        code = request.args.get('code')
        state = request.args.get('state')
        
        # 상태 토큰 검증
        slack_user_id = state_store.get(state)
        if not slack_user_id:
            return "Invalid state token", 400
        
        # 코드를 토큰으로 교환하고 저장
        github_token = github_auth_service.exchange_code_for_token(code, slack_user_id)
        
        # 사용자에게 성공 메시지 전송
        app.client.chat_postMessage(
            channel=slack_user_id,
            text="GitHub 계정이 성공적으로 연동되었습니다! 이제 `/analyze` 명령어를 사용할 수 있습니다."
        )
        
        return "GitHub 연동이 완료되었습니다. 이 창은 닫으셔도 됩니다.", 200

    @slack_app.command("/analyze")
    def handle_analyze(ack, body, respond):
        ack()
        repo = body["text"]  # 예: "owner/repo"
        user_id = body["user_id"]
        
        # GitHub 토큰 조회
        token = db_service.get_github_token(user_id)
        if not token:
            respond("먼저 GitHub 계정을 연결해주세요. `/connect-github` 명령어를 사용하세요.")
            return
        
        respond("레포지토리를 분석 중입니다...")
        
        try:
            # 관련 파일 찾기
            files = github_service.get_relevant_files(repo, token, ["payment", "billing"])
            
            # GPT 분석 요청
            analysis = gpt_service.analyze_repository(files)
            
            # 결과 응답
            respond(f"분석 결과:\n{analysis}")
        except Exception as e:
            respond(f"분석 중 오류가 발생했습니다: {str(e)}") 

    return slack_app 