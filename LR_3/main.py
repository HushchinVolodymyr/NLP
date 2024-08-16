import sys

from database.engine import session
from database.entitys import Feed, Order

import spacy
from spacy.tokens import Doc
from spacy.language import Language

import random


@Language.component("custom_intent_component")
def custom_intent_component(doc):
    intents = {
        "feed_request": any(token.lemma_ in ["їжа", "корм", "товари", "корми"] for token in doc),
        "gipo_request": any(token.lemma_ in ["гіпоалергенний", "алергік", "алергія"] for token in doc),
        "default_request": any(token.lemma_ in ["звичайний"] for token in doc),
        "price_request": any(token.lemma_ in ["ціна", "вартість"] for token in doc),
        "order": any(token.lemma_ in ["замовлення"] for token in doc),
        "dog_feed_request": any(token.lemma_ in ["собака", "собаки"] for token in doc),
        "cat_feed_request": any(token.lemma_ in ["кіт", "коти", "кота"] for token in doc),
    }
    doc._.intents = intents
    return doc


Doc.set_extension("intents", default={}, force=True)

GREETINGS = [
    "Привіт! Як я можу допомогти вам сьогодні?",
    "Добрий день! Чим можу бути корисним?",
    "Вітаю! Що вас цікавить?",
    "Здрастуйте! Чим можу допомогти?",
    "Привіт! Як я можу вам допомогти?"
]

ERROR_MESSAGES = [
    "Виникла помилка. Будь ласка, спробуйте ще раз.",
    "На жаль, сталася помилка. Спробуйте знову.",
    "Упс, щось пішло не так. Повторіть, будь ласка, спробу.",
    "Сталася помилка. Будь ласка, повторіть запит.",
    "Вибачте, виникла помилка. Будь ласка, спробуйте пізніше."
]


class Assistant:
    def __init__(self) -> None:
        self.nlp = spacy.load('uk_core_news_lg')
        self.nlp.add_pipe("custom_intent_component", last=True)
        self.session = session
        self.state = "command_input"
        self.role = True
        self.greet()

    @staticmethod
    def greet():
        print(random.choice(GREETINGS))

    def run(self, text: str) -> str:
        doc = self.nlp(text)
        intents = doc._.intents

        if self.state == "command_input":
            if intents["gipo_request"]:
                if intents["dog_feed_request"]:
                    return self.get_feeds(pet="собака", feed_type="гіпоалергенний")
                elif intents["cat_feed_request"]:
                    return self.get_feeds(pet="кіт", feed_type="гіпоалергенний")
                else:
                    return self.get_feeds(feed_type="гіпоалергенний")

            if intents["default_request"]:
                if intents["dog_feed_request"]:
                    return self.get_feeds(pet="собака", feed_type="звичайний")
                elif intents["cat_feed_request"]:
                    return self.get_feeds(pet="кіт", feed_type="звичайний")
                else:
                    return self.get_feeds(feed_type="звичайний")

        if intents["price_request"]:
            return self.get_prices()

        if intents["dog_feed_request"]:
            return self.get_feeds(pet="собака")

        if intents["cat_feed_request"]:
            return self.get_feeds(pet="кіт")

        if intents["feed_request"]:
            return self.get_feeds()

        if intents["order"]:
            if self.role:
                return self.get_orders()
            else:
                return self.proccess_order(text)
        else:
            return "Не вдалося визначити ваш запит. Спробуйте знову."

    def proccess_order(self, user_input: str):
        doc = self.nlp(user_input)
        feed_order = []

        for token in doc:
            if token.text.lower() in ["бріт", "віскас", "фелікс"]:
                index = token.i
                feed = token.text

                if index + 1 < len(doc) and doc[index + 1].text.lower() in ["помаранчевий", "синій", "зелений"]:
                    feed += " " + doc[index + 1].text

                feed_id = self.get_feed_name_by_id(feed)
                if feed_id:
                    feed_order.append(feed_id)

        address = input("Введіть адресу доставки: ")

        order = Order(address=address, time=12345678)

        for feed_id in feed_order:
            feed = self.session.get(Feed, feed_id)
            if feed:
                order.feeds.append(feed)

        try:
            self.session.add(order)
            self.session.commit()
            print(f"Ваше замовлення:\nАдреса: {address}")
            for feed in order.feeds:
                print(f"  - {feed.name}\n")
            confirm = input("Підтвердити замовлення (так/ні): ")
            if confirm.lower() in ["так", "так"]:
                return "Замовлення отримано!"
            else:
                self.session.rollback()
                return "Ви відмінили замовлення!"
        except Exception as e:
            self.session.rollback()
            return random.choice(ERROR_MESSAGES)

    def get_feed_name_by_id(self, feed) -> object or None:
        feed_obj = self.session.query(Feed).filter_by(name=feed).first()
        if feed_obj:
            return feed_obj.id
        return None

    def get_orders(self):
        orders = self.session.query(Order).all()
        response_orders = ''
        for order in orders:
            response_orders += f"\nOrder ID: {order.id}\nАдреса: {order.address}\nFeeds:\n"
            for feed in order.feeds:
                response_orders += f"  - {feed.name}\n"
        return response_orders

    def get_prices(self):
        feeds = self.session.query(Feed).all()
        response_feeds = ''
        for feed in feeds:
            response_feeds += f"Name: {feed.name}, Price: {feed.price}\n"
        return response_feeds

    def get_feeds(self, pet=None, feed_type=None):
        query = self.session.query(Feed)
        if pet:
            query = query.filter_by(pet=pet)
        if feed_type:
            query = query.filter_by(type=feed_type)
        feeds = query.all()

        if feeds:
            response_feeds = ''
            for feed in feeds:
                response_feeds += f"Name: {feed.name}, Type: {feed.type}, Pet: {feed.pet}\n"
            return response_feeds
        else:
            return "Таких кормів немає в наявності."


if __name__ == '__main__':
    assistant = Assistant()
    while True:
        user_input = str(input("Введіть запит: "))

        if user_input in ["вихід", "гарного дня"]:
            print("Асистент: Гарного дня!")
            sys.exit(0)

        response = assistant.run(user_input)
        print("Асистент: {}".format(response))
