import os
import telebot
from datetime import datetime
from helpers import *
# from helpers import UserData, TableManager, create_user, callback_funcs, format_expence

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'), parse_mode=None)
users_data = UserData()
table_manager = TableManager()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    users_data.load()

    s_id = str(message.chat.id)
    print('cur id ' + s_id)
    print(users_data.table)
    if s_id in users_data.table.keys():
        bot.send_message(message.chat.id, "у нас уже есть таблица для тебя\n" + users_data.table[s_id]['sheet_link'])
        users_data.table[s_id]['state'] = 2  # wait for expences
    else:
        bot.send_message(message.chat.id, "привет! для создания таблицы пришли, пожалуйста, свою gmail почту")
        users_data.table[s_id] = create_user()

        # bot.send_message(message.chat.id, 'go')
        # users_table[message.chat.id] = UserInfo()
        # users_table[message.chat.id].set_state(2)

    users_data.update()


@bot.message_handler(commands=['reset'])
def reset(message):
    users_data.load()

    s_id = str(message.chat.id)
    bot.send_message(message.chat.id, "сейчас я удалю все данные")
    table_manager.delete_table(users_data.table[s_id]['spreadsheet_id'])
    users_data.table.pop(s_id)

    users_data.update()


@bot.message_handler(commands=['table'])
def table(message):
    users_data.load()

    s_id = str(message.chat.id)
    if users_data.table[s_id]['sheet_link'] == '':
        bot.send_message(message.chat.id, "таблица еще не создана. введи команду /start")
    else:
        bot.send_message(message.chat.id, users_data.table[s_id]['sheet_link'])

    users_data.update()


@bot.message_handler(commands=['categories'])
def categories(message):
    users_data.load()

    keyboard = [
        [
            telebot.types.InlineKeyboardButton("посмотреть категории", callback_data='watch_categ'),
        ],
        [
            telebot.types.InlineKeyboardButton("добавить категорию, ключевое слово", callback_data='add_categ')
        ],
        [
            telebot.types.InlineKeyboardButton("удалить категорию, ключевое слово", callback_data='del_categ')
        ]
    ]

    bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',
                     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard))


@bot.message_handler(commands=['subscriptions'])
def subscribes(message):
    users_data.load()

    keyboard = [
        [
            telebot.types.InlineKeyboardButton("посмотреть подписки", callback_data='watch_sub'),
        ],
        [
            telebot.types.InlineKeyboardButton('добавить подписку', callback_data='add_sub')
        ],
        [
            telebot.types.InlineKeyboardButton("удалить подписку", callback_data='del_sub')
        ]
    ]

    bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',
                     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard))


@bot.message_handler(commands=['accounts'])
def accounts(message):
    users_data.load()

    keyboard = [
        [
            telebot.types.InlineKeyboardButton("посмотреть счета", callback_data='watch_acc'),
        ],
        [
            telebot.types.InlineKeyboardButton("установить основной счет", callback_data='set_main_acc')
        ],
        [
            telebot.types.InlineKeyboardButton("добавить счета", callback_data='add_acc')
        ],
        [
            telebot.types.InlineKeyboardButton("удалить счета", callback_data='del_acc')
        ]
    ]

    bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',
                     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard))


@bot.callback_query_handler(func=lambda call: call.data in ['watch_categ', 'add_categ', 'del_categ', 'watch_acc',
                                                            'set_main_acc', 'add_acc', 'del_acc', 'watch_sub',
                                                            'add_sub', 'del_sub'])
def test_callback(call):
    users_data.load()

    s_id = str(call.message.chat.id)
    print('got callback')
    print('data ' + call.data)
    callback_funcs[call.data](call.message.chat.id, users_data.table[s_id], bot)

    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 1)
def getting_email(message):
    users_data.load()

    s_id = str(message.chat.id)
    print('creating spredsheet')
    last_index = message.text.find('@gmail.com')
    if last_index == -1 or last_index == 0 or last_index != len(message.text) - len('@gmail.com'):
        bot.send_message(message.chat.id, 'почта некорректная, попробуй еще раз')
    else:
        users_data.table[s_id]['mail'] = message.text
        created = table_manager.create_table(users_data.table[s_id])
        if created:
            bot.send_message(message.chat.id, 'таблица готова\n' + 'https://docs.google.com/spreadsheets/d/' +
                             users_data.table[s_id]['spreadsheet_id'])
            users_data.table[s_id]['state'] = 2
        else:
            bot.send_message(message.chat.id, 'не получилось создать таблицу, попробуй перезапустить бота')
            users_data.table.pop(s_id)

        users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 2)
