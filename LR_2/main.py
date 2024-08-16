from database.engine import session
from database.entitys import Feed, Order, OrderFeed

import spacy


class Assistant:
    def __init__(self):
        self.nlp = spacy.load('uk_core_news_lg')
        self.session = session
        self.state = "command_input"
        self.role = True

    def extract_intents(self, doc):
        intents = {
            "feed_request": any(token.lemma_ in ["їжа", "корм"] for token in doc),
            "gipo_request": any(token.lemma_ in ["гіпоалергенний", "алергік"] for token in doc),
            "default_request": any(token.lemma_ in ["звичайний"] for token in doc),
            "price_request": any(token.lemma_ in ["ціна", "вартість"] for token in doc),
            "order": any(token.lemma_ in ["замовлення"] for token in doc),
        }

        return intents

    def run(self, user_input: str):
        global input
        doc = self.nlp(user_input)
        # lemmatized_input = ' '.join([token.lemma_ for token in doc])
        intents = self.extract_intents(doc)

        if self.state == "command_input":
            if intents["gipo_request"]:
                return self.get_gipo_type()

            if intents["default_request"]:
                return self.get_def_type()

            if intents["price_request"]:
                return self.get_prices()

            if intents["feed_request"]:
                return self.get_feeds()

            if intents["order"]:
                if self.role:
                    return self.get_orders()
                else:
                    return self.proccess_order(user_input)

    def proccess_order(self, user_input: str):
        doc = self.nlp(user_input)
        feed_order = []

        for token in doc:
            if token.text.lower() in "бріт":
                index = token.i
                feed = token.text

                if doc[index + 1].text.lower() in ["помаранчевий", "синій", "зелений"]:
                    feed += " " + doc[index + 1].text

                    feed_id = self.get_feed_name_by_id(feed)
                    feed_order.append(feed_id)


            elif token.text.lower() in "віскас":
                index = token.i
                feed = token.text

                if doc[index + 1].text.lower() in ["помаранчевий", "синій", "зелений"]:
                    feed += " " + doc[index + 1].text

                    feed_id = self.get_feed_name_by_id(feed)
                    feed_order.append(feed_id)

            elif token.text.lower() in "фелікс":
                index = token.i
                feed = token.text

                if doc[index + 1].text.lower() in ["помаранчевий", "синій", "зелений"]:
                    feed += " " + doc[index + 1].text

                    feed_id = self.get_feed_name_by_id(feed)
                    feed_order.append(feed_id)

        address = input("Введіть адресу доставки: ")

        order = Order(address=address, time=12345678)

        for feed_id in feed_order:
            order.feeds.append(self.session.get(Feed, feed_id))

        print(f"Ваше замовлення:\nАдреса: {address}")
        for feed in order.feeds:
            print(f"  - {feed.name}\n")

        confirm = input("Підвердити замовлення (так/ні): ")

        if confirm.lower() in "так":
            self.session.add(order)

            self.session.commit()
            self.session.close()
            return "Замовлення отримано!"
        else:
            return "Ви відмінили замовлення!"

    def get_feed_name_by_id(self, feed):
        return session.query(Feed).filter_by(name=feed).first().id

    def get_orders(self):
        orders = session.query(Order).all()
        response_orders = ''

        for order in orders:
            response_orders += f"\nOrder ID: {order.id}" + "\nFeeds:\n"
            for feed in order.feeds:
                response_orders += f"  - {feed.name}\n"

        return response_orders

    def get_prices(self):
        feeds = session.query(Feed).all()
        response_feeds = ''
        for feed in feeds:
            response_feeds += f"Name: {feed.name}, Price: {feed.price}\n"

        return response_feeds

    def get_gipo_type(self):
        feeds = session.query(Feed).filter_by(type='гіпоалергенний').all()
        response_feeds = ''
        for feed in feeds:
            response_feeds += f"Name: {feed.name}, Type: {feed.type}, Pet: {feed.pet}\n"

        return response_feeds

    def get_def_type(self):
        feeds = session.query(Feed).filter_by(type='звичайний').all()
        response_feeds = ''
        for feed in feeds:
            response_feeds += f"Name: {feed.name}, Type: {feed.type}, Pet: {feed.pet}\n"

        return response_feeds

    def get_feeds(self):
        feeds = session.query(Feed).all()
        response_feeds = ''
        for feed in feeds:
            response_feeds += f"Name: {feed.name}, Type: {feed.type}, Pet: {feed.pet}\n"

        return response_feeds


if __name__ == '__main__':
    assistant = Assistant()
    while True:
        user_input = str(input("Введіть запит: "))
        response = assistant.run(user_input)
        print("Ассистент: {}".format(response))
