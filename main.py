import os
import telebot
from datetime import datetime
from helpers import UserData, TableManager, callback_funcs, format_expense, update_cur_stat, add_new_record, \
    update_cur_stat_after_del

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'), parse_mode=None)
users_data = UserData()
table_manager = TableManager()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    s_id = str(message.chat.id)
    print('cur id ' + s_id)
    print(users_data.table)
    if s_id in users_data.table.keys() and users_data.table[s_id]['sheet_link'] != '':
        bot.send_message(message.chat.id, "у нас уже есть таблица для тебя\n" + users_data.table[s_id]['sheet_link'])
        users_data.table[s_id]['state'] = 2
    else:
        bot.send_message(message.chat.id, "привет! для создания таблицы пришли, пожалуйста, свою gmail почту")
        users_data.create_user(s_id)
    users_data.update()


@bot.message_handler(commands=['reset'])
def reset(message):
    s_id = str(message.chat.id)
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('удалить данные'))
    keyboard.add(telebot.types.KeyboardButton('отмена'))
    users_data.table[s_id]['state'] = 10
    bot.send_message(message.chat.id, "подтверди безвозвратное удаление данных", reply_markup=keyboard)
    users_data.update()


@bot.message_handler(commands=['table'])
def table(message):
    s_id = str(message.chat.id)
    if users_data.table[s_id]['sheet_link'] == '':
        bot.send_message(message.chat.id, "таблица еще не создана. введи команду /start")
    else:
        bot.send_message(message.chat.id, users_data.table[s_id]['sheet_link'])


@bot.message_handler(commands=['balance'])
def get_balance(message):
    s_id = str(message.chat.id)
    callback_funcs['watch_acc'](message.chat.id, users_data.table[s_id], bot)


@bot.message_handler(commands=['del'])
def del_record(message):
    s_id = str(message.chat.id)
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('удалить запись расхода'))
    keyboard.add(telebot.types.KeyboardButton('удалить запись дохода'))
    keyboard.add(telebot.types.KeyboardButton('отменить действие'))
    users_data.table[s_id]['state'] = 21
    users_data.update()
    bot.send_message(message.chat.id, 'Выбери, какую последнюю запись ты хочешь удалить.', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def support(message):
    keyboard = [
        [
            telebot.types.InlineKeyboardButton("инструкция", callback_data='instruction'),
        ],
        [
            telebot.types.InlineKeyboardButton("написать сообщение в поддержку", callback_data='support')
        ]
    ]

    bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',
                     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard))


@bot.message_handler(commands=['brief'])
def get_brief(message):
    s_id = str(message.chat.id)
    update_cur_stat(users_data.table[s_id], '_expense', 0, datetime.today())
    update_cur_stat(users_data.table[s_id], '_income', 0, datetime.today())
    res = ''
    res += 'траты за сегодняшний день ' + str(users_data.table[s_id]['today_expense']) + '\n'
    res += 'доход за сегодняшний день ' + str(users_data.table[s_id]['today_income']) + '\n\n'

    res += 'траты за текущий месяц ' + str(users_data.table[s_id]['cur_month_expense']) + '\n'
    res += 'доход за текущий месяц ' + str(users_data.table[s_id]['cur_month_income']) + '\n\n'

    res += 'траты за предыдущий месяц ' + str(users_data.table[s_id]['last_month_expense']) + '\n'
    res += 'доход за предыдущий месяц ' + str(users_data.table[s_id]['last_month_income'])

    users_data.update()
    bot.send_message(message.chat.id, res)


@bot.message_handler(commands=['stat'])
def get_stat(message):
    s_id = str(message.chat.id)
    users_data.table[s_id]['state'] = 12
    users_data.update()
    bot.send_message(message.chat.id, 'необходимо выбрать период. отправь две даты в формате\nдд.мм.гггг - дд.мм.гггг')


