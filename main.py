import telebot  # основной файл
import random
from telebot import types
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

bot = telebot.TeleBot("7148716540:AAFK_D_AKZt1dDE4VC6nT4dgzcI_6HNn1XA")


def pieplot(teacher_id, name_of_database_csv="database.csv", topic="овощи"):
    inf_database = pd.read_csv("информация_о_людях.csv")
    with open(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == teacher_id]['id_внутреннее'])[0]}/dict_topic.json", "r", encoding='utf-8') as f:
        slovar = json.load(f)[topic]
        len_slovar = len(slovar)
    df = pd.read_csv(name_of_database_csv)
    twenty_low = len(df[(df['название_темы'] == topic) & (df["количество_баллов"] / len_slovar * 100 <= 20)])
    fifty_low = len(df[(df['название_темы'] == topic) & (20 < df["количество_баллов"] / len_slovar * 100) & (
                df["количество_баллов"] / len_slovar * 100 <= 50)])
    seventy_five_low = len(df[(df['название_темы'] == topic) & (50 < df["количество_баллов"] / len_slovar * 100) & (
                df["количество_баллов"] / len_slovar * 100 <= 75)])
    hundred_low = len(df[(df['название_темы'] == topic) & (75 < df["количество_баллов"] / len_slovar * 100) & (
                df["количество_баллов"] / len_slovar * 100 < 100)])
    hundred = len(df[(df['название_темы'] == topic) & (df["количество_баллов"] / len_slovar * 100 == 100)])
    labels = ["<= 20", "20 < x <= 50", "50 < x <= 75", "75 < x < 100", "100"]
    data = [twenty_low, fifty_low, seventy_five_low, hundred_low, hundred]

    plt.pie(data, autopct='%1.1f%%')
    plt.legend(loc='right', labels=labels, bbox_to_anchor=(1.2, 0, 0, 0))
    plt.savefig(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == teacher_id]['id_внутреннее'])[0]}/ds/pie.jpg")


def participants(name_of_database_csv="database.csv", topic="овощи"):
    topic = topic.lower()
    df = pd.read_csv(name_of_database_csv)
    inf_database = pd.read_csv("информация_о_людях.csv")
    mnozh = set(df[df['название_темы'] == topic]["id_пользователя"].tolist())
    slovar_with_result = {}
    for i in mnozh:
        slovar_with_result[list(inf_database[inf_database['id_пользователя'] == i]["id_внутреннее"])[0]] = max(
            df[(df['название_темы'] == topic) & (df["id_пользователя"] == i)]["количество_баллов"])
    return slovar_with_result


def max_result_count_test(name_of_database_csv, topic, stud_id):
    topic = topic.lower()
    df = pd.read_csv(name_of_database_csv)
    return [max((df[(df['название_темы'] == topic) & (df["id_пользователя"] == stud_id)]['количество_баллов'])), len(df[
                                                                                                                         (
                                                                                                                                     df[
                                                                                                                                         'название_темы'] == topic) & (
                                                                                                                                     df[
                                                                                                                                         "id_пользователя"] == stud_id)])]  # выводит сначала макс балл ученика, а потом количество попыток


