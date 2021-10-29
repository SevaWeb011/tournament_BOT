import os
import time
import threading
from threading import Thread
import telebot
from telebot import types
import main
import logging
import json

token = os.getenv("BOT")
bot = telebot.TeleBot(token)
state = "city_selection"
global listCity
listCity = []

@bot.message_handler(content_types=['text'])

def message(message):

    mainButton = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main1 = types.KeyboardButton('сообщение автору')
    main2 = types.KeyboardButton('сменить город')
    main3 = types.KeyboardButton('мой город')
    main5 = types.KeyboardButton('турниры на выходных')
    main4 = types.KeyboardButton('турниры в моем городе')

    mainButton.add(main1, main2, main3, main5, main4)

    towns = types.ReplyKeyboardMarkup(resize_keyboard=True)

    age = types.ReplyKeyboardMarkup(resize_keyboard=True)
    age1 = types.KeyboardButton('я ребенок (до 18 лет)')
    age2 = types.KeyboardButton('я взрослый')
    age.add(age1, age2)

    navigation = types.ReplyKeyboardMarkup(resize_keyboard=True)
    nav1 = types.KeyboardButton('далее')
    nav2 = types.KeyboardButton('стоп')
    navigation.add(nav1, nav2)

    state_user = "city_selection"

    users = [
        message.chat.id,
        message.chat.first_name,
        message.chat.last_name,
        message.chat.username,
        state_user
    ]

    main.query_users(users)

    SelectState = main.selectState(message.chat.id)

#=======================================================================================================
#ИСПРАВНО
    if SelectState == "city_selection":

        all_city = sorted(set(main.get_all_cities()) - set(listCity))
        for city in all_city:
            towns.add(types.KeyboardButton(city))

        if message.text.lower() == "/start":
            bot.send_message(message.chat.id, 'Привет, выбери города 🏘, в которых турниры актуальны для тебя 😉', reply_markup=towns)
            #log(message.chat.id, "send command /start", logging.INFO)

        if message.html_text in all_city:
            main.add_city(message.chat.id, message.html_text)
            listCity.append(message.html_text)
            bot.send_message(message.chat.id, 'Если хочешь выбрать еще города, нажми ДАЛЕЕ, если нет, то нажми СТОП', reply_markup=navigation)

        if message.html_text == 'далее':
            bot.send_message(message.chat.id, 'Выбери город', reply_markup=towns)
       
        if message.html_text == 'стоп':
            main.query_change_state("age_category", message.chat.id)
            SelectState = main.selectState(message.chat.id)
            bot.send_message(message.chat.id, 'Выбери свою категорию. Это нужно, чтобы я фильтровал для тебя турниры. В категории я ребенок, присылаюся все турниры. В категории я взрослый, только взрослые турниры.', reply_markup=age)
            listCity.clear()

#=======================================================================================================
#ИСПРАВНО
    if SelectState == "change_city":
        
        all_city = sorted(set(main.get_all_cities()) - set(listCity))
        
        for city in all_city:
            towns.add(types.KeyboardButton(city))

        if message.text.lower() == "/start":
            bot.send_message(message.chat.id, 'Выбери города 😉', reply_markup=towns)

        if message.html_text in all_city:
            main.add_city(message.chat.id, message.html_text)
            listCity.append(message.html_text)
            bot.send_message(message.chat.id, 'Если хочешь выбрать еще города, нажми ДАЛЕЕ, если нет, то нажми СТОП', reply_markup=navigation)

        if message.html_text == 'далее':
            bot.send_message(message.chat.id, 'Выбери город', reply_markup=towns)
       
        if message.html_text == 'стоп':
            main.query_change_state("main", message.chat.id)
            SelectState = main.selectState(message.chat.id)
            bot.send_message(message.chat.id, 'Смена городов произведена успешно', reply_markup=mainButton)
            listCity.clear()
            return
          