@bot.message_handler(commands=['categories'])
def categories(message):
    keyboard = [
        [
            telebot.types.InlineKeyboardButton("посмотреть категории", callback_data='watch_categ'),
        ],
        [
            telebot.types.InlineKeyboardButton("добавить категорию,\nключевое слово расхода",
                                               callback_data='add_categ_out')
        ],
        [
            telebot.types.InlineKeyboardButton("добавить категорию,\nключевое слово дохода",
                                               callback_data='add_categ_in')
        ],
        [
            telebot.types.InlineKeyboardButton("удалить категорию, ключевое слово", callback_data='del_categ')
        ]
    ]

    bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',
                     reply_markup=telebot.types.InlineKeyboardMarkup(keyboard))


@bot.message_handler(commands=['subs'])
def subscribes(message):
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


@bot.callback_query_handler(func=lambda call: call.data in ['watch_categ', 'add_categ_out', 'add_categ_in', 'del_categ',
                                                            'watch_acc', 'set_main_acc', 'add_acc', 'del_acc',
                                                            'watch_sub', 'add_sub', 'del_sub', 'instruction',
                                                            'support', 'cost_distrib', 'cost_dyn', 'cancel'])
def test_callback(call):
    s_id = str(call.message.chat.id)
    print('got callback')
    print('data ' + call.data)
    callback_funcs[call.data](call.message.chat.id, users_data.table[s_id], bot)
    bot.answer_callback_query(call.message.chat.id, text='answered callback ' + s_id)
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 1)
def getting_email(message):
    s_id = str(message.chat.id)
    print('creating spreadsheet')
    last_index = message.text.find('@gmail.com')
    if last_index == -1 or last_index == 0 or last_index != len(message.text) - len('@gmail.com'):
        bot.send_message(message.chat.id, 'почта некорректная, попробуй еще раз')
    else:
        users_data.table[s_id]['mail'] = message.text
        created = table_manager.create_table(users_data.table[s_id])
        if created:
            bot.send_message(message.chat.id, 'таблица готова\n' + 'https://docs.google.com/spreadsheets/d/' +
                             users_data.table[s_id]['spreadsheet_id'] + '\nдалее необходимо настроить таблицу. ' +
                             'прочитай, пожалуйста, инструкцию https://telegra.ph/finance-bot-05-15')
            users_data.table[s_id]['state'] = 2
        else:
            bot.send_message(message.chat.id, 'не получилось создать таблицу, попробуй перезапустить бота')
            users_data.table.pop(s_id)

        users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 2)
def get_expense(message):
    print("got an expense")
    print("\ttext: " + message.text)
    print("\titems: ", end='')
    print(message.text.split())

    s_id = str(message.chat.id)
    if users_data.table[s_id]['main_acc'] == '':
        bot.send_message(message.chat.id, 'не установлен основной счет')
        return

    income, expense, category, account, comment, approx_category = format_expense(message.text, users_data.table[s_id])
    if not expense:
        bot.send_message(message.chat.id, 'некорректные данные')
        return

    if not approx_category:
        add_new_record(s_id, users_data.table[s_id], bot, table_manager, income, expense, category, account, comment)
        users_data.update()
    else:
        users_data.table[s_id]['state'] = 20
        users_data.update()
        users_data.save_record(s_id, income, expense, category, account, comment)
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('добавить запись'))
        keyboard.add(telebot.types.KeyboardButton('отменить действие'))
        bot.send_message(message.chat.id,
                         'Категория указана неверно. Добавить следующую запись?\n\nсумма: ' + str(expense) +
                         '\nкатегория: ' + category + '\nсчет: ' + account + '\nкомментарий: ' + comment,
                         reply_markup=keyboard)


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     (users_data.table[str(message.chat.id)]['state'] == 30 or
                      users_data.table[str(message.chat.id)]['state'] == 31))
