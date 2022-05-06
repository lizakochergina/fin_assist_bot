from telebot import types
from datetime import datetime


def watch_categ(chat_id, user, bot):
    print('got callback watch_categ')
    str = ''
    for category in user.categories:
        str += category
        if user.categories[category]:
            str += ' - '
            for key_word in user.categories[category]:
                str += key_word
                str += ', '
            str = str[:-2]
        str += '\n'
    print(str)
    user.set_state(2)
    bot.send_message(chat_id, str)


def add_categ(chat_id, user, bot):
    print('got callback add_categ')
    user.set_state(3)
    bot.send_message(chat_id,
                     'чтобы добавить категории и ключевые слова, отправь сообщение в таком формате\n' +
                     '[категория] - [ключевое слово 1], [ключевое слово 2]; [категория] - [ключевое слово 1]; ' +
                     '[категория]')


def del_categ(chat_id, user, bot):
    print('got callback del_categ')
    user.set_state(4)
    bot.send_message(chat_id, 'чтобы удалить категорию категорию или ключевое слово, напиши эти позиции через запятую')


def watch_acc(chat_id, user, bot):
    print('got callback watch_acc')
    str = ''
    for acc in user.accounts:
        if acc == user.main_account:
            str += '<b>' + acc + '</b>'
        else:
            str += acc
        str += '\n'
    print(str)
    user.set_state(2)
    bot.send_message(chat_id, str, parse_mode='HTML')


def set_main_acc(chat_id, user, bot):
    print('got callback set_main_acc')
    user.set_state(5)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for acc in user.accounts:
        keyboard.add(types.KeyboardButton(acc))
    bot.send_message(chat_id, 'чтобы установить основной счет, выбери из предложенных или напиши его название в чат',
                     reply_markup=keyboard)


def add_acc(chat_id, user, bot):
    print('got callback add_acc')
    user.set_state(6)
    bot.send_message(chat_id, 'чтобы добавить счета, отправь сообщение в таком формате\n[счет 1], [счет 2]')


def del_acc(chat_id, user, bot):
    print('got callback del_acc')
    user.set_state(7)
    bot.send_message(chat_id, 'чтобы удалить счета, напиши их через запятую')


def watch_sub(chat_id, user, bot):
    print('got callback watch_acc')
    if not user.subscriptions:
        bot.send_message(chat_id, 'нет подписок')
    else:
        subs = ''
        for sub_name in user.subscriptions.keys():
            subs += sub_name + ' ' + str(user.subscriptions[sub_name].cost) + 'р. '
            today = datetime.today()
            if today > user.subscriptions[sub_name].date:
                new_year = today.year + today.month // 12
                new_month = (today.month % 12) + 1
                user.subscriptions[sub_name].date = user.subscriptions[sub_name].date.replace(month=new_month,
                                                                                              year=new_year)
            subs += user.subscriptions[sub_name].date.strftime('%d.%m.%Y') + '\n'
        bot.send_message(chat_id, subs)
    user.set_state(2)


def add_sub(chat_id, user, bot):
    print('got callback add_sub')
    user.set_state(8)
    bot.send_message(chat_id, 'чтобы добавить подписку, отправь сообщение в таком формате\n' +
                     '[день списания] [сумма] [название подписки]\n' +
                     'если хочешь добавить несколько подписок, запиши их в формате выше через запятую')


def del_sub(chat_id, user, bot):
    print('got callback del_sub')
    user.set_state(9)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for sub in user.subscriptions.keys():
        keyboard.add(types.KeyboardButton(sub))
    keyboard.add(types.KeyboardButton('отменить действие'))
    bot.send_message(chat_id, 'чтобы удалить подписку, выбери ее из предложенных или напиши их названия через запятую',
                     reply_markup=keyboard)


def format_expence(text, chat_id, users_table):  # ret (income/outcome, sum, categoty, acc, comment)
    items = text.split()

    if len(items) < 2:
        print("too few items")
        return (False, False, False, False, False)

    income = 0
    if items[0] == '+':
        income = 1

    sum = 0
    try:
        sum = int(items[0])
    except ValueError:
        print("value err")
        return (False, False, False, False, False)

    category = items[1]
    print("\tcategories: ", end='')
    print(users_table[chat_id].categories)
    print("\tkey words: ", end='')
    print(users_table[chat_id].key_words)
    print("\tcur category: " + category)
    i = 2
    while category not in users_table[chat_id].categories and category not in users_table[chat_id].key_words.keys():
        if i == len(items):
            print("cant define category")
            return (False, False, False, False, False)
        category += items[i]
        ++i
    if category in users_table[chat_id].key_words.keys():
        category = users_table[chat_id].key_words[category] + ", " + category

    account = users_table[chat_id].main_account
    comment = ""

    if i == len(items):
        return (income, sum, category, account, comment)

    if items[i] in users_table[chat_id].accounts:
        account = items[i]
        i += 1

    while i < len(items):
        comment += items[i] + " "
        i += 1

    return (income, sum, category, account, comment)


callback_funcs = {'watch_categ': watch_categ, 'add_categ': add_categ, 'del_categ': del_categ, 'watch_acc': watch_acc,
                  'set_main_acc': set_main_acc, 'add_acc': add_acc, 'del_acc': del_acc, 'watch_sub': watch_sub,
                  'add_sub': add_sub, 'del_sub': del_sub}
