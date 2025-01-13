from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from services.github_auth_service import GitHubAuthService
import os
from dotenv import load_dotenv
import secrets

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
flask_app = Flask(__name__)

# Slack 앱 초기화
slack_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

handler = SlackRequestHandler(slack_app)

# GitHub 인증 서비스 초기화
github_auth_service = GitHubAuthService()

# Slack 커맨드 핸들러
@slack_app.command("/connect-github")
def handle_github_connect(ack, body, respond):
    ack()
    state = secrets.token_urlsafe(16)
    oauth_url = github_auth_service.get_oauth_url(state)
    
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

# Flask 라우트 핸들러
@flask_app.route("/github/callback", methods=["GET"])
def handle_github_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return "Authorization code not found", 400
    
    try:
        github_token = github_auth_service.exchange_code_for_token(code)
        return "GitHub 연동이 완료되었습니다. 이 창은 닫으셔도 됩니다.", 200
    except Exception as e:
        return f"Authentication failed: {str(e)}", 400

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(port=5000, debug=True) 