def adding_category(message):
    if users_data.table[str(message.chat.id)]['state'] == 30:
        major_category = '_out'
    else:
        major_category = '_in'

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
            if cur_category not in users_data.table[s_id]['categories' + major_category].keys():
                users_data.table[s_id]['categories' + major_category][cur_category] = []
            print('key words: ', end='')
            print(key_words)
            for key_word in key_words:
                users_data.table[s_id]['categories' + major_category][cur_category].append(key_word.strip(' '))
                users_data.table[s_id]['key_words' + major_category][key_word.strip(' ')] = cur_category
        else:
            cur_category = item.strip(' ')
            print('cur category ' + cur_category)
            if cur_category not in users_data.table[s_id]['categories' + major_category].keys():
                users_data.table[s_id]['categories' + major_category][cur_category] = []

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 4)
def deleting_category(message):
    s_id = str(message.chat.id)
    items = [item.strip() for item in message.text.split(',')]
    print(message.text)
    print(items)
    non_del = ''
    for item in items:
        if item[0] == '+':
            major_category = '_in'
            item = item[1:]
        else:
            major_category = '_out'

        if item in users_data.table[s_id]['categories' + major_category].keys():
            for key_word in users_data.table[s_id]['categories' + major_category][item]:
                users_data.table[s_id]['key_words' + major_category].pop(key_word)
            users_data.table[s_id]['categories' + major_category].pop(item)
        elif item in users_data.table[s_id]['key_words' + major_category].keys():
            category = users_data.table[s_id]['key_words' + major_category][item]
            users_data.table[s_id]['key_words' + major_category].pop(item)
            users_data.table[s_id]['categories' + major_category][category].remove(item)
        else:
            non_del += item + '\n'

    if non_del != '':
        bot.send_message(message.chat.id, 'не получилось найти и удалить следующие категории:\n' + non_del)

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 5)
def setting_main_acc(message):
    s_id = str(message.chat.id)
    acc = message.text.strip()
    if acc not in users_data.table[s_id]['accounts'].keys():
        items = message.text.split()
        balance = items[-1]
        new_acc = message.text[:-len(balance)].strip()
        try:
            users_data.table[s_id]['accounts'][new_acc] = int(balance)
            users_data.table[s_id]['main_acc'] = new_acc
        except ValueError:
            print("def setting_main_acc, can't cast balance")
            users_data.table[s_id]['state'] = 2
            bot.send_message(message.chat.id, 'произошла ошибка, попробуй еще раз')
            return
    else:
        users_data.table[s_id]['main_acc'] = acc

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 6)
def adding_acc(message):
    s_id = str(message.chat.id)
    undef = ''
    items = message.text.split(',')
    print(items)
    for item in items:
        balance = item.split()[-1].strip()
        acc = item[:-len(balance)].strip()
        print(item, balance, acc)
        try:
            users_data.table[s_id]['accounts'][acc] = int(balance)
        except ValueError:
            print("def adding_acc, can't cast balance")
            undef += acc + '\n'

    if undef != '':
        bot.send_message(message.chat.id, 'не удалось установить следующие счета:\n' + undef)

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 7)
def deleting_acc(message):
    s_id = str(message.chat.id)
    if message.text != 'отменить действие':
        items = [item.strip() for item in message.text.split(',')]
        for item in items:
            if item == users_data.table[s_id]['main_acc']:
                users_data.table[s_id]['main_acc'] = ''
            users_data.table[s_id]['accounts'].pop(item)

        if users_data.table[s_id]['main_acc'] == '':
            users_data.update()
            bot.send_message(message.chat.id,
                             'ты удалил основной счет. пожалуйста, установи новый основной счет')
            callback_funcs['set_main_acc'](message.chat.id, users_data.table[s_id], bot)
        else:
            users_data.table[s_id]['state'] = 2

    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 8)
def adding_sub(message):
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


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 10)
def deleting_all(message):
    s_id = str(message.chat.id)
    if message.text == 'удалить данные':
        table_manager.delete_table(users_data.table[s_id]['spreadsheet_id'])
        users_data.table.pop(s_id)
    else:
        users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 11)
