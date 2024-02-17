import pyttsx3
import speech_recognition as sr


# Creating class for echo bot
class EchoBot:
    # Constructor method
    def __init__(self) -> None:
        # Create engine for TTS (Text-To-Speach)
        self.engine = pyttsx3.init()
        # Applying default settings fot TTS engine
        self.__set_default_settings()
        self.recognizer = sr.Recognizer()

    # Default setting method (encapsulated)
    # (run after object initialization by default)
    def __set_default_settings(self) -> bool:
        # Get all available voices
        voices = self.engine.getProperty('voices')

        # Search voice with Ukrainian language and set it
        for voice in voices:
            if voice.name == 'Volodymyr':
                self.engine.setProperty('voice', voice.id)

        # Set voice rate
        self.engine.setProperty('rate', 100)
        # set voice volume
        self.engine.setProperty('volume', 1)

        return True

    # Response audio and text method (encapsulated)
    # (takes message with string type)
    def __bot_response(self, message: str) -> bool:
        # Say text
        self.engine.say(message)
        # Control that program continued work after pronounce all text
        self.engine.runAndWait()
        # Print text
        print("Bot: " + message)

        return True

    # Set voice method (encapsulated)
    def __set_voice(self) -> bool:
        # Get all voices
        voices = self.engine.getProperty('voices')

        # Show all voices in chat
        for voice in voices:
            print(f"[{voice.id}]Voice: {voice.name}")

        # Get from user new voice id
        choise_voice = int(input("Введіть id голосу: "))
        # Set new voice
        self.engine.setProperty('voice', choise_voice)

        return True

    # Set rate method (encapsulated)
    def __set_rate(self) -> bool:
        # Create loop for set voice rate
        while True:
            # Get from user voice rate
            choise_rate = int(input("Введіть швидкість проговорення (від 100 до 300): "))

            # Check if voice rate from 100 to 300
            if 100 <= choise_rate <= 300:
                # Set voice rate
                self.engine.setProperty('rate', choise_rate)

                # Create message for bot response
                message = f"Швидкість проговорення встановленна на {choise_rate}"

                # Bot response
                self.__bot_response(message)

                return True
            # Rate not in 100 to 300
            else:
                # Create message
                message = (f"Ви ввели {choise_rate}, рекомендоване значення від 100 до 300! \nЯкщо ви хочете " +
                           f"використати це значення введіть так.")
                # Say message
                self.__bot_response(message)

                # Get user decision
                confirm = str(input("Так чи ні: "))
                # If user agree set voice rate
                if confirm.lower() in 'так':
                    self.engine.setProperty('rate', choise_rate)

                    return True
                # If not user did not agree continue loop
                elif confirm.lower() == 'ні':
                    continue

        return True

    # Set voice volume (encapsulated)
    def __set_volume(self) -> bool:
        # Loop to get volume settings
        while True:
            # Get from user volume height
            choise_volume = float(input("Введіть гучність проговорення (від 0.1 до 1): "))

            # Check if volume from 0.1 to 1
            if 0.1 <= choise_volume <= 1:
                # Set volume value
                self.engine.setProperty('volume', choise_volume)

                # Create message for bot response
                message = f"Гучність встановленна на {choise_volume}"

                # Bot response
                self.__bot_response(message)

                return True
            # If not show error message
            else:
                # Create message to for bot response
                message = f"Ви ввели {choise_volume}, значення має бути у проміжку від 0.1 до 1"

                # Bot response
                self.__bot_response(message)

                # Continue loop
                continue

        return True

    # Chat settings method (encapsulated)
    def __chat_settings(self) -> bool:
        # Create message to get from user his decision
        print("""Оберіть налаштування
        [1]. Голос, мова (1, голос, мова)
        [2]. Швидкість проговорення (2, швидкість проговорення)
        [3]. Гучність (3, гучність)
        [4]. Завершити (4, завершити)""")

        # Loop for setting
        while True:
            choise = input("Вибір:")

            if choise.lower() in ["1", "голос", "мова"]:
                self.__set_voice()
            elif choise.lower() in ["2", "швидкість проговорення"]:
                self.__set_rate()
            elif choise.lower() in ["3", "гучність"]:
                self.__set_volume()
            elif choise.lower() in ["4", "завершити"]:
                return True
            else:
                message = "Немає такого налаштування спробуйте ше раз"
                self.__bot_response(message)

        return True

    # Bot chat method (encapsulated)
    def __chat(self, type: int) -> bool:
        # Loop until user decided to exit
        while True:
            # Get message from user
            if type == 1:
                with sr.Microphone() as source:
                    print("Повідомлення: ")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)

                try:
                    user_input = self.recognizer.recognize_google(audio, language="uk-UA")
                except sr.UnknownValueError:
                    print("Не вдалося розпізнати мовлення")
                except sr.RequestError as e:
                    print("Помилка при отриманні результатів від Google Speech Recognition service; {0}".format(e))

            if type == 2:
                user_input = str(input("Message: "))

            # Check if user message mean to exit from program
            if user_input.lower() in ["до побачення", "вихід"]:
                # Call response method
                self.__bot_response("До побачення гарного дня!!!")
                # Break point
                break

            # Check if user message call settings
            if user_input.lower() in ["налаштування"]:
                pass

            # Call response method
            self.__bot_response(user_input)

        return True

    # Method to start bot
    def run(self) -> bool:
        # Request from user action
        choice = input('''Привіт це Ехо-Бот!!!
        Оберіть що ви хочете:
            1. Спілкування з ботом ( Введіть 1 або спілкування )
            2. Налаштування боту ( Введіть 2 або налаштування
        Enter your choice: ''')

        while True:
            # Check what user decided
            if choice == '1' or choice == 'спілкування':
                type = input("""Введіть як ви хочете спілкуватись
                1. За допомогою голосу (1, голос)
                2. За допомогою тексту (2, текст)
                Ваш вибір: """)

                if type in ["1", "голос"]:
                    self.__chat(1)
                elif type in ["2", "'текст"]:
                    self.__chat(2)
                else:
                    message = "Немає такого варінту!"
                    self.__bot_response(message)
                    continue

            elif choice == '2' or choice == 'налаштування':
                self.__chat_settings()
            # Uncorrected error message
            else:
                print('Incorrect option!')

        return True


# Start file program
if __name__ == "__main__":
    # Create object from class
    bot = EchoBot()
    # Run echo bot
    bot.run()