#=======================================================================================================
#ИСПРАВНО
    if SelectState == "age_category":

        if message.text.lower() == "я ребенок (до 18 лет)":
            main.subscribe_to_child_change(message.chat.id, 1)
            welcome(message.chat, mainButton)

        if message.text.lower() == "я взрослый":
            welcome(message.chat, mainButton)
        return

#=======================================================================================================
 #ИСПРАВНО
    if SelectState == "main":

        if message.text.lower() == "/start" or message.text.lower() == "приветствие":
            bot.send_message(message.chat.id, 'Здравствуй, ' + message.chat.first_name, reply_markup=mainButton)
            return
       
        # if message.text.lower() == "/tournaments" or message.text.lower() == "все турниры":
        #     for tournament in main.all_tournaments():
        #         bot.send_message(message.chat.id, '🏆 \n' + tournament, reply_markup=mainButton)
        #     return
        
        if message.text.lower() == "/weekend_tournaments" or message.text.lower() == "турниры на выходных":
            if len(main.weekend_tournaments(message.chat.id)) == 0:
                bot.send_message(message.chat.id, 'Турниры в твоем городе на выходные не запранированы', reply_markup=mainButton)
            for flag in main.get_flag_is_child(message.chat.id):
                for tournament in main.weekend_tournaments(message.chat.id):

                    if "is_child: 0" in tournament:
                        bot.send_message(message.chat.id, 'Турнир в твоем городе на выходные... \n\n' + tournament, reply_markup=mainButton)
                        
                    if "is_child: 1" in tournament:
                        if flag[0] == 1:
                            bot.send_message(message.chat.id, 'Турнир в твоем городе на выходные... \n\n' + tournament, reply_markup=mainButton)
            return
            
        if message.text.lower() == "/my_city" or message.text.lower() == "мой город":
            for city in main.my_city(message.chat.id):
                bot.send_message(message.chat.id, city, reply_markup=mainButton)
            return
        
        if message.text.lower() == "/tournaments_in_my_city" or message.text.lower() == "турниры в моем городе": 
            if len(main.all_tournaments_in_city(message.chat.id)) == 0:
                bot.send_message(message.chat.id, 'В твоем городе пока что нет запланированных турниров :(', reply_markup=mainButton)
            for flag in main.get_flag_is_child(message.chat.id):
                for tournament in main.all_tournaments_in_city(message.chat.id):
                    
                    if "is_child: 0" in tournament:
                        bot.send_message(message.chat.id, 'Турнир в твоем городе 🏆... \n\n' + tournament, reply_markup=mainButton)
                    
                    if "is_child: 1" in tournament:
                        if flag[0] == 1:
                            bot.send_message(message.chat.id, 'Турнир в твоем городе 🏆... \n\n' + tournament, reply_markup=mainButton)
            
            return

        if message.text.lower() == "/message_to_developer" or message.text.lower() == "сообщение автору":
            main.query_change_state("message_to_developer", message.chat.id)
            SelectState = main.selectState(message.chat.id)
            bot.send_message(message.chat.id, 'Напиши разработчику об ошибках, неисправностях, и тп. Отправь сюда сообщение, чтобы я отправил его разработчику', reply_markup=types.ReplyKeyboardRemove())
            return

        if message.text.lower() == "/change_city" or message.text.lower() == "сменить город":
            main.remove_city_for_user(message.chat.id)
            main.query_change_state("change_city", message.chat.id)
            SelectState = main.selectState(message.chat.id)
            bot.send_message(message.chat.id, 'Я очистил твои города')
            bot.send_message(message.chat.id, 'Выбирай новые, если не появилась клавиатура напиши команду /start', reply_markup=towns)
            return

        if message.text.lower() == "/child_tournaments":
            for flag in main.get_flag_is_child(message.chat.id):

                if flag[0] == 0:
                    bot.send_message(message.chat.id, 'Ты подписался на рассылку детских турниров. Это можно отменить командой /become_an_adult', reply_markup=mainButton)
                    main.subscribe_to_child_change(message.chat.id, 1)
                if flag[0] == 1:
                    bot.send_message(message.chat.id, 'Ты уже находишься в детской категории', reply_markup=mainButton)

            return

        if message.text.lower() == "/become_an_adult":
            for flag in main.get_flag_is_child(message.chat.id):

                if flag[0] == 0:
                    bot.send_message(message.chat.id, 'Ты уже находишься во взрослой категории', reply_markup=mainButton)
                if flag[0] == 1:
                    main.subscribe_to_child_change(message.chat.id, 0)
                    bot.send_message(message.chat.id, 'Ты отписался от рассылки детских турниров', reply_markup=mainButton)

            return

        else: 
            bot.send_message(message.chat.id, 'Я тебя не понимаю, напиши что-нибудь другое :(')

