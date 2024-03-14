import telebot # основной файл
from telebot import types
import os
import json
import pandas as pd

bot = telebot.TeleBot("")


@bot.message_handler(commands=["start"])
def start(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    if message.chat.id not in list(inf_database["id_пользователя"]):
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}! Я бот помощник по подготовке к иностранным языкам.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Учитель")
        btn2 = types.KeyboardButton("Ученик")
        markup.add(btn1, btn2)
        sent_msg = bot.send_message(message.chat.id, "Вы учитель или ученик? Для ответа нажмите на кнопку", reply_markup=markup)
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
    os.mkdir(f"Teachers/{message.chat.id}")
    os.mkdir(f"Teachers/{message.chat.id}/Topics")
    os.mkdir(f"Teachers/{message.chat.id}/Topics/txt")
    with open(f"Teachers/{message.chat.id}/dict_topic.json", "w", encoding='utf-8') as jfile:
        json.dump({}, jfile)
    inf_database = pd.read_csv("информация_о_людях.csv")
    name = message.text
    sl = {"id": message.chat.id, "name": name, "student": stud}
    inf_database.loc[len(inf_database)] = [message.chat.id, name, stud]
    inf_database.to_csv("информация_о_людях.csv", mode='w', index = False)
    bot.send_message(message.chat.id, "Введите команду /menu для открытия меню")
    #Добавляем имя в базу данных, обозначаем как учитель

def name_student(message, stud):
    inf_database = pd.read_csv("информация_о_людях.csv")
    name = message.text
    sl = {"id": message.chat.id, "name": name, "student": stud}
    inf_database.loc[len(inf_database)] = [message.chat.id, name, stud]
    inf_database.to_csv("информация_о_людях.csv", mode='w', index = False)
    bot.send_message(message.chat.id, "Введите команду /menu для открытия меню")
    # Добавляем имя в базу данных, обозначаем как учитель

