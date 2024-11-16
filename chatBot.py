# chatBot.py
import os
import openai
from openai import RateLimitError, OpenAIError
import fixed_values
from dotenv import load_dotenv
import markdown

load_dotenv()

openai.api_key = os.environ.get('OPENAI_KEY')

class ChatBot:
    content = {
        1: 'You are an experienced Quality Analyst, you will be asked some doubts, related to Quality testing. ',  # doubt
        2: "You are an experienced quality analyst. You will be provided functionality later, you have to generate as many as test cases. Each test case should include the following fields: Test case description, Prerequisites, Step number, Step description, Expected results, and Validations. Write them in number list and step number in 'a,b,c,d....'. Strictly use the given field names and don't used bold, italic texts",  # testcase
        3: 'You are an experienced Quality Analyst, you will be asked to generate selenium with java code for the user story provided.',  # automation code: java
        4: 'You are an experienced Quality Analyst, you will be asked to generate selenium with python code for the user story provided.',  # automation code: python
        5: 'You are a helpful assistant.'  # other
    }

    def __init__(self):
        self.msg = []

    def set_message(self, option):
        content = self.content.get(option, 'You are a helpful assistant.')
        self.msg = [{"role": "system", "content": content}]

    def get_response(self, user_message, option):
        self.set_message(option)
        self.msg.append({"role": "user", "content": user_message})
        
        try: 
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.msg,
                temperature=fixed_values.TEMPERATURE,
                max_tokens=fixed_values.MAX_TOKENS,
            )

            self.reply = response.choices[0].message.content
            self.msg.append({"role": "assistant", "content": self.reply})
            self.html_reply = markdown.markdown(self.reply)
            if option == 2:
                return self.reply
            else:
                return self.html_reply
        except RateLimitError:
            return "<p>The system is experiencing high traffic, please try again later.</p>"
        except OpenAIError as e:
            return f"<p>An error occurred while generating the response: {str(e)}</p>"
        except Exception as e:
            return f"<p>An unexpected error occurred: {str(e)}</p>"
