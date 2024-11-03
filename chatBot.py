# chatBot.py
import os
import openai
from openai import RateLimitError, OpenAIError
import fixed_values
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ['OPENAI_KEY']

class ChatBot:
    content = {
        1: 'You are an experienced Quality Analyst, you will be asked some doubts, related to Quality testing.',
        2: "You are an experienced quality analyst. You will be provided functionality later...",
        3: 'You are an experienced Quality Analyst, you will be asked to generate selenium with java code for the user story provided.',
        4: 'You are an experienced Quality Analyst, you will be asked to generate selenium with python code for the user story provided.',
        5: 'You are a helpful assistant.'
    }

    def __init__(self):
        self.msg = []

    def set_message(self, option):
        content = self.content.get(option, 'You are a helpful assistant.')
        self.msg = [{"role": "system", "content": content}]

    def get_response(self, user_message, option):
        self.set_message(option)
        self.msg.append({"role": "user", "content": user_message})

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.msg,
            temperature=fixed_values.TEMPERATURE,
            max_tokens=fixed_values.MAX_TOKENS,
        )

        reply = response.choices[0].message.content
        self.msg.append({"role": "assistant", "content": reply})
        return reply
