#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import json
from enum import Enum, unique

ASSERT_MAP = {True: '正确', False: '错误'}

with open("const.json", "r", encoding="utf8") as c_json:
    const_json = json.loads("".join(c_json.readlines()))

target_dir = const_json['target_dir']


class ConstAPI:

    class Baidu:
        const = const_json['baidu']
        app_id = const['app_id']
        api_key = const['api_key']
        secret_key = const['secret_key']

    class LianZhong:
        const = const_json['lianzhong']
        username = const['username']
        password = const['password']


@unique
class ServiceType(Enum):
    MuggleOCR = 'MuggleOCR'
    BaiduOCR = 'BaiduOCR'
    LianZhong = 'LianZhong'


@unique
class ProxyType(Enum):
    none = 'none'
    customize = 'customize'