@bot.message_handler(commands=["menu"])
def welcome(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    n = list(inf_database[inf_database["id_пользователя"] == message.chat.id]["имя"])[0]
    sent_msg = bot.send_message(message.chat.id, f"Welcome, {n}!")
    if message.chat.id not in list(inf_database["id_пользователя"]):
        bot.send_message(message.chat.id, "Напишите /start для регистрации")
    elif list(inf_database[inf_database["id_пользователя"] == message.chat.id]['ученик'])[0] is False:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Меню")
        markup.add(btn1)
        sent_msg = bot.send_message(message.chat.id, "Напишите кнопку, чтобы зайти в меню", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, menu_teacher)
    elif list(inf_database[inf_database["id_пользователя"] == message.chat.id]['ученик'])[0] is True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Меню")
        markup.add(btn1)
        sent_msg = bot.send_message(message.chat.id, "Напишите кнопку, чтобы зайти в меню", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, menu_student)
def menu_teacher(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить тему")
    btn2 = types.KeyboardButton("Список тем")
    markup.add(btn1, btn2)
    n = list(inf_database[inf_database["id_пользователя"] == message.chat.id]["имя"])[0]
    sent_msg = bot.send_message(message.chat.id, f"Добро пожаловать в меню, {n}. Для навигации нажимайте на кнопки.", reply_markup=markup)  # здесь писать имя человека из базы
    bot.register_next_step_handler(sent_msg, navigate_teacher)
def navigate_teacher(message):
    if message.text == "Добавить тему":
        sent_msg = bot.send_message(message.chat.id, "Чтобы добавить тему, напишите название темы")
        bot.register_next_step_handler(sent_msg, file_topic)
    elif message.text == "Список тем":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        with open(f'Teachers/{message.chat.id}/dict_topic.json', encoding='utf-8') as jsfile:
            main_dict = json.load(jsfile)
        sp = [types.KeyboardButton(i) for i in main_dict]
        markup.add(*sp)
        sent_msg = bot.send_message(message.chat.id, "Список тем:", reply_markup=markup)

def file_topic(message):
    topic_name = message.text  # Добавить в базу
    sent_msg = bot.send_message(message.chat.id, "Дальше отправьте файл в формате txt, где будут записаны слова в формате *English word - перевод*, каждое с новой строки", parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, get_file_topic, topic_name)
def get_file_topic(message, topic_name):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    name_of_txt = message.document.file_name
    with open(f'Teachers/{message.chat.id}/Topics/txt/{name_of_txt}', 'wb') as new_file:
        new_file.write(downloaded_file)
    with open(f'Teachers/{message.chat.id}/dict_topic.json', encoding='utf-8') as jsfile:
        main_dict = json.load(jsfile)
        with open(f'Teachers/{message.chat.id}/Topics/txt/{name_of_txt}', encoding='utf-8') as txtfile:
            slovar = {}
            for i in txtfile.read().split("\n"):
                slovar[i.split(' - ')[0]] = i.split(' - ')[1]
            main_dict[topic_name] = slovar
            with open(f'Teachers/{message.chat.id}/dict_topic.json', 'w', encoding='utf-8') as writejson:
                json.dump(main_dict, writejson, ensure_ascii=False)
    sent_msg = bot.send_message(message.chat.id, "Файл загружен")

def menu_student(message):
    inf_database = pd.read_csv("информация_о_людях.csv")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Пройти тест")
    markup.add(btn1)
    n = list(inf_database[inf_database["id_пользователя"] == message.chat.id]["имя"])[0]
    sent_msg = bot.send_message(message.chat.id, f"Добро пожаловать в меню, {n}. Для навигации нажимайте на кнопки.", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, navigate_student)

def navigate_student(message):
    if message.text == "Пройти тест":
        sent_msg = bot.send_message(message.chat.id, "Введите id учителя")
        bot.register_next_step_handler(sent_msg, get_id)
    #elif message.text == "Результаты":

def get_id(message):
    teacher_id = message.text
    sent_msg = bot.send_message(message.chat.id, "Введите название темы")
    bot.register_next_step_handler(sent_msg, get_test, teacher_id)

def get_test(message, teacher_id):
    name_topic = message.text
    try:
        with open(f'Teachers/{str(teacher_id)}/dict_topic.json', "r", encoding='utf-8') as f:
            main_dict = json.load(f)
            if name_topic in main_dict:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("Начать тест!")
                markup.add(btn1)
                sent_msg = bot.send_message(message.chat.id, "Тест найден! Нажмите кнопку или напишите любое слово, чтобы начать", reply_markup=markup)
                count = 0
                result = 0
                bot.register_next_step_handler(sent_msg, go, teacher_id, name_topic, count, result)
            else:
                sent_msg = bot.send_message(message.chat.id, "Такой темы нет или вы ввели неправильный id учителя. Напишите /menu или любое слово, чтобы попасть в меню")
                bot.register_next_step_handler(sent_msg, menu_student)
    except:
        sent_msg = bot.send_message(message.chat.id, "Такой темы нет или вы ввели неправильный id учителя.")
        bot.register_next_step_handler(sent_msg, menu_student)

def go(message, teacher_id, name_topic, count, result):
    with open(f'Teachers/{teacher_id}/dict_topic.json', "r", encoding='utf-8') as f:
        main_dict = json.load(f)
        sent_msg = bot.send_message(message.chat.id, [i for i in main_dict[name_topic]][count])
        bot.register_next_step_handler(sent_msg, answer, teacher_id, name_topic, count, result)

def answer(message, teacher_id, name_topic, count, result):
    with open(f'Teachers/{teacher_id}/dict_topic.json', "r", encoding='utf-8') as f:
        main_dict = json.load(f)
        if message.text == main_dict[name_topic][[i for i in main_dict[name_topic]][count]]:
            result += 1
        count += 1
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Продолжить!")
        markup.add(btn1)
        sent_msg = bot.send_message(message.chat.id, "Ответ получен. Нажмите на кнопку, чтобы продолжить.", reply_markup=markup)
        if count == len(main_dict[name_topic]):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Посмотреть результаты")
            markup.add(btn1)
            sent_msg = bot.send_message(message.chat.id, "Тест закончен. Нажмите на кнопку, чтобы посмотреть результаты", reply_markup=markup)
            bot.register_next_step_handler(sent_msg, final, result, teacher_id, name_topic)
        else:
            bot.register_next_step_handler(sent_msg, go, teacher_id, name_topic, count, result)

def final(message, result, teacher_id, name_topic):
    sent_msg = bot.send_message(message.chat.id, f"Ваш результат: {result}")
    student_id = message.chat.id
    df = pd.read_csv("database.csv")
    df.loc[len(df)] = [student_id, teacher_id, name_topic, result]
    df.to_csv("database.csv", mode='w', index=False)





@bot.message_handler(content_types=["text"])
def f(message):
    bot.send_message(message.chat.id, "Введите команду /menu для открытия меню")

bot.infinity_polling()