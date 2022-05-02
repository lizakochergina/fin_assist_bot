import os
import telebot
from google.oauth2 import service_account
import googleapiclient.discovery
import pprint
import json
from datetime import datetime
from telebot import types
from helpers import *

TELEGRAM_TOKEN = ''

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = ''
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheet_service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)
drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)
spreadsheet_body = {
    "properties": {"title": "учет финансов", "locale": "ru_RU"},
    "sheets": [
        {"properties": {"gridProperties": {"columnCount": 11, "frozenRowCount": 2}, "sheetId": 0}}
    ]
}


class TableManager:
    spreadsheet_id = 0
    sheet_id0 = 0
    last_row_expences = 3
    last_row_income = 3

    def set_id(self, ss_id):
        self.spreadsheet_id = ss_id

    def first_fill(self):
        sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "value_input_option": "USER_ENTERED",
            "data": [
                {
                    "range": "Лист1!A1:K2",
                    "majorDimension": "ROWS",
                    "values": [
                        ["расходы", "", "", "", "", "", "доходы", "", "", "", ""],
                        ["дата", "сумма", "категория", "комментарий", "счет", "", "дата", "сумма", "категория",
                         "комментарий", "счет"]
                    ]
                }
            ]
        }).execute();

        try:
            sheet_service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
                "requests": [
                    self.create_update_dim_json(0, 1, 80),
                    self.create_update_dim_json(1, 2, 90),
                    self.create_update_dim_json(2, 3, 140),
                    self.create_update_dim_json(3, 4, 220),
                    self.create_update_dim_json(4, 5, 100),
                    self.create_update_dim_json(5, 6, 125),
                    self.create_update_dim_json(6, 7, 80),
                    self.create_update_dim_json(7, 8, 90),
                    self.create_update_dim_json(8, 9, 140),
                    self.create_update_dim_json(9, 10, 220),
                    self.create_update_dim_json(10, 11, 100),
                    {
                        "updateCells": {
                            "fields": "textFormatRuns,userEnteredFormat",
                            "range": {
                                "sheetId": self.sheet_id0,
                                "startRowIndex": 0,
                                "endRowIndex": 2,
                                "startColumnIndex": 0,
                                "endColumnIndex": 11
                            },
                            "rows": [
                                {
                                    "values": [
                                        {
                                            "textFormatRuns": {
                                                "format": {"fontSize": 14, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        }, {}, {}, {}, {}, {},
                                        {
                                            "textFormatRuns": {
                                                "format": {"fontSize": 14, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "values": [
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {},
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        },
                                        {
                                            "textFormatRuns": {
                                                "startIndex": 0,
                                                "format": {"fontSize": 10, "bold": True, }
                                            },
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "CENTER"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    {
                        "mergeCells": {
                            "range": {
                                "sheetId": self.sheet_id0,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                                "startColumnIndex": 0,
                                "endColumnIndex": 5
                            },
                            "mergeType": "MERGE_ALL"
                        }
                    },
                    {
                        "mergeCells": {
                            "range": {
                                "sheetId": self.sheet_id0,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                                "startColumnIndex": 6,
                                "endColumnIndex": 11
                            },
                            "mergeType": "MERGE_ALL"
                        }
                    },
                    {
                        "mergeCells": {
                            "range": {
                                "sheetId": self.sheet_id0,
                                "startRowIndex": 0,
                                "endRowIndex": 2,
                                "startColumnIndex": 5,
                                "endColumnIndex": 6
                            },
                            "mergeType": "MERGE_ALL"
                        }
                    },
                    {
                        "mergeCells": {
                            "range": {
                                "sheetId": self.sheet_id0,
                                "startRowIndex": 2,
                                "startColumnIndex": 5,
                                "endColumnIndex": 6
                            },
                            "mergeType": "MERGE_ALL"
                        }
                    }
                ]
            }).execute()
        except BaseException as e:
            print("tried to merge data")
            print(e)

    def create_update_dim_json(self, start_id, end_id, pixel_size):
        return {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": self.sheet_id0,
                    "dimension": "COLUMNS",
                    "startIndex": start_id,
                    "endIndex": end_id
                },
                "properties": {
                    "pixelSize": pixel_size
                },
                "fields": "pixelSize"
            }
        }

    def set_expense(self, date, sum, category, account, comment):
        try:
            sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
                "value_input_option": "USER_ENTERED",
                "data": [
                    {
                        "range": "Лист1!A" + str(self.last_row_expences) + ":E" + str(self.last_row_expences),
                        "majorDimension": "ROWS",
                        "values": [
                            [date, sum, category, comment, account]  # add date!
                        ]
                    }
                ]
            }).execute();
            self.last_row_expences += 1
            return True
        except BaseException as e:
            print("could't set expence")
            print(e)
            return False

    def set_income(self, date, sum, category, account, comment):
        try:
            sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
                "value_input_option": "USER_ENTERED",
                "data": [
                    {
                        "range": "Лист1!G" + str(self.last_row_expences) + ":K" + str(self.last_row_expences),
                        "majorDimension": "ROWS",
                        "values": [
                            [date, sum, category, comment, account]  # add date!
                        ]
                    }
                ]
            }).execute();
            self.last_row_income += 1
            return True
        except BaseException as e:
            print("could't set income")
            print(e)
            return False


class UserInfo:
    mail = ''
    state = -1  # 1 - wait for email,   2 - get expences, 3 - add category, 4 - del category
    sheet_link = ''
    spreadsheet_id = 0
    perm_id = 0
    categories = {'супермаркеты': set(), 'кафе': {'кофе'}, 'одежда': set(), 'аптека': set(), 'жкх': set(),
                  'квартира': set(), 'транспорт': set(), 'книги': set(), 'кино': set(), 'спорттовары': set()}
    key_words = {'кофе': 'кафе'}
    accounts = {'тиньк', 'сбер'}
    main_account = 'тиньк'
    table_manager = TableManager()
    send_for_verific = True

    def set_state(self, new_state):
        self.state = new_state

    def set_mail(self, new_mail):
        self.mail = new_mail

    def create_table(self):
        created = True
        try:
            sheet = sheet_service.spreadsheets().create(body=spreadsheet_body).execute()
        except BaseException as e:
            print("tried to create a table")
            print(e)
            created = False
        if created:
            self.spreadsheet_id = sheet["spreadsheetId"]
            self.sheet_link = sheet["spreadsheetUrl"]
            self.table_manager.set_id(self.spreadsheet_id)
            self.table_manager.first_fill()
            perm_id = drive_service.permissions().create(fileId=self.spreadsheet_id,
                                                         body={'role': 'writer', 'type': 'user',
                                                               'emailAddress': self.mail,
                                                               "sendNotificationEmail": False}).execute()["id"]
        return created


users_table = {}  # chat id - user info()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id in users_table:
        bot.send_message(message.chat.id,
                         "у нас уже есть таблица для тебя " + users_table[message.chat.id].sheet_link)
        users_table[message.chat.id].set_state(2)  # wait for expences
        # next logic ??
    else:
        bot.send_message(message.chat.id,
                         "Привет! Сейчас я создам тебе таблицу. Для этого мне нужно, чтобы ты прислал свою gmail почту.")
        users_table[message.chat.id] = UserInfo()
        users_table[message.chat.id].set_state(1)


@bot.message_handler(commands=['reset'])
def reset(message):
    bot.send_message(message.chat.id,
                     "сейчас я удалю все данные")
    drive_service.files().delete(fileId=users_table[message.chat.id].spreadsheet_id).execute()
    users_table[message.chat.id].set_state(-1)


@bot.message_handler(
    func=lambda message: message.chat.id in users_table and users_table[message.chat.id].state == 1)
def getting_email(message):
    last_index = message.text.find('@gmail.com')
    if last_index == -1 or last_index == 0 or last_index != len(message.text) - len('@gmail.com'):
        bot.send_message(message.chat.id, 'почта некорректная, попробуй еще раз')
    else:
        users_table[message.chat.id].set_mail(message.text)
        created = users_table[message.chat.id].create_table()
        if created:
            bot.send_message(message.chat.id, 'таблица готова\n' + 'https://docs.google.com/spreadsheets/d/' +
                             users_table[message.chat.id].spreadsheet_id)
            users_table[message.chat.id].set_state(2)
            # set accounts and categories
        else:
            bot.send_message(message.chat.id, 'не получилось создать таблицу, попробуй перезапустить бота')
            users_table[message.chat.id].set_state(-1)


@bot.message_handler(commands=['categories'])
def categories_settings(message):
    keyboard = [
        [
            types.InlineKeyboardButton("посмотреть категории", callback_data='watch_categ'),
        ],
        [
            types.InlineKeyboardButton("добавить категорию, ключевое слово", callback_data='add_categ')
        ],
        [
            types.InlineKeyboardButton("удалить категорию, ключевое слово", callback_data='del_categ')
        ]
    ]

    bot.send_message(message.chat.id, 'выбери, что ты хочешь сделать',
                     reply_markup=types.InlineKeyboardMarkup(keyboard))


@bot.callback_query_handler(func=lambda call: call.data in ['watch_categ', 'add_categ', 'del_categ'])
def test_callback(call):
    print('got callback')
    print('data ' + call.data)
    if call.data == 'watch_categ':
        watch_categ(call, users_table, bot)
    elif call.data == 'add_categ':
        add_categ(call, users_table, bot)
    elif call.data == 'del_categ':
        del_categ(call, users_table, bot)


@bot.message_handler(func=lambda message: message.chat.id in users_table and users_table[message.chat.id].state == 2)
def get_expence(message):
    print("got an expence")
    print("\ttext: " + message.text)
    print("\titems: ", end='')
    print(message.text.split())

    income, sum, category, account, comment = format_expence(message.text, message.chat.id)
    if sum == False:
        bot.send_message(message.chat.id, 'некорректные данные')
        return

    res = False
    if income == 1:
        res = users_table[message.chat.id].table_manager.set_income(datetime.today().strftime('%d.%m.%Y'),
                                                                    sum, category, account, comment)
    else:
        res = users_table[message.chat.id].table_manager.set_expense(datetime.today().strftime('%d.%m.%Y'),
                                                                     sum, category, account, comment)

    if not res:
        bot.send_message(message.chat.id, 'произошла ошибка, попробуйте еще раз')
    else:
        if users_table[message.chat.id].send_for_verific:
            bot.send_message(message.chat.id,
                             "добавил следующую запись:\nсумма: " + str(sum) + "\nкатегория: " + category
                             + "\nсчет: " + account + "\nкомментарий: " + comment)
        else:
            bot.send_message(message.chat.id, 'запись добавлена успешно')


@bot.message_handler(
    func=lambda message: message.chat.id in users_table and users_table[message.chat.id].state == 3)
def adding_category(message):
    items = message.text.split(';')
    print(message.text)
    print(items)
    for item in items:
        k = item.find('-')
        if k != -1:
            cur_category = item[:k].strip(' ')
            print('cur category ' + cur_category)
            key_words = item[k + 1:].split(',')
            if cur_category not in users_table[message.chat.id].categories.keys():
                users_table[message.chat.id].categories[cur_category] = set()
            print('key words: ', end='')
            print(key_words)
            for key_word in key_words:
                users_table[message.chat.id].categories[cur_category].add(key_word.strip(' '))
                users_table[message.chat.id].key_words[key_word.strip(' ')] = cur_category
        else:
            cur_category = item.strip(' ')
            print('cur category ' + cur_category)
            if cur_category not in users_table[message.chat.id].categories.keys():
                users_table[message.chat.id].categories[cur_category] = {}
    users_table[message.chat.id].set_state(2)


@bot.message_handler(
    func=lambda message: message.chat.id in users_table and users_table[message.chat.id].state == 4)
def adding_category(message):
    items = [item.strip() for item in message.text.split(',')]
    print(message.text)
    print(items)
    for item in items:
        if item in users_table[message.chat.id].categories.keys():
            for key_word in users_table[message.chat.id].categories[item]:
                users_table[message.message.chat.id].key_words.pop(key_word)
            users_table[message.chat.id].categories.pop(item)
        elif item in users_table[message.chat.id].key_words.keys():
            category = users_table[message.chat.id].key_words[item]
            users_table[message.chat.id].key_words.pop(item)
            users_table[message.chat.id].categories[category].remove(item)
    users_table[message.chat.id].set_state(2)


bot.infinity_polling()
