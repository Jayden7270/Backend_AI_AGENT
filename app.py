from flask import Flask, request, jsonify, make_response
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from github import Github
import os
from dotenv import load_dotenv
import logging
from services.github_service import GitHubService
from services.code_analyzer import CodeAnalyzer

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
flask_app = Flask(__name__)

# Slack 앱 초기화
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

handler = SlackRequestHandler(slack_app)
github_service = GitHubService()
code_analyzer = CodeAnalyzer()

@slack_app.event("message")
def handle_message(body, say):
    """메시지 이벤트 처리"""
    try:
        message = body["event"]["text"]
        thread_ts = body["event"].get("thread_ts", None)
        
        # GitHub 토큰이 없는 경우 연동 요청
        if not github_service.has_token():
            say("먼저 GitHub 계정을 연동해주세요. `/connect-github` 명령어를 사용해주세요.")
            return

        # 레포지토리 문의
        if "레포지토리" in message or "repo" in message.lower():
            repos = github_service.get_repositories()
            repo_list = "\n".join([f"- {repo.name}" for repo in repos])
            say(f"다음 레포지토리들이 있습니다:\n{repo_list}\n\n어떤 레포지토리를 확인하시겠습니까?")
            return

        # 기능 구현 여부 문의
        if "구현" in message or "기능" in message:
            # 컨텍스트에서 레포지토리 정보 가져오기
            repo_name = github_service.get_current_repo()
            if not repo_name:
                say("먼저 확인하실 레포지토리를 알려주세요.")
                return

            # 코드 분석
            files = github_service.get_potential_files(repo_name, message)
            if not files:
                say("해당 기능이 구현되어 있을 만한 파일을 찾지 못했습니다.")
                return

            # 파일 내용 분석
            analysis_result = code_analyzer.analyze_files(files, message)
            say(f"분석 결과:\n{analysis_result}")

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        say("죄송합니다. 오류가 발생했습니다.")

@slack_app.command("/connect-github")
def handle_github_connect(ack, body, respond):
    """GitHub 연동 명령어 처리"""
    try:
        ack()
        oauth_url = github_service.get_oauth_url()
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
    except Exception as e:
        logger.error(f"Error in handle_github_connect: {str(e)}")
        respond({"text": "GitHub 연동 중 오류가 발생했습니다."})

@flask_app.route("/slack/events", methods=["POST", "GET"])
def slack_events():
    """Slack 이벤트 처리"""
    if request.method == "GET":
        return "Hello! This endpoint is for Slack events.", 200

    try:
        return handler.handle(request)
    except Exception as e:
        logger.error(f"Error handling slack event: {str(e)}")
        return make_response(str(e), 500)

if __name__ == "__main__":
    logger.info("Starting Flask application")
    flask_app.run(debug=True, port=5000)