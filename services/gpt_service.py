from openai import OpenAI
from typing import List, Dict

class GPTService:
    def __init__(self):
        self.client = OpenAI()
    
    def analyze_repository(self, files: List[Dict]) -> str:
        # 파일 내용을 하나의 문맥으로 결합
        context = self._prepare_context(files)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                # Updated system prompt with detailed instructions
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specialized in reading code, determining whether certain features "
                        "have been implemented, and providing expert-level code feedback. You have access to relevant "
                        "code snippets or entire code files. Your job is to:\n\n"
                        "1. Identify whether a feature request or specification is implemented in the provided code.\n"
                        "2. Summarize the findings accurately.\n"
                        "3. Provide constructive, clear, and actionable feedback on how to improve the code, if necessary.\n\n"
                        "When responding, follow this structure:\n"
                        "1) Implementation Status: Is the feature fully implemented, partially, or not at all?\n"
                        "2) Detailed Explanation: Summarize the relevant parts of the code or logic.\n"
                        "3) Feedback / Suggestions: Provide concise tips for improvement.\n\n"
                        "Be concise but thorough, and stay within the provided code context. Use a professional tone, "
                        "and if anything is ambiguous, highlight what is missing. Avoid speculation beyond the given snippets."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"다음 코드들을 분석하여 기의 구현 여부와 구현 상태를 설명해주세요.\n\n{context}"
                    )
                }
            ]
        )
        
        return response.choices[0].message.content
    
    def _prepare_context(self, files: List[Dict]) -> str:
        context = []
        for file in files:
            content = f"File: {file['path']}\n```\n{file['content']}\n```\n"
            context.append(content)
        return "\n".join(context)