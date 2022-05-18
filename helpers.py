import io
from googleapiclient.http import MediaIoBaseDownload
from telebot import types
from datetime import datetime
from datetime import date
from json import JSONDecodeError
import os
import json
from google.oauth2 import service_account
import googleapiclient.discovery
from analytics import count_distrib, count_dynamic
from thefuzz import process


class UserData:
    table = {}
    tmp_table = {}
    records_table = {}

    def __init__(self):
        print('loaded data first time')
        with open('data.json') as f:
            try:
                self.table = json.load(f)
            except JSONDecodeError:
                pass

    def update(self):
        with open('data.json', 'w') as f:
            json.dump(self.table, f)

    def create_user(self, s_id):
        self.table[s_id] = {
            'mail': '',
            'state': 1,
            'sheet_link': '',
            'spreadsheet_id': '',
            'categories_out': {
                'супермаркеты': [], 'кафе': [], 'одежда': [], 'аптека': [], 'жкх': [], 'квартира': [],
                'транспорт': [], 'книги': [], 'кино': []
            },
            'categories_in': {
                'зарплата': []
            },
            'key_words_out': dict(),
            'key_words_in': dict(),
            'accounts': dict(),
            'main_acc': '',
            'subscriptions': dict(),
            'send_for_verific': True,
            'last_row_expense': 3,
            'last_row_income': 3,
            'today_expense': 0,
            'today_income': 0,
            'cur_month_expense': 0,
            'cur_month_income': 0,
            'last_month_expense': 0,
            'last_month_income': 0,
            'day': date.today().day,
            'month': date.today().month,
            'year': date.today().year
        }

    def create_new_stat(self, s_id, start, end):
        self.tmp_table[s_id] = {
            'start_date': start,
            'end_date': end,
            'type': '',
            'full_targets': False,
            'local_targets': [],
            'global_targets': [],
            'accounts': set()
        }

    def clear_stat(self, s_id):
        self.tmp_table[s_id] = {}

    def save_record(self, s_id, income, expense, category, account, comment):
        self.records_table[s_id] = {
            'income': income,
            'expense': expense,
            'category': category,
            'account': account,
            'comment': comment
        }


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
    ranges = {
        'expense': {'left': 'A', 'right': 'E'},
        'income': {'left': 'G', 'right': 'K'},
    }

    def __init__(self):
        print('def init for table manager')
        creds = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
                                                                      scopes=self.SCOPES)
        self.sheet_service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)
        self.drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)

    def delete_table(self, spreadsheet_id):
        self.drive_service.files().delete(fileId=spreadsheet_id).execute()

    def download_table(self, spreadsheet_id):
        print(spreadsheet_id)
        request = self.drive_service.files().export(fileId=spreadsheet_id, mimeType='text/csv')
        fh = io.FileIO(spreadsheet_id + '.csv', 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %.2f%%." % (status.progress() * 100.0))
        fh.close()

    def delete_last(self, user, kind):
        row = str(user['last_row_' + kind] - 1)
        response, date, summa, acc = self.get_values(user, kind)
        if response:
            try:
                self.sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=user['spreadsheet_id'], body={
                    "value_input_option": "USER_ENTERED",
                    "data": [
                        {
                            "range": "Лист1!" + self.ranges[kind]['left'] + row + ":" +
                                     self.ranges[kind]['right'] + row,
                            "majorDimension": "ROWS",
                            "values": [
                                ['', '', '', '', '']
                            ]
                        }
                    ]
                }).execute()
                user['last_row_' + kind] -= 1
                return True, date, float(summa), acc
            except BaseException as e:
                print("could't set expense")
                print(e)
                return False, None, None, None
        else:
            return False, None, None, None

    def get_values(self, user, kind):
        row = str(user['last_row_' + kind] - 1)
        try:
            response = self.sheet_service.spreadsheets().values().get(
                spreadsheetId=user['spreadsheet_id'],
                range="Лист1!" + self.ranges[kind]['left'] + row + ":" + self.ranges[kind]['right'] + row,
                majorDimension="ROWS",
            ).execute()
            print(response['values'])
            date, summa, categ, comment, acc = response['values'][0]
            return True, date, summa, acc
        except BaseException as e:
            print("could't get values")
            print(e)
            return False, None, None, None

    def set_expense(self, user, date, expense, category, account, comment):
        try:
            self.sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=user['spreadsheet_id'], body={
                "value_input_option": "USER_ENTERED",
                "data": [
                    {
                        "range": "Лист1!A" + str(user['last_row_expense']) + ":E" + str(user['last_row_expense']),
                        "majorDimension": "ROWS",
                        "values": [
                            [date, expense, category, comment, account]
                        ]
                    }
                ]
            }).execute()
            user['last_row_expense'] += 1
            return True
        except BaseException as e:
            print("could't set expense")
            print(e)
            return False

    def set_income(self, user, date, income, category, account, comment):
        try:
            self.sheet_service.spreadsheets().values().batchUpdate(spreadsheetId=user['spreadsheet_id'], body={
                "value_input_option": "USER_ENTERED",
                "data": [
                    {
                        "range": "Лист1!G" + str(user['last_row_income']) + ":K" + str(user['last_row_income']),
                        "majorDimension": "ROWS",
                        "values": [
                            [date, income, category, comment, account]
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


def watch_categ(chat_id, user, bot):
    print('got callback watch_categ')

    majors = ['_out', '_in']
    categ_str = '<b>расходы</b>\n'
    for major in majors:
        for category in user['categories' + major].keys():
            categ_str += category
            if user['categories' + major][category]:
                categ_str += ' - '
                for key_word in user['categories' + major][category]:
                    categ_str += key_word
                    categ_str += ', '
                categ_str = categ_str[:-2]
            categ_str += '\n'
        if major == '_out':
            categ_str += '\n<b>доходы</b>\n'

    print(categ_str)
    user['state'] = 2
    bot.send_message(chat_id, categ_str, parse_mode='HTML')


def add_categ_out(chat_id, user, bot):
    print('got callback add_categ out')
    user['state'] = 30
    bot.send_message(chat_id,
                     'чтобы добавить категории и ключевые слова, отправь сообщение в таком формате\n' +
                     '[категория] - [ключевое слово 1], [ключевое слово 2]; [категория] - [ключевое слово 1]; ' +
                     '[категория]')


def add_categ_in(chat_id, user, bot):
    print('got callback add_categ in')
    user['state'] = 31
    bot.send_message(chat_id,
                     'чтобы добавить категории и ключевые слова, отправь сообщение в таком формате\n' +
                     '[категория] - [ключевое слово 1], [ключевое слово 2]; [категория] - [ключевое слово 1]; ' +
                     '[категория]')


def del_categ(chat_id, user, bot):
    print('got callback del_categ')
    user['state'] = 4
    bot.send_message(chat_id, 'чтобы удалить категорию категорию или ключевое слово из раздела доходов, ' +
                     'напиши эти позиции через запятую\n' + 'чтобы удалить категорию категорию или ключевое ' +
                     'слово из раздела расходов, напиши перед категорией знак <b>+</b>', parse_mode='HTML')


def watch_acc(chat_id, user, bot):
    print('got callback watch_acc')
    print(user['accounts'])
    s_acc = ''
    for acc in user['accounts'].keys():
        if acc == user['main_acc']:
            s_acc += '<b>' + acc + '</b>'
        else:
            s_acc += acc
        s_acc += '  ' + str(user['accounts'][acc]) + '\n'
    if s_acc == '':
        s_acc = 'счета не установлены'
    print(s_acc)
    user['state'] = 2
    bot.send_message(chat_id, s_acc, parse_mode='HTML')


def set_main_acc(chat_id, user, bot):
    print('got callback set_main_acc')
    user['state'] = 5
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for acc in user['accounts'].keys():
        keyboard.add(types.KeyboardButton(acc))
    bot.send_message(chat_id, 'чтобы установить основной счет, выбери из предложенных или напиши его название в чат ' +
                     'в формате\n[название счета] [баланс]', reply_markup=keyboard)


def add_acc(chat_id, user, bot):
    print('got callback add_acc')
    user['state'] = 6
    bot.send_message(chat_id, 'чтобы добавить счета, отправь сообщение в таком формате\n[счет 1] [баланс 1], ' +
                     '[счет 2] [баланс 2]')


def del_acc(chat_id, user, bot):
    print('got callback del_acc')
    user['state'] = 7
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    for acc in user['accounts'].keys():
        keyboard.add(types.KeyboardButton(acc))
    keyboard.add(types.KeyboardButton('отменить действие'))
    bot.send_message(chat_id, 'чтобы удалить счета, выбери из предложенных или напиши их названия через запятую',
                     reply_markup=keyboard)


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


def format_expense(text, user):  # ret (income/outcome, expense, category, acc, comment)
    items = text.split()

    if len(items) < 2:
        print("too few items")
        return False, False, False, False, False

    if items[0] == '+':
        print("incorrect format")
        return False, False, False, False, False

    income = 0
    major = '_out'
    if items[0][0] == '+':
        income = 1
        items[0] = items[0][1:]
        major = '_in'

    if items[0] < '0' or items[0] > '9':
        print('too many symbols')
        return False, False, False, False, False, False

    try:
        expense = int(items[0])
    except ValueError:
        print("value err")
        return False, False, False, False, False, False

    category = items[1]
    print("\tcategories: ", end='')
    print(user['categories' + major])
    print("\tkey words: ", end='')
    print(user['key_words' + major])
    print("\tcur category: " + category)
    i = 2
    maybe_categ = ''
    ratio = 0
    k = -1
    while category not in user['categories' + major].keys() and category not in user['key_words' + major].keys():
        print(category, end=' ')

        cur_maybe_categ, cur_ratio = process.extractOne(category, user['categories' + major].keys())
        print(cur_maybe_categ, cur_ratio, end=' ')
        if cur_ratio > ratio:
            ratio = cur_ratio
            maybe_categ = cur_maybe_categ
            k = i

        if user['key_words' + major].keys():
            cur_maybe_categ, cur_ratio = process.extractOne(category, user['key_words' + major].keys())
            print(cur_maybe_categ, cur_ratio, end=' ')
            if cur_ratio > ratio:
                ratio = cur_ratio
                maybe_categ = cur_maybe_categ
                k = i

        if i == len(items):
            break

        category += ' ' + items[i]
        i += 1

    print('k, maybe categ', k, maybe_categ)

    approx_category = False
    if category not in user['categories' + major].keys() and category not in user['key_words' + major].keys():
        category = maybe_categ
        i = k
        approx_category = True

    if category in user['key_words' + major].keys():
        category = user['key_words' + major][category] + ", " + category

    account = user['main_acc']
    comment = ''

    if i == len(items):
        return income, expense, category, account, comment, approx_category

    if items[i] in user['accounts'].keys():
        account = items[i]
        i += 1

    while i < len(items):
        comment += items[i] + ' '
        i += 1

    return income, expense, category, account, comment, approx_category


def get_instruction(chat_id, user, bot):
    bot.send_message(chat_id, "https://telegra.ph/finance-bot-05-15")


def get_support(chat_id, user, bot):
    bot.send_message(chat_id, 'пожалуйста, в следующем сообщении опиши проблему и укажи ник в Telegram')
    user['state'] = 11


def update_cur_stat(user, kind, expense, today):
    if today.day == user['day'] and today.month == user['month'] and today.year == user['year']:
        user['today' + kind] += expense
        user['cur_month' + kind] += expense
    else:
        user['today' + kind] = expense
        user['day'] = today.day

        if (user['year'] == today.year and user['month'] + 1 == today.month) or (
                user['year'] + 1 == today.year and user['month'] == 12 and today.month == 1):
            user['last_month_expense'] = user['cur_month_expense']
            user['last_month_income'] = user['cur_month_income']
            user['cur_month_expense'] = 0
            user['cur_month_income'] = 0
            user['cur_month' + kind] = expense
        elif user['year'] == today.year and user['month'] == today.month:
            user['cur_month' + kind] += expense
        else:
            user['last_month_expense'] = 0
            user['last_month_income'] = 0
            user['cur_month_expense'] = 0
            user['cur_month_income'] = 0
            user['cur_month' + kind] = expense

        user['month'] = today.month
        user['year'] = today.month


def update_cur_stat_after_del(user, kind, summa, today):
    if today.day == user['day'] and today.month == user['month'] and today.year == user['year']:
        user['today' + kind] += summa
        user['cur_month' + kind] += summa
    elif today.month == user['month'] and today.year == user['year']:
        user['cur_month' + kind] += summa
    elif (today.month == 12 and user['month'] == 1 and today.year + 1 == user['year']) or (
            today.month + 1 == user['month'] and today.year == user['year']):
        user['last_month' + kind] += summa


def cancel(chat_id, user, bot):
    bot.send_message(chat_id, 'действие отменено')
    user['state'] = 2


def get_categories_for_analytics(chat_id, user, bot):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(types.KeyboardButton('отменить действие'))
    user['state'] = 16
    bot.send_message(chat_id, 'напиши через запятую категории и ключевые слова, ' +
                     'которые ты хочешь увидеть в распределении. если ты хочешь, чтобы ключевые слова некоторой ' +
                     'категории учитывались отдельно, напиши эту категорию с знаком' +
                     '<b>+</b>, например, [кафе+]', parse_mode='HTML', reply_markup=keyboard)


def get_dynamic(chat_id, ss_id, user, bot, table_manager):
    print(user)
    bot.send_message(chat_id, 'analyze...')
    bot.send_chat_action(chat_id, 'upload_photo')
    table_manager.download_table(ss_id)
    res = count_dynamic(ss_id, user)
    if not res.startswith('нет трат'):
        img = open(ss_id + '.png', 'rb')
        bot.send_photo(chat_id, img)
        img.close()
    bot.send_message(chat_id, res, parse_mode='HTML')


def get_distrib(chat_id, ss_id, user, bot, table_manager):
    print(user)
    bot.send_message(chat_id, 'analyze...')
    bot.send_chat_action(chat_id, 'upload_photo')
    table_manager.download_table(ss_id)
    res_str = count_distrib(ss_id, user)
    if not res_str.startswith('нет трат'):
        img = open(ss_id + '.png', 'rb')
        bot.send_photo(chat_id, img)
        img.close()
    bot.send_message(chat_id, res_str, parse_mode='HTML')


def get_accs_for_analytics(chat_id, user, bot):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(types.KeyboardButton('отменить действие'))
    user['state'] = 18
    bot.send_message(chat_id, 'напиши через запятую счета, которые ты хочешь увидеть в распределении\n',
                     reply_markup=keyboard)


def add_new_record(chat_id, user, bot, table_manager, income, summa, category, account, comment):
    cur_date = datetime.today()
    if income == 1:
        res = table_manager.set_income(user, cur_date.strftime('%d.%m.%Y'), summa, category, account, comment)
    else:
        res = table_manager.set_expense(user, cur_date.strftime('%d.%m.%Y'), summa, category, account, comment)

    if not res:
        bot.send_message(chat_id, 'произошла ошибка, попробуйте еще раз')
    else:
        if income == 1:
            user['accounts'][account] += summa
            update_cur_stat(user, '_income', summa, cur_date)
        else:
            user['accounts'][account] -= summa
            update_cur_stat(user, '_expense', summa, cur_date)

        if user['send_for_verific']:
            bot.send_message(chat_id,
                             "добавил следующую запись:\nсумма: " + str(summa) + "\nкатегория: " + category +
                             "\nсчет: " + account + "\nкомментарий: " + comment)
        else:
            bot.send_message(chat_id, 'запись добавлена успешно')


callback_funcs = {'watch_categ': watch_categ, 'add_categ_out': add_categ_out, 'add_categ_in': add_categ_in,
                  'del_categ': del_categ, 'watch_acc': watch_acc, 'set_main_acc': set_main_acc, 'add_acc': add_acc,
                  'del_acc': del_acc, 'watch_sub': watch_sub, 'add_sub': add_sub, 'del_sub': del_sub,
                  'instruction': get_instruction, 'support': get_support, 'get_distrib': get_distrib,
                  'get_dynamic': get_dynamic, 'cancel': cancel, 'get_accs_for_analytics': get_accs_for_analytics,
                  'get_categories_for_analytics': get_categories_for_analytics}