def get_complain(message):
    s_id = str(message.chat.id)
    bot.send_message(os.getenv('SUPPORT_CHAT_ID'), '<b>SUPPORT MESSAGE</b>\n' + 'user chat id ' + s_id + '\n' +
                     message.text, parse_mode='HTML')
    bot.send_message(message.chat.id, 'сообщение успешно отправлено')
    users_data.table[s_id]['state'] = 2
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 12)
def get_date(message):
    s_id = str(message.chat.id)
    items = message.text.split('-')
    print(items)

    if len(items) != 2:
        bot.send_message(message.chat.id, 'некорректные данные')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return

    try:
        start_date = datetime.strptime(items[0].strip(), '%d.%m.%Y')
        end_date = datetime.strptime(items[1].strip(), '%d.%m.%Y')
    except ValueError:
        bot.send_message(message.chat.id, 'некоректные данные')
        return

    if start_date > end_date:
        bot.send_message(message.chat.id, 'первая дата должна быть меньше второй')
        return

    users_data.create_new_stat(s_id, start_date, end_date)
    users_data.table[s_id]['state'] = 13
    users_data.update()

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('распределение трат'))
    keyboard.add(telebot.types.KeyboardButton('динамика трат'))
    keyboard.add(telebot.types.KeyboardButton('отменить действие'))
    bot.send_message(message.chat.id, 'выбери, что ты хочешь получить', reply_markup=keyboard)


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 13)
def get_distrib(message):
    s_id = str(message.chat.id)
    print(message.text)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return
    elif message.text == 'распределение трат':
        users_data.tmp_table[s_id]['type'] = 'get_distrib'
    elif message.text == 'динамика трат':
        users_data.tmp_table[s_id]['type'] = 'get_dynamic'
    else:
        bot.send_message(message.chat.id, 'некорректные данные, необходимо начать заново')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('все'))
    keyboard.add(telebot.types.KeyboardButton('указать счета'))
    keyboard.add(telebot.types.KeyboardButton('отменить действие'))
    bot.send_message(message.chat.id, 'выбери счета, по которым хочешь получить аналитику', reply_markup=keyboard)
    users_data.table[s_id]['state'] = 14
    users_data.update()


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 14)
def get_accounts_for_stat(message):
    s_id = str(message.chat.id)
    print(message.text)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return
    elif message.text == 'все':
        users_data.table[s_id]['state'] = 15
        users_data.update()
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        if users_data.tmp_table[s_id]['type'] == 'get_dynamic':
            keyboard.add(telebot.types.KeyboardButton('общая динамика'))
        keyboard.add(telebot.types.KeyboardButton('все категории'))
        keyboard.add(telebot.types.KeyboardButton('указать категории'))
        keyboard.add(telebot.types.KeyboardButton('отменить действие'))
        bot.send_message(message.chat.id, 'выбери категории', reply_markup=keyboard)
    elif message.text == 'указать счета':
        callback_funcs['watch_acc'](message.chat.id, users_data.table[s_id], bot)
        callback_funcs['get_accs_for_analytics'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
    else:
        bot.send_message(message.chat.id, 'некорректные данные, необходимо начать заново')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 15)