#=======================================================================================================
  #ИСПРАВНО
    if SelectState == "message_to_developer" and message.text.lower() != "/message_to_developer": 

        bot.send_message(925936432, "Сообщение от: " + "\n" + str(message.chat.id) + "\n" + str(message.html_text))

        bot.send_message(message.chat.id, "Отправил")
        main.query_change_state("main", message.chat.id)
        bot.send_message(message.chat.id, 'Если хочешь еще раз написать разработчику, напиши команду /message_to_developer', reply_markup=mainButton)

#=======================================================================================================

def push_message():
    try:
        tournaments = main.get_new_tournaments()
        if(any(tournaments)):
            for tour in tournaments:
                if(any(tour)):
                    for cityId in main.get_cities_by_new_tournament_id(tour[0]):
                        for user in main.getUsersChatByCityId(cityId):
                            bot.send_message(user, "В твоем городе появился турнир \n" + main.getTournomentMessageById(tour[0]))

    except Exception as e:
            print(e) 
    except AssertionError:
            print( "!!!!!!! user has been blocked !!!!!!!" ) 
            # если выборка city из таблицы NEW_tournament_go 
            # есть (in) в выборке города из таблицы UserCity 
            # то выполнить запрос к таблице UserCity 
            # (выбрать id_user где city = city из таблицы NEW_tournament_go) 
            # отправить этому id сообщение о турнире

def push_message_up_to_20():
    print('empty function')
    # try:
    #     for city in main.all_cities_from_new_tournaments_20():
    #         if city in main.user_cities():
    #             for user in main.id_user_where_city_in_NEW_20():
    #                 all_tournaments = main.all_tournaments_in_city_NEW_20(user[0])
    #                 for tournament in all_tournaments:
    #                     result = main.Select_message_was_send_20(user[0], tournament[0])
    #                     if len(result) == 0:
    #                         state_child = "main_child"
    #                         if len(main.if_is_tournament_up_to_20(user[0], state_child)) != 0:
    #                             bot.send_message(user[0], "В твоем городе появился турнир \n" + tournament[1])
    #                             main.message_was_send_20(user[0], tournament[0])
    #                         else:
    #                             print()
                                
    # except Exception as e:
    #         print(e) 
    # except AssertionError:
    #         print( "!!!!!!! user has been blocked !!!!!!!" )

def log(chatID, action, level):
    data = {'chatID': chatID, 'action': action}
    logger = logging.getLogger('')
    if level == logging.INFO:
        logger.info(json.dumps(data))

def welcome(chat, mainButton):
    main.query_change_state("main", chat.id)
    SelectState = main.selectState(chat.id)
    bot.send_message(chat.id, 'Добро пожаловать 👋, ' + chat.first_name, reply_markup=mainButton)

def background():
    while True:
        main.download_page("https://gofederation.ru/tournaments/", "current.html"),  # скачивание актуальной версии турниров
        main.compare("current.html", "old.html"),  # сравнение
        main.copy_current_to_old("old.html", "current.html"),  # замена старого на новое
        #main.main(),  # запись новых турниров
        #push_message(),  # уведомление пользователей о новых турнирах
        main.delete_old_tournaments(),  # удаление устаревших по дате турниров из основной таблицы

        time.sleep(10)
        

if __name__ == '__main__':

    t1 = Thread(target=background, args=())
    t1.start()
    
    bot.polling(none_stop=True)