def get_expence(message):
    users_data.load()

    print("got an expence")
    print("\ttext: " + message.text)
    print("\titems: ", end='')
    print(message.text.split())

    s_id = str(message.chat.id)
    income, expence, category, account, comment = format_expence(message.text, users_data.table[s_id])
    if not expence:
        bot.send_message(message.chat.id, 'некорректные данные')
        return

    if income == 1:
        res = table_manager.set_income(users_data.table[s_id], datetime.today().strftime('%d.%m.%Y'), expence, category,
                                       account, comment)
    else:
        res = table_manager.set_expense(users_data.table[s_id], datetime.today().strftime('%d.%m.%Y'), expence,
                                        category, account, comment)

    if not res:
        bot.send_message(message.chat.id, 'произошла ошибка, попробуйте еще раз')
    else:
        if users_data.table[s_id]['send_for_verific']:
            bot.send_message(message.chat.id,
                             "добавил следующую запись:\nсумма: " + str(expence) + "\nкатегория: " + category +
                             "\nсчет: " + account + "\nкомментарий: " + comment)
        else:
            bot.send_message(message.chat.id, 'запись добавлена успешно')


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 3)
def adding_category(message):
    users_data.load()

    s_id = str(message.chat.id)
    items = message.text.split(';')
    print(message.text)
    print(items)
    for item in items:
        k = item.find('-')
        if k != -1:
            cur_category = item[:k].strip(' ')
            print('cur category ' + cur_category)
            key_words = item[k + 1:].split(',')
            if cur_category not in users_data.table[s_id]['categories'].keys():
                users_data.table[s_id]['categories'][cur_category] = []
            print('key words: ', end='')
            print(key_words)
            for key_word in key_words:
                users_data.table[s_id]['categories'][cur_category].append(key_word.strip(' '))
                users_data.table[s_id]['key_words'][key_word.strip(' ')] = cur_category
        else:
            cur_category = item.strip(' ')
            print('cur category ' + cur_category)
            if cur_category not in users_data.table[s_id]['categories'].keys():
                users_data.table[s_id]['categories'][cur_category] = []

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 4)
def deleting_category(message):
    users_data.load()

    s_id = str(message.chat.id)
    items = [item.strip() for item in message.text.split(',')]
    print(message.text)
    print(items)
    for item in items:
        if item in users_data.table[s_id]['categories'].keys():
            for key_word in users_data.table[s_id]['categories'][item]:
                users_data.table[s_id]['key_words'].pop(key_word)
            users_data.table[s_id]['categories'].pop(item)
        elif item in users_data.table[s_id]['key_words'].keys():
            category = users_data.table[s_id]['key_words'][item]
            users_data.table[s_id]['key_words'].pop(item)
            users_data.table[s_id]['categories'][category].remove(item)

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 5)
def setting_main_acc(message):
    users_data.load()

    s_id = str(message.chat.id)
    acc = message.text.strip()
    if acc not in users_data.table[s_id]['accounts']:
        users_data.table[s_id]['accounts'].append(acc)
    users_data.table[s_id]['main_acc'] = acc

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 6)
def adding_acc(message):
    users_data.load()

    s_id = str(message.chat.id)
    items = [item.strip() for item in message.text.split(',')]
    for item in items:
        if item not in users_data.table[s_id]['accounts']:
            users_data.table[s_id]['accounts'].append(item)

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 7)
def deleting_acc(message):
    users_data.load()

    s_id = str(message.chat.id)
    items = [item.strip() for item in message.text.split(',')]
    for item in items:
        if item == users_data.table[s_id]['main_acc']:
            users_data.table[s_id]['main_acc'] = ''
        users_data.table[s_id]['accounts'].remove(item)

    if users_data.table[s_id]['main_acc'] == '':
        bot.send_message(message.chat.id,
                         'ты удалил основной счет. пожалуйста, установи новый основной счет')
        callback_funcs['set_main_acc'](message.chat.id, users_data.table[s_id], bot)
    else:
        users_data.table[s_id]['state'] = 2

    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 8)
def adding_sub(message):
    users_data.load()

    s_id = str(message.chat.id)
    items = message.text.split(',')
    for item in items:
        sub = item.split()
        today = datetime.today()
        new_day = int(sub[0])
        print('day ' + sub[0])
        print('today ' + str(today.day))
        if new_day < today.day:
            new_year = today.year + today.month // 12
            new_month = (today.month % 12) + 1
            today = today.replace(day=new_day, month=new_month, year=new_year)
        else:
            today = today.replace(day=new_day)
        print('new date ' + today.strftime('%d.%m.%Y'))
        print(today.day, today.month, today.year)
        name = ' '.join(sub[2:]).strip()
        print('new sub: ' + '\'' + name + '\'  ' + today.strftime('%d.%m.%Y') + '  ' + sub[1])
        users_data.table[s_id]['subscriptions'][name] = {'date': today.strftime('%d.%m.%Y'), 'cost': int(sub[1])}

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 9)
def deleting_sub(message):
    users_data.load()

    s_id = str(message.chat.id)
    items = [item.strip() for item in message.text.split(',')]
    if items[0] != 'отменить действие':
        not_found = ''
        for item in items:
            if item in users_data.table[s_id]['subscriptions'].keys():
                users_data.table[s_id]['subscriptions'].pop(item)
            else:
                not_found += ' - ' + item + '\n'
        if not_found != '':
            bot.send_message(message.chat.id,
                             'следующие подписки не были найдены:\n' + not_found)

    users_data.table[s_id]['state'] = 2
    users_data.update()


bot.infinity_polling()
