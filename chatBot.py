# chatBot.py
import os
from openai import OpenAI
from openai import RateLimitError, OpenAIError
import fixed_values
from dotenv import load_dotenv
import markdown
import json
import ast

load_dotenv()

client = OpenAI()

client.api_key = os.environ.get("OPENAI_API_KEY")


class ChatBot:
    content = {
        1: "You are an experienced Quality Analyst, you will be asked some doubts, related to Quality testing. ",  # doubt
        2: "You are an experienced quality analyst. You will be provided functionality later, you have to generate as many as test cases. Each test case should include the following fields: Test case description, Prerequisites, Step number, Step description, Expected results, and Validations. Write them in number list and step number in 'a,b,c,d....'. Strictly use the given field names and don't used bold, italic texts",  # testcase
        3: "You are an experienced Quality Analyst, you will be asked to generate selenium with java code for the user story provided.",  # automation code: java
        4: "You are an experienced Quality Analyst, you will be asked to generate selenium with python code for the user story provided.",  # automation code: python
        5: "You are a helpful assistant.",  # other
    }

    def __init__(self):
        self.msg = []

    def set_message(self, option):
        content = self.content.get(option, "You are a helpful assistant.")
        self.msg = [{"role": "system", "content": content}]

    def normalize_previous_response(self, prev_response):
        if not prev_response or str(prev_response).lower() in ["none", "null"]:
            return None
        return {"role": prev_response.role, "content": prev_response.content}

    def get_response(self, user_message, option, prev_response):
        self.set_message(option)

        self.previous_response = self.normalize_previous_response(prev_response)
        
        messages = self.msg.copy()
        
        if self.previous_response:
            messages.append(self.previous_response)
        messages.append({"role": "user", "content": user_message})
        try:

            request_kwargs = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": fixed_values.TEMPERATURE,
                "max_tokens": fixed_values.MAX_TOKENS,
            }

            response = client.chat.completions.create(**request_kwargs)
            self.previous_response = response.choices[0].message
            self.reply = response.choices[0].message.content
            self.msg.append({"role": "assistant", "content": self.reply})
            self.html_reply = markdown.markdown(self.reply)
            return (
                (self.reply, self.previous_response)
                if option == 2
                else (self.html_reply, self.previous_response)
            )
        except RateLimitError:
            return (
                "<p>The system is experiencing high traffic, please try again later.</p>",
                None,
            )
        except OpenAIError as e:
            return (
                f"<p>An error occurred while generating the response: {str(e)}</p>",
                None,
            )
        except Exception as e:
            return f"<p>An unexpected error occurred: {str(e)}</p>", None

    # def get_stream_of_response(self, user_message, option):
    #     self.set_message(option)
    #     self.msg.append({"role": "user", "content": user_message})

    #     try:
    #         response = client.chat.completions.create(
    #             model="gpt-3.5-turbo",
    #             messages=self.msg,
    #             temperature=fixed_values.TEMPERATURE,
    #             max_tokens=fixed_values.MAX_TOKENS,
    #         )

    #         self.reply = response.choices[0].message.content
    #         self.msg.append({"role": "assistant", "content": self.reply})
    #         self.html_reply = markdown.markdown(self.reply)
    #         if option == 2:
    #             return self.reply
    #         else:
    #             return self.html_reply
    #     except RateLimitError:
    #         return "<p>The system is experiencing high traffic, please try again later.</p>"
    #     except OpenAIError as e:
    #         return f"<p>An error occurred while generating the response: {str(e)}</p>"
    #     except Exception as e:
    #         return f"<p>An unexpected error occurred: {str(e)}</p>"


#         [
#     {
#         "index": 0,
#         "message": {
#             "role": "assistant",
#             "content": "Under the soft glow of the moon, Luna the unicorn danced through fields of twinkling stardust, leaving trails of dreams for every child asleep.",
#             "refusal": null
#         },
#         "logprobs": null,
#         "finish_reason": "stop"
#     }
# ]
