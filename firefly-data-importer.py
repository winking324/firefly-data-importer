# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
__copyright__ = "Copyright (c) 2014-2017 winking324."


import os
import pandas
import account
import argparse


def parse_money_wiz_csv(csv_file):
    """
    MoneyWiz 导出的 CSV 文件结构格式如下:
       1         2     3     4      5        6      7     8     9     10     11        12
    "命名","当前余额","账户","转账","描述","交易对方","分类","日期","时间","金额","货币","支票号码"
    分为几种情况：
    1. 账户以及当前余额，默认是第一行；
    2. 转账信息（需要注意对应接收账户也会存在该条记录）；
    3. 支出；
    4. 收入；
    5. 调整余额；
    """
    csv = pandas.read_csv(csv_file, skiprows=2, header=None)
    accounts = []
    new_account = None
    for row in csv.itertuples():
        if not pandas.isna(row[1]):
            if new_account:
                accounts.append(new_account)
            new_account = account.Account()
            if not new_account.parse_account(row):
                print('Error: parse account {} failed'.format(row))
                return None
            continue
        if not new_account.parse_transaction(row):
            print('Warning: parse transaction {} failed, ignore'.format(row))

    if new_account:
        accounts.append(new_account)
    return accounts


def import_to_firefly(port, accounts):
    accounts_id = {}
    for account_item in accounts:
        if not account_item.create_account(port):
            print('Error: create account {} failed'.format(account_item))
            return False
        accounts_id[account_item.name] = account_item.id

    for account_item in accounts:
        if not account_item.create_transactions(port, accounts_id):
            print('Error: create account transactions {} failed'.format(account_item))
            return False
    return True


def main():
    parser = argparse.ArgumentParser(prog='MoneyWiz-To-Firefly', description='Import MoneyWiz CSV data to Firefly III')
    parser.add_argument('-f', '--filename', help='csv 文件的路径', required=True, type=str)
    parser.add_argument('-p', '--port', help='服务端口', required=False, type=int, default=80)
    args = parser.parse_args()
    if not os.path.isfile(args.filename):
        print('Error: {} is not exist'.format(args.filename))
        return
    accounts = parse_money_wiz_csv(args.filename)
    if not accounts:
        print('Error: parse {} failed'.format(args.filename))
        return

    if not import_to_firefly(args.port, accounts):
        print('Error: import to firefly failed')
        return
    print('Info: import to firefly success')


if __name__ == '__main__':
    main()
