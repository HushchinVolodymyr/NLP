import os
import sys

from openai import OpenAI
from dotenv import load_dotenv

from database.engine import session
from database.entitys import Feed


class Assistant:
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        self.client = OpenAI(api_key=self.API_KEY)
        self.session = session
        self.history = []
        self.training()

    def open_ai_response(self, context, data = None) -> str:
        if data:
            if context:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Reply on ukrainian"},
                        {"role": "system", "content": f"Наявні товари: {data}"},
                        {"role": "user", "content": str(context)}
                    ]
                )

                bot_response = response.choices[0].message.content

                return f"Ассистент: {bot_response}"
            else:
                return "Ассистент: Я готов помочь. Чем могу быть полезен?"
        else:
            if context:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Reply on ukrainian"},
                        {"role": "user", "content": str(context)}
                    ]
                )

                bot_response = response.choices[0].message.content

                return f"Ассистент: {bot_response}"
            else:
                return "Ассистент: Я готов помочь. Чем могу быть полезен?"

    def training(self):
        feeds_obj = self.session.query(Feed).all()
        feeds = ""
        for i, feed in enumerate(feeds_obj, 1):
            feed_info = (f"{i}. {feed.name}\n"
                         f"   Ціна: {feed.price} грн\n"
                         f"   Тип: {feed.type}\n"
                         f"   Представлено для: {feed.pet}\n")
            feeds += feed_info + "\n"


        training_text = (f"Привіт, ти ассистент для магазину з продажу корму.\n"
                         f"Ось тобі база наявних кормів:\n{feeds}\n"
                         f"Ти маєш інформувати покупців про наявні товари, їх ціну та для кого вони підходять.")

        self.history.append(training_text)
        AI_response = self.open_ai_response(training_text)

        return AI_response

    def run(self):
        feeds_obj = self.session.query(Feed).all()
        feeds = ""
        for i, feed in enumerate(feeds_obj, 1):
            feed_info = (f"{i}. {feed.name}\n"
                         f"   Ціна: {feed.price} грн\n"
                         f"   Тип: {feed.type}\n"
                         f"   Представлено для: {feed.pet}\n")
            feeds += feed_info + "\n"

        while True:
            user_input = input("Покупець: ")

            if user_input.lower() in ["вихід", "до побачення", "гарного дня"]:
                print("Ассистент: До побачення! Гарного дня!")
                sys.exit(0)

            if user_input:
                context = "\n".join(self.history + [f"Покупець: {user_input}"])
                response = self.open_ai_response(context, feeds)
                self.history.append(f"Покупець: {user_input}")
                self.history.append(response)

                print(response)


if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("OPEN_AI_API_KEY")
    assistant = Assistant(API_KEY)
    assistant.run()