@bot.message_handler(commands=["start"])
def start(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    if message.chat.id not in list(inf_database["id_пользователя"]):
        bot.send_message(message.chat.id,
                         f"Здравствуйте, {message.from_user.first_name}! Я бот помощник по подготовке к иностранным языкам.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Учитель")
        btn2 = types.KeyboardButton("Ученик")
        markup.add(btn1, btn2)
        sent_msg = bot.send_message(message.chat.id, "Вы учитель или ученик? Для ответа нажмите на кнопку",
                                    reply_markup=markup)
        bot.register_next_step_handler(sent_msg, person)
    else:
        bot.send_message(message.chat.id, "Напишите /menu, чтобы открыть меню")


def person(message):
    if message.text == "Учитель":
        sent_msg = bot.send_message(message.chat.id, "Как вас зовут? Напишите в формате Фамилия Имя (Иванов Иван)")
        bot.register_next_step_handler(sent_msg, name_teacher, False)
    elif message.text == "Ученик":
        sent_msg = bot.send_message(message.chat.id, "Как вас зовут? Напишите в формате Фамилия Имя (Иванов Иван)")
        bot.register_next_step_handler(sent_msg, name_student, True)
    else:
        sent_msg = bot.send_message(message.chat.id, "Нажмите на кнопку")
        bot.register_next_step_handler(sent_msg, person)


def name_teacher(message, stud):
    inf_database = pd.read_csv("информация_о_людях.csv")
    name = message.text.lower()
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    sl = {"id": message.chat.id, "name": name, "student": stud}
    inter_id = str(len(inf_database['id_внутреннее']) + 1) + random.choice(a) + random.choice(a) + random.choice(a)
    inf_database.loc[len(inf_database)] = [message.chat.id, name, stud, inter_id]
    inf_database.to_csv("информация_о_людях.csv", mode='w', index=False)
    os.mkdir(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}")
    os.mkdir(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}/ds")
    os.mkdir(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}/Topics")
    os.mkdir(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}/Topics/txt")
    with open(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}/dict_topic.json", "w", encoding='utf-8') as jfile:
        json.dump({}, jfile)
    bot.send_message(message.chat.id, "Введите команду /menu для открытия меню")
    # Добавляем имя в базу данных, обозначаем как учитель


def name_student(message, stud):
    inf_database = pd.read_csv("информация_о_людях.csv")
    name = message.text.lower()
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    sl = {"id": message.chat.id, "name": name.lower(), "student": stud}
    inter_id = str(len(inf_database['id_внутреннее']) + 1) + random.choice(a) + random.choice(a) + random.choice(a)
    inf_database.loc[len(inf_database)] = [message.chat.id, name, stud, inter_id]
    inf_database.to_csv("информация_о_людях.csv", mode='w', index=False)
    bot.send_message(message.chat.id, "Введите команду /menu для открытия меню")
    # Добавляем имя в базу данных, обозначаем как учитель


@bot.message_handler(commands=["menu"])
def welcome(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    if message.chat.id not in list(inf_database["id_пользователя"]):
        bot.send_message(message.chat.id, "Напишите /start для регистрации")
    elif list(inf_database[inf_database["id_пользователя"] == message.chat.id]['ученик'])[0] is False:
        menu_teacher(message)
    elif list(inf_database[inf_database["id_пользователя"] == message.chat.id]['ученик'])[0] is True:
        menu_student(message)


def menu_teacher(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить тему")
    btn2 = types.KeyboardButton("Список тем")
    markup.add(btn1, btn2)
    n = list(inf_database[inf_database["id_пользователя"] == message.chat.id]["имя"])[0]
    sent_msg = bot.send_message(message.chat.id, f"Добро пожаловать в меню, {n.title()}. Ваш id *{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}*. Для навигации нажимайте на кнопки.",
                                reply_markup=markup, parse_mode="Markdown")  # здесь писать имя человека из базы
    bot.register_next_step_handler(sent_msg, navigate_teacher)


def navigate_teacher(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    if message.text == "Добавить тему":
        sent_msg = bot.send_message(message.chat.id, "Чтобы добавить тему, напишите название темы")
        bot.register_next_step_handler(sent_msg, file_topic)
    elif message.text == "Список тем":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/dict_topic.json', encoding='utf-8') as jsfile:
            main_dict = json.load(jsfile)
        sp = [types.KeyboardButton(i) for i in main_dict]
        markup.add(*sp)
        sent_msg = bot.send_message(message.chat.id, "Список тем:", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, data_sc)
    else:
        sent_msg = bot.send_message(message.chat.id, "Нажмите на кнопку")
        bot.register_next_step_handler(sent_msg, navigate_teacher)


def file_topic(message):
    try:
        topic_name = message.text.lower()  # Добавить в базу
        sent_msg = bot.send_message(message.chat.id,
                                    "Дальше отправьте файл в формате txt, где будут записаны слова в формате *English word - перевод*, каждое с новой строки",
                                    parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, get_file_topic, topic_name)
    except Exception as e:
        bot.send_message(message.chat.id, "Неправильное название для темы")
        bot.send_message(705359495, "Неправильное название для темы" + e)


def get_file_topic(message, topic_name):
    try:
        inf_database = pd.read_csv("информация_о_людях.csv")
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        name_of_txt = message.document.file_name
        with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/Topics/txt/{name_of_txt}', 'wb') as new_file:
            new_file.write(downloaded_file)
        with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/dict_topic.json', encoding='utf-8') as jsfile:
            main_dict = json.load(jsfile)
            with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/Topics/txt/{name_of_txt}', encoding='utf-8') as txtfile:
                slovar = {}
                for i in txtfile.read().split("\n"):
                    i = i.lower()
                    slovar[i.split(' - ')[0]] = i.split(' - ')[1:]
                main_dict[topic_name] = slovar
                with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/dict_topic.json', 'w', encoding='utf-8') as writejson:
                    json.dump(main_dict, writejson, ensure_ascii=False)
        sent_msg = bot.send_message(message.chat.id, "Файл загружен")
    except:
        bot.send_message(message.chat.id, "Ошибка загрузки файла")


def menu_student(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Пройти тест")
    btn2 = types.KeyboardButton("Результаты")
    markup.add(btn1, btn2)
    n = list(inf_database[inf_database["id_пользователя"] == message.chat.id]["имя"])[0]
    sent_msg = bot.send_message(message.chat.id, f"Добро пожаловать в меню, {n.title()}. Для навигации нажимайте на кнопки.",
                                reply_markup=markup)
    bot.register_next_step_handler(sent_msg, navigate_student)


def navigate_student(message):
    if message.text == "Пройти тест":
        sent_msg = bot.send_message(message.chat.id, "Введите id учителя")
        bot.register_next_step_handler(sent_msg, get_id)
    elif message.text == "Результаты":
        res_database = pd.read_csv("database.csv")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*list(set(res_database[res_database["id_пользователя"] == message.chat.id]["название_темы"])))
        bot.send_message(message.chat.id, "Выберите тему:", reply_markup=markup)
        bot.register_next_step_handler(message, result_student)
    else:
        bot.send_message(message.chat.id, "Нажмите на кнопку")
        bot.register_next_step_handler(message, navigate_student)

def result_student(topic_name):
    res_database = pd.read_csv("database.csv")
    if topic_name.text.lower() not in set(res_database[res_database["id_пользователя"] == topic_name.chat.id]["название_темы"]):
        bot.send_message(topic_name.chat.id, "Нажмите на кнопку")
        bot.register_next_step_handler(topic_name, result_student)
    else:
        inf_database = pd.read_csv("информация_о_людях.csv")
        bot.send_message(topic_name.chat.id,
                         f'Ваш максимальный балл: {max_result_count_test("database.csv", topic_name.text, topic_name.chat.id)[0]}')
        markup = types.ReplyKeyboardRemove()
        bot.send_message(topic_name.chat.id,
                         f'Количество попыток: {max_result_count_test("database.csv", topic_name.text, topic_name.chat.id)[1]}', reply_markup=markup)


def get_id(message):
    teacher_id = message.text
    sent_msg = bot.send_message(message.chat.id, "Введите название темы")
    bot.register_next_step_handler(sent_msg, get_test, teacher_id)


def get_test(message, teacher_id):
    name_topic = message.text.lower()
    inf_database = pd.read_csv("информация_о_людях.csv")
    try:
        with open(f'Teachers/{teacher_id}/dict_topic.json', "r", encoding='utf-8') as f:
            main_dict = json.load(f)
            if name_topic in main_dict:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("Начать тест!")
                markup.add(btn1)
                sent_msg = bot.send_message(message.chat.id,
                                            "Тест найден! Вам будут писаться слова на иностранном языке, а вы должны будете написать их перевод. Нажмите кнопку или напишите любое слово, чтобы начать",
                                            reply_markup=markup)
                count = 0
                result = 0
                bot.register_next_step_handler(sent_msg, go, teacher_id, name_topic, count, result)
            else:
                sent_msg = bot.send_message(message.chat.id,
                                            "Такой темы нет или вы ввели неправильный id учителя. Напишите /menu или любое слово, чтобы попасть в меню")
                bot.register_next_step_handler(sent_msg, menu_student)
    except:
        sent_msg = bot.send_message(message.chat.id, "Такой темы нет или вы ввели неправильный id учителя.")
        bot.register_next_step_handler(sent_msg, menu_student)


def go(message, teacher_id, name_topic, count, result):
    markup = types.ReplyKeyboardRemove()
    inf_database = pd.read_csv("информация_о_людях.csv")
    with open(f'Teachers/{teacher_id}/dict_topic.json', "r", encoding='utf-8') as f:
        main_dict = json.load(f)
        sent_msg = bot.send_message(message.chat.id, [i for i in main_dict[name_topic]][count], reply_markup=markup)
        bot.register_next_step_handler(sent_msg, answer, teacher_id, name_topic, count, result)


def answer(message, teacher_id, name_topic, count, result):
    inf_database = pd.read_csv("информация_о_людях.csv")
    with open(f'Teachers/{teacher_id}/dict_topic.json', "r", encoding='utf-8') as f:
        main_dict = json.load(f)
        if message.text.lower() in main_dict[name_topic][[i for i in main_dict[name_topic]][count]]:
            result += 1
            ans = "правильный"
        else:
            ans = "неправильный"
        count += 1
        sent_msg = bot.send_message(message.chat.id, f"Это {ans} ответ")
        if count == len(main_dict[name_topic]):
            sent_msg = bot.send_message(message.chat.id,
                                        "Тест закончен")
            final(message, result, teacher_id, name_topic)
        else:
            go(message, teacher_id, name_topic, count, result)


def final(message, result, teacher_id, name_topic):
    bot.send_message(message.chat.id, f"Ваш результат: {result}")
    student_id = message.chat.id
    df = pd.read_csv("database.csv")
    df.loc[len(df)] = [student_id, teacher_id, name_topic, result]
    df.to_csv("database.csv", mode='w', index=False)


def data_sc(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/dict_topic.json', encoding='utf-8') as jsfile:
        main_dict = json.load(jsfile)
    if message.text not in main_dict:
        bot.send_message(message.chat.id, "Такой темы нет")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Получить диаграмму")
        btn2 = types.KeyboardButton("Результаты")
        btn3 = types.KeyboardButton("Информация об ученике")
        btn4 = types.KeyboardButton("Удалить тему")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, f"Вы выбрали тему {message.text}", reply_markup=markup)
        bot.register_next_step_handler(message, data_science, message)

def data_science(message, topic_name):
    inf_database = pd.read_csv("информация_о_людях.csv")
    if message.text == "Получить диаграмму":
        pieplot(message.chat.id, "database.csv", topic_name.text)
        bot.send_photo(message.chat.id, open(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}/ds/pie.jpg", "rb"))
        os.remove(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}//ds/pie.jpg")
        bot.register_next_step_handler(message, data_science, topic_name)
    elif message.text == "Результаты":
        inf_database = pd.read_csv("информация_о_людях.csv")
        sl = participants("database.csv", topic_name.text)
        bot.send_message(message.chat.id, "имя   результат")
        sp = [f'{list(inf_database[inf_database["id_внутреннее"] == i]["имя"])[0]}   {sl[i]}' for i in sl]
        bot.send_message(message.chat.id, '\n'.join(sp))
        bot.register_next_step_handler(message, data_science, topic_name)
    elif message.text == "Информация об ученике":
        stud_result(topic_name)
    elif message.text == "Удалить тему":
        with open(f'Teachers/{list(inf_database[inf_database["id_пользователя"] == message.chat.id]["id_внутреннее"])[0]}/dict_topic.json', encoding='utf-8') as jsfile:
            main_dict = json.load(jsfile)
        del main_dict[topic_name.text]
        with open(f"Teachers/{list(inf_database[inf_database['id_пользователя'] == message.chat.id]['id_внутреннее'])[0]}/dict_topic.json", "w", encoding='utf-8') as jfile:
            json.dump(main_dict, jfile)
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Тема удалена", reply_markup=markup)
        return
    elif message.text == "/menu":
        welcome(message)
    else:
        bot.send_message(message.chat.id, "Нажми на кнопку")
        bot.register_next_step_handler(message, data_science, topic_name)


def stud_result(message):
    bot.send_message(message.chat.id, "Имя и фамилия ученика с большой буквы, у которого вы хотите узнать результаты?")
    bot.register_next_step_handler(message, get_max, message)


def get_max(message, topic_name):
    try:
        message.text = message.text.lower()
        inf_database = pd.read_csv("информация_о_людях.csv")
        bot.send_message(message.chat.id,
                         f'Максимальный балл ученика: {max_result_count_test("database.csv", topic_name.text, list(inf_database[inf_database["имя"] == message.text]["id_пользователя"])[0])[0]}')
        bot.send_message(message.chat.id,
                         f'Количество попыток: {max_result_count_test("database.csv", topic_name.text, list(inf_database[inf_database["имя"] == message.text]["id_пользователя"])[0])[1]}')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Да")
        btn2 = types.KeyboardButton("Нет")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Вы хотите узнать результат другого ученика?", reply_markup=markup)
        bot.register_next_step_handler(message, get_max1, topic_name)
    except:
        bot.send_message(message.chat.id, "Проблема с получением статистики.")


def get_max1(message, topic_name):
    if message.text == "Да":
        stud_result(topic_name)
    elif message.text == "Нет":
        data_sc(topic_name)
    else:
        bot.send_message(message.chat.id, "Нажмите на кнопку")
        bot.register_next_step_handler(message, get_max1, topic_name)


@bot.message_handler(content_types=["text"])
def f(message):
    bot.send_message(message.chat.id, "Введите команду /menu для открытия меню")

bot.infinity_polling()