def get_parameters(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return
    elif message.text == 'общая динамика':
        users_data.tmp_table[s_id]['full_targets'] = True
        users_data.table[s_id]['state'] = 2
        users_data.update()
        callback_funcs[users_data.tmp_table[s_id]['type']](message.chat.id, users_data.table[s_id]['spreadsheet_id'],
                                                           users_data.tmp_table[s_id], bot, table_manager)
        users_data.clear_stat(s_id)
    elif message.text == 'все категории':
        users_data.tmp_table[s_id]['global_targets'] = list(users_data.table[s_id]['categories_out'].keys())
        users_data.table[s_id]['state'] = 2
        users_data.update()
        callback_funcs[users_data.tmp_table[s_id]['type']](message.chat.id, users_data.table[s_id]['spreadsheet_id'],
                                                           users_data.tmp_table[s_id], bot, table_manager)
        users_data.clear_stat(s_id)
    elif message.text == 'указать категории':
        callback_funcs['watch_categ'](message.chat.id, users_data.table[s_id], bot)
        callback_funcs['get_categories_for_analytics'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
    else:
        bot.send_message(message.chat.id, 'некоректные данные')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 16)
def get_categories_for_stat(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return

    user = users_data.table[s_id]
    non_def = ''
    items = [item.strip() for item in message.text.split(',')]
    for item in items:
        if item[-1] == '+':
            categ = item[:-1]
            if categ in user['categories_out'].keys():
                users_data.tmp_table[s_id]['local_targets'].append(categ)
                for key_word in user['categories_out'][categ]:
                    users_data.tmp_table[s_id]['local_targets'].append(categ + ', ' + key_word)
            else:
                non_def += categ + '\n'
        elif item in user['categories_out'].keys():
            users_data.tmp_table[s_id]['global_targets'].append(item)
        elif item in user['key_words_out'].keys():
            users_data.tmp_table[s_id]['global_targets'].append(user['key_words_out'][item] + ', ' + item)
        else:
            non_def += item + '\n'

    if non_def == '' and (users_data.tmp_table[s_id]['global_targets'] or users_data.tmp_table[s_id]['local_targets']):
        users_data.table[s_id]['state'] = 2
        users_data.update()
        callback_funcs[users_data.tmp_table[s_id]['type']](message.chat.id, users_data.table[s_id]['spreadsheet_id'],
                                                           users_data.tmp_table[s_id], bot, table_manager)  # args ???
        users_data.clear_stat(s_id)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)

        error_str = ''
        if not users_data.tmp_table[s_id]['local_targets'] and not users_data.tmp_table[s_id]['global_targets']:
            error_str = 'слишком мало категорий'

        if non_def != '':
            if error_str != '':
                error_str += ' и '
            else:
                keyboard.add(telebot.types.KeyboardButton('все равно получить аналитику'))
            error_str += 'не удалось определить следующие категории:\n' + non_def

        keyboard.add(telebot.types.KeyboardButton('написать категории заново'))
        keyboard.add(telebot.types.KeyboardButton('отменить действие'))
        users_data.table[s_id]['state'] = 17
        users_data.update()
        bot.send_message(message.chat.id, error_str + '\nвыбери, что ты хочешь сделать', reply_markup=keyboard)


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 17)
def type_categories_again(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return
    elif message.text == 'написать категории заново':
        callback_funcs['watch_categ'](message.chat.id, users_data.table[s_id], bot)
        callback_funcs['get_categories_for_analytics'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
    elif message.text == 'все равно получить аналитику':
        users_data.table[s_id]['state'] = 2
        users_data.update()
        callback_funcs[users_data.tmp_table[s_id]['type']](message.chat.id, users_data.table[s_id]['spreadsheet_id'],
                                                           users_data.tmp_table[s_id], bot, table_manager)
        users_data.clear_stat(s_id)
    else:
        bot.send_message(message.chat.id, 'некорректные данные')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 18)
def get_accs_for_stat(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return

    non_def = ''
    items = [item.strip() for item in message.text.split(',')]
    for item in items:
        if item in users_data.table[s_id]['accounts'].keys():
            users_data.tmp_table[s_id]['accounts'].append(item)
        else:
            non_def += item + '\n'

    if non_def == '' and users_data.tmp_table[s_id]['accounts']:
        if len(users_data.tmp_table[s_id]['accounts']) == len(users_data.table[s_id]['accounts'].keys()):
            users_data.tmp_table[s_id]['accounts'].clear()
        users_data.table[s_id]['state'] = 15
        users_data.update()
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        if users_data.tmp_table[s_id]['type'] == 'get_dynamic':
            keyboard.add(telebot.types.KeyboardButton('общая динамика'))
        keyboard.add(telebot.types.KeyboardButton('все категории'))
        keyboard.add(telebot.types.KeyboardButton('указать категории'))
        keyboard.add(telebot.types.KeyboardButton('отменить действие'))
        bot.send_message(message.chat.id, 'выбери категории', reply_markup=keyboard)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)

        error_str = ''
        if not users_data.tmp_table[s_id]['accounts']:
            error_str = 'указано слишком мало счетов'

        if non_def != '':
            if error_str != '':
                error_str += ' и '
            else:
                keyboard.add(telebot.types.KeyboardButton('все равно получить аналитику'))
            error_str += 'не удалось определить следующие категории:\n' + non_def

        keyboard.add(telebot.types.KeyboardButton('написать счета заново'))
        keyboard.add(telebot.types.KeyboardButton('отменить действие'))
        users_data.table[s_id]['state'] = 19
        users_data.update()
        bot.send_message(message.chat.id, error_str + '\nвыбери, что ты хочешь сделать', reply_markup=keyboard)


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 19)
def type_accounts_again(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return
    elif message.text == 'написать счета заново':
        callback_funcs['watch_acc'](message.chat.id, users_data.table[s_id], bot)
        callback_funcs['get_accs_for_analytics'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
    elif message.text == 'все равно получить аналитику':
        users_data.table[s_id]['state'] = 15
        users_data.update()
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('все'))
        keyboard.add(telebot.types.KeyboardButton('указать категории'))
        keyboard.add(telebot.types.KeyboardButton('отменить действие'))
        bot.send_message(message.chat.id, 'выбери категории', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'некорректные данные')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 20)
