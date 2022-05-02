def watch_categ(call, users_table, bot):
    print('got callback watch_categ')
    str = ''
    for category in users_table[call.message.chat.id].categories:
        str += category
        if users_table[call.message.chat.id].categories[category]:
            str += ' - '
            for key_word in users_table[call.message.chat.id].categories[category]:
                str += key_word
                str += ', '
            str = str[:-2]
        str += '\n'
    print(str)
    bot.send_message(call.message.chat.id, str)


def add_categ(call, users_table, bot):
    print('got callback add_categ')
    users_table[call.message.chat.id].set_state(3)
    bot.send_message(call.message.chat.id,
                     'чтобы добавить категории и ключевые слова, отправь сообщение в таком формате\n' +
                     '[категория] - [ключевое слово 1], [ключевое слово 2]; [категория] - [ключевое слово 1]; ' +
                     '[категория]')


def del_categ(call, users_table, bot):
    print('got callback del_categ')
    users_table[call.message.chat.id].set_state(4)
    bot.send_message(call.message.chat.id,
                     'чтобы удалить категорию категорию или ключевое слово, напиши эти позиции через запятую')


def format_expence(text, chat_id):  # ret (income/outcome, sum, categoty, acc, comment)
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
