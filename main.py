# Бот канала Понемногу обо всем.

import telebot
import pymysql
import config
import messages

# Создание объекта бота:
bot = telebot.TeleBot(config.bot_token)


# Возвращает ID пользователя в БД из строки, заданной аргументом:
def extract_number(message_text):
    i = 0

    while not message_text[i].isdigit():
        i += 1

    j = i

    while message_text[i].isdigit():
        i += 1

    return int(message_text[j:i])


# Возвращает ответ пользователю из строки, заданной аргументом:
def extract_answer(message_text):
    answer = ''
    flag = False

    for i in range(len(message_text)):

        if flag:
            answer += message_text[i]

        if message_text[i] == '\n':
            flag = True

    return answer


# Обработчики команд:


# Команда /start:
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, messages.start_message)


# Команда /help:
@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(message.chat.id, messages.help_message)


# Команда /feedback:
@bot.message_handler(commands=["feedback"])
def feedback_message(message):
    if message.chat.id == config.owner:

        # Чтение из БД данных всех пользователей, ожидающих ответа:
        db_con = pymysql.connect(config.host, config.user, config.password, config.db)

        try:

            with db_con.cursor() as cursor:

                query = "SELECT COUNT(*) FROM users;"
                cursor.execute(query)

                for i in cursor:

                    if i[0] == 0:

                        bot.send_message(config.owner, messages.feedback_author_message_2)

                    else:

                        query = "SELECT ID, user_name FROM users;"
                        cursor.execute(query)

                        answer = messages.feedback_author_message_3

                        for j in cursor:
                            answer += (str(j[0]) + " - " + j[1] + "\n")

                        bot.send_message(config.owner, answer)
                        bot.send_message(config.owner, messages.feedback_author_message_1)

        finally:

            db_con.close()

    elif message.text == "/feedback":

        bot.send_message(message.chat.id, messages.feedback_user_message_1)

    else:

        # Запись ID пользователя в БД:
        db_con = pymysql.connect(config.host, config.user, config.password, config.db)

        try:

            with db_con.cursor() as cursor:

                query = "INSERT INTO users(chat_id, user_name) VALUES (" + str(
                    message.chat.id) + ", '" + message.from_user.first_name + "');"
                cursor.execute(query)
                db_con.commit()

        finally:

            db_con.close()

        # Сообщение автору:
        bot.send_message(config.owner, "Сообщение от " + str(message.from_user.first_name) + ":")
        bot.forward_message(config.owner, message.chat.id, message.message_id)

        # Сообщение пользователю:
        bot.send_message(message.chat.id, str(message.from_user.first_name) + messages.feedback_user_message_2)


# Команда /answer:
@bot.message_handler(commands=["answer"])
def answer_message(message):
    if message.chat.id == config.owner:

        user_number = extract_number(message.text)
        user_answer = extract_answer(message.text)

        # Ответ пользователю:
        db_con = pymysql.connect(config.host, config.user, config.password, config.db)

        try:

            with db_con.cursor() as cursor:

                query = "SELECT chat_id, user_name FROM users WHERE ID = " + str(user_number) + ";"
                cursor.execute(query)

                for row in cursor:
                    bot.send_message(int(row[0]), row[1] + messages.answer_user_message_1 + user_answer)

                query = "DELETE FROM users WHERE ID = " + str(user_number) + ";"
                cursor.execute(query)

                bot.send_message(config.owner, messages.answer_author_message)

                db_con.commit()

        finally:

            db_con.close()

    else:

        bot.send_message(message.chat.id, messages.answer_user_message_2)


# Команда /privacy:
@bot.message_handler(commands=["privacy"])
def privacy_message(message):
    bot.send_message(message.chat.id, messages.privacy_message)


# Обработка текстового сообщения:
@bot.message_handler(content_types=["text"])
def send_text(message):
    bot.send_message(message.chat.id, messages.default_message)


if __name__ == "__main__":
    bot.polling(none_stop=True)
