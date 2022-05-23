import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

col_names = ['date_out', 'sum_out', 'categ_out', 'comment_out', 'acc_out', 'nan',
             'date_in', 'sum_in', 'categ_in', 'comment_in', 'acc_in']
col_types = {'sum_out': 'float64', 'categ_out': str, 'acc_out': str, 'sum_in': 'float64',
             'categ_in': str, 'acc_in': str}


def get_absolute(pct, total):
    absolute = int(np.round(pct / 100. * total))
    return str(absolute)


def count_distrib(ss_id, user):
    try:
        df = pd.read_csv(ss_id + '.csv', header=0, names=col_names, skiprows=1, decimal=',', dtype=col_types,
                         parse_dates=['date_out', 'date_in'], dayfirst=True)
    except BaseException as e:
        print(e)
        return ''
    begin, end = df['date_out'].searchsorted([user['start_date'], user['end_date'] + timedelta(days=1)])
    df = df.drop(index=list(range(end, len(df)))).drop(index=list(range(begin)))

    if user['accounts']:
        df = df.loc[~df['acc_out'].isin(user['accounts'])]

    targets = {}
    total = 0
    res_str = ''
    k = 0

    for target_category in user['global_targets']:
        summa = sum(df.loc[df['categ_out'].str.startswith(target_category)]['sum_out'])
        total += summa
        if summa != 0:
            res_str += target_category + ' ' + "{:.2f}".format(summa) + '\n'
            targets[target_category] = summa
            k += 1

    for target_category in user['local_targets']:
        summa = sum(df.loc[df['categ_out'] == target_category]['sum_out'])
        total += summa
        if summa != 0:
            k += 1
            if ',' not in target_category:
                res_str += target_category + ', другое ' + "{:.2f}".format(summa) + '\n'
                targets[target_category + ', другое'] = summa
            else:
                res_str += target_category + ' ' + "{:.2f}".format(summa) + '\n'
                targets[target_category] = summa

    res_str += '<b>всего</b> ' + "{:.2f}".format(total)

    if not targets:
        res_str = 'Нет трат по по заданным категориям и периоду'

    colors = plt.get_cmap('Paired')(np.arange(k))
    fig, ax = plt.subplots()
    wedges, _, _ = ax.pie(list(targets.values()), autopct=lambda pct: get_absolute(pct, total), colors=colors)
    ax.legend(wedges, list(targets.keys()), title="категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title("распределение за " + user['start_date'].strftime('%d.%m.%Y') + ' - ' +
                 user['end_date'].strftime('%d.%m.%Y'), loc='center')
    plt.savefig(ss_id + '.png', bbox_inches='tight')
    plt.clf()
    return res_str


def count_dynamic(ss_id, user):
    try:
        df = pd.read_csv(ss_id + '.csv', header=0, names=col_names, skiprows=1, decimal=',', dtype=col_types,
                         parse_dates=['date_out', 'date_in'], dayfirst=True)
    except BaseException as e:
        print(e)
        return ''

    begin, end = df['date_out'].searchsorted([user['start_date'], user['end_date'] + timedelta(days=1)])
    df = df.drop(index=list(range(end, len(df)))).drop(index=list(range(begin)))

    if user['accounts']:
        df = df.loc[~df['acc_out'].isin(user['accounts'])]

    if user['full_targets']:
        print(df)
        print(df['sum_out'])
        total = sum(df['sum_out'])
        if total == 0:
            return 'Нет трат по по заданным категориям и периоду '
        df = df.groupby(['date_out'], as_index=False)['sum_out'].sum().set_index('date_out')
        plot = df['sum_out'].plot(color='cornflowerblue', label='все траты',
                                  title='динамика трат за ' + user['start_date'].strftime('%d.%m.%Y') + ' - ' +
                                        user['end_date'].strftime('%d.%m.%Y'))
        fig = plot.get_figure()
        plt.legend(title="категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.xlabel('даты')
        plt.ylabel('сумма')
        fig.savefig(ss_id + '.png', bbox_inches='tight')
        plt.clf()
        print(total)
        return '<b>всего</b> ' + "{:.2f}".format(total)
    else:
        ax = None
        for target in user['global_targets']:
            df['categ_out'] = df['categ_out'].replace(to_replace=target + ', \\S+', value=target, regex=True)

        targets = user['global_targets'] + user['local_targets']
        df = df.groupby(['date_out', 'categ_out'], as_index=False)['sum_out'].sum().set_index('date_out')

        colors = plt.get_cmap('Paired')(np.arange(len(targets)))
        total = 0
        res_str = ''
        for target, color in zip(targets, colors):
            summa = sum(df.loc[df['categ_out'] == target]['sum_out'])
            if summa != 0:
                res_str += target + ' ' + "{:.2f}".format(summa) + '\n'
                total += summa
                if not ax:
                    ax = df.loc[df['categ_out'] == target]['sum_out'].plot(label=target, color=color)
                else:
                    df.loc[df['categ_out'] == target]['sum_out'].plot(ax=ax, label=target)

        if total == 0:
            return 'Нет трат по по заданным категориям и периоду'

        res_str += '<b>всего</b> ' + str(total)
        plt.legend(title="категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.xlabel('даты')
        plt.ylabel('сумма')
        plt.title('динамика трат за ' + user['start_date'].strftime('%d.%m.%Y') + ' - ' +
                  user['end_date'].strftime('%d.%m.%Y'))
        plt.savefig(ss_id + '.png', bbox_inches='tight')
        plt.clf()
        return res_str
