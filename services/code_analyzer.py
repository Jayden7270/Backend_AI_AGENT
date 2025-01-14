from typing import List
import logging
from services.gpt_service import GPTService

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    def __init__(self):
        self.gpt_service = GPTService()

    def analyze_files(self, files: List, feature_description: str) -> str:
        """파일들의 코드를 분석하여 기능 구현 여부 확인"""
        try:
            # 파일 데이터 준비
            file_data = []
            for file in files:
                try:
                    content = file.decoded_content.decode('utf-8')
                    file_data.append({
                        'path': file.path,
                        'content': content
                    })
                except Exception as e:
                    logger.error(f"Error processing file {file.path}: {str(e)}")
                    continue

            if not file_data:
                return "분석할 파일이 없습니다."

            # GPT 서비스를 통한 코드 분석
            analysis = self.gpt_service.analyze_repository(file_data)
            return analysis

        except Exception as e:
            logger.error(f"Error in analyze_files: {str(e)}")
            return f"코드 분석 중 오류가 발생했습니다: {str(e)}" 