def add_record_cont(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
        users_data.update()
        return
    elif message.text == 'добавить запись':
        add_new_record(s_id, users_data.table[s_id], bot, table_manager, users_data.records_table[s_id]['income'],
                       users_data.records_table[s_id]['expense'], users_data.records_table[s_id]['category'],
                       users_data.records_table[s_id]['account'], users_data.records_table[s_id]['comment'])
        users_data.update()
        return
    else:
        bot.send_message(message.chat.id, 'некорректные данные')
        users_data.table[s_id]['state'] = 2
        users_data.update()
        return


@bot.message_handler(func=lambda message:
                     str(message.chat.id) in users_data.table.keys() and
                     users_data.table[str(message.chat.id)]['state'] == 21)
def del_record_major(message):
    s_id = str(message.chat.id)
    if message.text == 'отменить действие':
        callback_funcs['cancel'](message.chat.id, users_data.table[s_id], bot)
    elif message.text == 'удалить запись расхода':
        if users_data.table[s_id]['last_row_expense'] > 3:
            response, date, summa, acc = table_manager.delete_last(users_data.table[s_id], 'expense')
            if response:
                bot.send_message(message.chat.id, 'Удалил успешно.')
                update_cur_stat_after_del(users_data.table[s_id], '_expense', -summa,
                                          datetime.strptime(date, '%d.%m.%Y'))
                if acc in users_data.table[s_id]['accounts'].keys():
                    users_data.table[s_id]['accounts'][acc] += summa

            else:
                bot.send_message(message.chat.id, 'Произошла ошибка, попробуй еще раз.')
        else:
            bot.send_message(message.chat.id, 'Записей нет.')
    elif message.text == 'удалить запись дохода':
        if users_data.table[s_id]['last_row_income'] > 3:
            response, date, summa, acc = table_manager.delete_last(users_data.table[s_id], 'income')
            if response:
                bot.send_message(message.chat.id, 'Удалил успешно.')
                update_cur_stat_after_del(users_data.table[s_id], '_income', summa,
                                          datetime.strptime(date, '%d.%m.%Y'))
                if acc in users_data.table[s_id]['accounts'].keys():
                    users_data.table[s_id]['accounts'][acc] -= summa
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка, попробуй еще раз.')
        else:
            bot.send_message(message.chat.id, 'Записей нет.')
    else:
        bot.send_message(message.chat.id, 'некорректные данные')

    users_data.table[s_id]['state'] = 2
    users_data.update()


bot.infinity_polling()
