from telebot import types
from datetime import datetime
from json import JSONDecodeError
import os
import json
from google.oauth2 import service_account
import googleapiclient.discovery


class UserData:
    table = {}
    first_load = True

    def __init__(self):
        if self.first_load:
            print('loaded data first time')
            with open('data.json') as f:
                try:
                    self.table = json.load(f)
                except JSONDecodeError:
                    pass
        self.first_load = False

    def update(self):
        with open('data.json', 'w') as f:
            json.dump(self.table, f)

    def load(self):
        self.__init__()

    def __del__(self):
        self.update()
        print('__del__ for user data')


class TableManager:
    sheet_service = None
    drive_service = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    spreadsheet_body = {
        "properties": {"title": "учет финансов", "locale": "ru_RU"},
        "sheets": [
            {"properties": {"gridProperties": {"columnCount": 11, "frozenRowCount": 2}, "sheetId": 0}}
        ]
    }

    def __init__(self):
        print('def init for table manager')
        creds = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
                                                                      scopes=self.SCOPES)
        self.sheet_service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)
        self.drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)

    def delete_table(self, spreadsheet_id):
        self.drive_service.files().delete(fileId=spreadsheet_id).execute()

    def set_expense(self, user, date, expence, category, account, comment):
        try:
            self.sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=user['spreadsheet_id'], body={
                "value_input_option": "USER_ENTERED",
                "data": [
                    {
                        "range": "Лист1!A" + str(user['last_row_expence']) + ":E" + str(user['last_row_expence']),
                        "majorDimension": "ROWS",
                        "values": [
                            [date, expence, category, comment, account]
                        ]
                    }
                ]
            }).execute()
            user['last_row_expence'] += 1
            return True
        except BaseException as e:
            print("could't set expence")
            print(e)
            return False

    def set_income(self, user, date, expence, category, account, comment):
        try:
            self.sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=user['spreadsheet_id'], body={
                "value_input_option": "USER_ENTERED",
                "data": [
                    {
                        "range": "Лист1!G" + str(user['last_row_income']) + ":K" + str(user['last_row_income']),
                        "majorDimension": "ROWS",
                        "values": [
                            [date, expence, category, comment, account]
                        ]
                    }
                ]
            }).execute()
            user['last_row_income'] += 1
            return True
        except BaseException as e:
            print("could't set income")
            print(e)
            return False

    def create_table(self, user):
        created = True
        try:
            sheet = self.sheet_service.spreadsheets().create(body=self.spreadsheet_body).execute()
        except BaseException as e:
            print("tried to create a table")
            print(e)
            created = False
        if created:
            print('created sheet')
            user['spreadsheet_id'] = sheet["spreadsheetId"]
            user['sheet_link'] = sheet["spreadsheetUrl"]
            self.first_fill(user['spreadsheet_id'])
            self.drive_service.permissions().create(
                fileId=user['spreadsheet_id'],
                body={
                    'role': 'writer',
                    'type': 'user',
                    'emailAddress': user['mail'],
                    'sendNotificationEmail': False}).execute()
        return created

    def first_fill(self, spreadsheet_id):
        sheet_id = 0

        self.sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
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
        }).execute()

        self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "requests": [
                self.create_update_dim_json(0, 1, 80, sheet_id),
                self.create_update_dim_json(1, 2, 90, sheet_id),
                self.create_update_dim_json(2, 3, 140, sheet_id),
                self.create_update_dim_json(3, 4, 220, sheet_id),
                self.create_update_dim_json(4, 5, 100, sheet_id),
                self.create_update_dim_json(5, 6, 125, sheet_id),
                self.create_update_dim_json(6, 7, 80, sheet_id),
                self.create_update_dim_json(7, 8, 90, sheet_id),
                self.create_update_dim_json(8, 9, 140, sheet_id),
                self.create_update_dim_json(9, 10, 220, sheet_id),
                self.create_update_dim_json(10, 11, 100, sheet_id),
                {
                    "updateCells": {
                        "fields": "textFormatRuns,userEnteredFormat",
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 2,
                            "startColumnIndex": 0,
                            "endColumnIndex": 11
                        },
                        "rows": [
                            {
                                "values": [
                                    self.create_update_cells_json(14, True, 'CENTER'),
                                    {}, {}, {}, {}, {},
                                    self.create_update_cells_json(14, True, 'CENTER')
                                ]
                            },
                            {
                                "values": [
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    {},
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER'),
                                    self.create_update_cells_json(10, True, 'CENTER')
                                ]
                            }
                        ]
                    }
                },
                self.create_merge_cells_json(0, 1, 0, 5, sheet_id, 'MERGE_ALL'),
                self.create_merge_cells_json(0, 1, 6, 11, sheet_id, 'MERGE_ALL'),
                self.create_merge_cells_json(0, 2, 5, 6, sheet_id, 'MERGE_ALL'),
                self.create_merge_cells_json(2, -1, 5, 6, sheet_id, 'MERGE_ALL'),
            ]
        }).execute()

    @staticmethod
    def create_update_dim_json(start_id, end_id, pixel_size, sheet_id):
        return {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
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

    @staticmethod
    def create_update_cells_json(font_size, is_bold, alignment):
        return {
            "textFormatRuns": {
                "format": {"fontSize": font_size, "bold": is_bold}
            },
            "userEnteredFormat": {
                "horizontalAlignment": alignment
            }
        }

    @staticmethod
    def create_merge_cells_json(start_row_id, end_row_id, start_col_id, end_col_id, sheet_id, merge_type):
        merge_cells = {
            "mergeCells": {
                "range": {
                    "sheetId": sheet_id,
                },
                "mergeType": merge_type
            }
        }

        if start_row_id >= 0:
            merge_cells['mergeCells']['range']['startRowIndex'] = start_row_id
        if end_row_id >= 0:
            merge_cells['mergeCells']['range']['endRowIndex'] = end_row_id
        if start_col_id >= 0:
            merge_cells['mergeCells']['range']['startColumnIndex'] = start_col_id
        if end_col_id >= 0:
            merge_cells['mergeCells']['range']['endColumnIndex'] = end_col_id

        return merge_cells


def create_user():
    print('def create_user')
    return {
        'mail': '',
        'state': 1,
        'sheet_link': '',
        'spreadsheet_id': '',
        'categories': {
            'супермаркеты': [], 'кафе': ['кофе'], 'одежда': [], 'аптека': [], 'жкх': [], 'квартира': [],
            'транспорт': [], 'книги': [], 'кино': [], 'спорттовары': []
        },
        'key_words': dict(),
        'accounts': [],
        'main_acc': '',
        'subscriptions': dict(),
        'send_for_verific': True,
        'last_row_expence': 3,
        'last_row_income': 3
    }


def watch_categ(chat_id, user, bot):
    print('got callback watch_categ')
    categ_str = ''
    for category in user['categories'].keys():
        categ_str += category
        if user['categories'][category]:
            categ_str += ' - '
            for key_word in user['categories'][category]:
                categ_str += key_word
                categ_str += ', '
            categ_str = categ_str[:-2]
        categ_str += '\n'
    print(categ_str)
    user['state'] = 2
    bot.send_message(chat_id, categ_str)


def add_categ(chat_id, user, bot):
    print('got callback add_categ')
    user['state'] = 3
    bot.send_message(chat_id,
                     'чтобы добавить категории и ключевые слова, отправь сообщение в таком формате\n' +
                     '[категория] - [ключевое слово 1], [ключевое слово 2]; [категория] - [ключевое слово 1]; ' +
                     '[категория]')


def del_categ(chat_id, user, bot):
    print('got callback del_categ')
    user['state'] = 4
    bot.send_message(chat_id, 'чтобы удалить категорию категорию или ключевое слово, напиши эти позиции через запятую')


def watch_acc(chat_id, user, bot):
    print('got callback watch_acc')
    s_acc = ''
    for acc in user['accounts']:
        if acc == user['main_acc']:
            s_acc += '<b>' + acc + '</b>'
        else:
            s_acc += acc
        s_acc += '\n'
    if s_acc == '':
        s_acc = 'счета не установлены'
    print(s_acc)
    user['state'] = 2
    bot.send_message(chat_id, s_acc, parse_mode='HTML')


def set_main_acc(chat_id, user, bot):
    print('got callback set_main_acc')
    user['state'] = 5
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for acc in user['accounts']:
        keyboard.add(types.KeyboardButton(acc))
    bot.send_message(chat_id, 'чтобы установить основной счет, выбери из предложенных или напиши его название в чат',
                     reply_markup=keyboard)


def add_acc(chat_id, user, bot):
    print('got callback add_acc')
    user['state'] = 6
    bot.send_message(chat_id, 'чтобы добавить счета, отправь сообщение в таком формате\n[счет 1], [счет 2]')


def del_acc(chat_id, user, bot):
    print('got callback del_acc')
    user['state'] = 7
    bot.send_message(chat_id, 'чтобы удалить счета, напиши их через запятую')


def watch_sub(chat_id, user, bot):
    print('got callback watch_acc')
    if not user['subscriptions']:
        bot.send_message(chat_id, 'нет подписок')
    else:
        subs = ''
        for sub_name in user['subscriptions'].keys():
            subs += sub_name + ' ' + str(user['subscriptions'][sub_name]['cost']) + 'р. '
            today = datetime.today()
            est_date = datetime.strptime(user['subscriptions'][sub_name]['date'], '%d.%m.%Y')
            if est_date.day < today.day:
                new_year = today.year + today.month // 12
                new_month = (today.month % 12) + 1
                est_date = est_date.replace(month=new_month, year=new_year)
            else:
                est_date = today.replace(day=est_date.day)

            user['subscriptions'][sub_name]['date'] = est_date.strftime('%d.%m.%Y')
            subs += user['subscriptions'][sub_name]['date'] + '\n'
        bot.send_message(chat_id, subs)

    user['state'] = 2


def add_sub(chat_id, user, bot):
    print('got callback add_sub')
    user['state'] = 8
    bot.send_message(chat_id, 'чтобы добавить подписку, отправь сообщение в таком формате\n' +
                     '[день списания] [сумма] [название подписки]\n' +
                     'если хочешь добавить несколько подписок, запиши их в формате выше через запятую')


def del_sub(chat_id, user, bot):
    print('got callback del_sub')
    user['state'] = 9
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for sub in user.subscriptions.keys():
        keyboard.add(types.KeyboardButton(sub))
    keyboard.add(types.KeyboardButton('отменить действие'))
    bot.send_message(chat_id, 'чтобы удалить подписку, выбери ее из предложенных или напиши их названия через запятую',
                     reply_markup=keyboard)


def format_expence(text, user):  # ret (income/outcome, expence, category, acc, comment)
    items = text.split()

    if len(items) < 2:
        print("too few items")
        return False, False, False, False, False

    income = 0
    if items[0] == '+':
        income = 1

    expence = 0
    try:
        expence = int(items[0])
    except ValueError:
        print("value err")
        return False, False, False, False, False

    category = items[1]
    print("\tcategories: ", end='')
    print(user['categories'])
    print("\tkey words: ", end='')
    print(user['key_words'])
    print("\tcur category: " + category)
    i = 2
    while category not in user['categories'].keys() and category not in user['key_words'].keys():
        if i == len(items):
            print("cant define category")
            return False, False, False, False, False
        category += items[i]
        i += 1
    if category in user['key_words'].keys():
        category = user['key_words'][category] + ", " + category

    account = user['main_acc']
    comment = ''

    if i == len(items):
        return income, expence, category, account, comment

    if items[i] in user['accounts']:
        account = items[i]
        i += 1

    while i < len(items):
        comment += items[i] + ' '
        i += 1

    return income, expence, category, account, comment


callback_funcs = {'watch_categ': watch_categ, 'add_categ': add_categ, 'del_categ': del_categ, 'watch_acc': watch_acc,
                  'set_main_acc': set_main_acc, 'add_acc': add_acc, 'del_acc': del_acc, 'watch_sub': watch_sub,
                  'add_sub': add_sub, 'del_sub': del_sub}
