#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import os
import sys
import uuid
import time
import json
import random
import hashlib
import traceback
from constants import target_dir, ProxyType, ASSERT_MAP, ServiceType, Charset
from requests import Session
from typing import Union, Tuple
from urllib.parse import urlparse
from parsel import Selector
from fake_useragent import UserAgent
from service import GetCaptchaText

ua = UserAgent()


class Proxy(object):

    @staticmethod
    def no_proxy():
        return {}

    @staticmethod
    def customize():
        return {"http": "http://*自定义代理组", "https": "http://*自定义代理组"}


class Project(object):
    class Parser(Selector):

        def input(self, name):
            return self.xpath('//[@name={name}]/@value'.format(name=name)).extract_first()

    base_headers = {
        'User-Agent': ua.random
    }

    def configuration(self, proxy: ProxyType = ProxyType.none, headers={}, save_false=False):

        headers.update(self.base_headers)
        self.session.headers = headers
        self.save_false = save_false

        if proxy == ProxyType.customize:
            self.proxy = Proxy.customize

    def __init__(
            self,
            service_type: ServiceType = None,
            captcha_url: str = None,
            captcha_length: Union[list, int] = None,
            captcha_charset: Charset = Charset.UNDEFINED,
            platform_type: str = None,
    ):
        if captcha_length is None:
            captcha_length = [1, 18]
        if isinstance(captcha_length, list):
            if len(captcha_length) != 2:
                raise ValueError('<captcha_length> should be a list of length 2 '
                                 'and satisfy the equation: captcha_length[0] <captcha_length[1].')
            if captcha_length[0] > captcha_length[1]:
                raise ValueError('<captcha_length> should satisfy the equation captcha_length[0] <captcha_length[1]')

        self.captcha_length: Union[list, int] = captcha_length
        self.captcha_charset: Charset = captcha_charset
        self.should_stop = False
        self.service_type = service_type if service_type else ServiceType.Kerlomz
        self.platform_type = platform_type if platform_type else "1105"
        self._captcha_url = captcha_url

        project_name = self.__class__.__name__
        if project_name == 'Project' and self._captcha_url:
            project_name = urlparse(self._captcha_url).netloc
            project_name = project_name.split(":")[0] if ":" in project_name else project_name

        self.project_path: str = os.path.join(target_dir, project_name)
        self.true_path: str = os.path.join(self.project_path, "true")
        self.false_path: str = os.path.join(self.project_path, "false")
        self.path_selector: dict = {True: self.true_path, False: self.false_path}
        self.session: Session = Session()
        self.proxy = Proxy.no_proxy
        self.true_count: int = 0
        self.false_count: int = 0
        self.save_false: bool = False
        self.before_params: dict = {}
        self.platform: GetCaptchaText = None
        self.delay: float = 0

    @staticmethod
    def is_chinese(text):
        for ch in text:
            if not ('\u4e00' <= ch <= '\u9fff'):
                return False
        return True

    def validate(self, text: str) -> Tuple[bool, str]:
        if not text:
            return False, "<captcha_text> is None or ''"
        if self.captcha_charset == Charset.ALPHANUMERIC:
            if not text.isalnum():
                return False, "[{}] is not in [ALPHANUMERIC]".format(text)
        elif self.captcha_charset == Charset.ALPHABET:
            if not text.isalpha():
                return False, "[{}] is not in [ALPHABET]".format(text)
        elif self.captcha_charset == Charset.NUMERIC:
            if not text.isdigit():
                return False, "[{}] is not in [NUMERIC]".format(text)
        elif self.captcha_charset == Charset.ARITHMETIC:
            charset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(', ')', '+', '-', '×', '÷', '=', 'x', 'X']
            for index in text:
                if index not in charset:
                    return False, "[{}] is not in [ARITHMETIC]".format(text)
        elif self.captcha_charset == Charset.CHINESE:
            if not Project.is_chinese(text):
                return False, "[{}] is not in [CHINESE]".format(text)

        if isinstance(self.captcha_length, list):
            len_min = self.captcha_length[0]
            len_max = self.captcha_length[1]
            length_assert = len_min <= len(text) <= len_max
            if not length_assert:
                return False, "LEN[{}] is not in the [{}, {}]".format(text, len_min, len_max)
            return True, ""
        elif isinstance(self.captcha_length, int):
            length_assert = len(text) == self.captcha_length
            if not length_assert:
                return False, "LEN[{}] is not equal to {}".format(text, self.captcha_length)
            return True, ""

    def init(self):
        self.platform: GetCaptchaText = GetCaptchaText(service_type=self.service_type, platform_type=self.platform_type)

    def save(self, label: str, img_bytes: bytes, result_assert: bool):
        _save_path = self.path_selector[result_assert]
        if not os.path.exists(_save_path):
            os.makedirs(_save_path)
        tag = hashlib.md5(img_bytes).hexdigest()
        filename = "{}_{}.png".format(label, tag)
        filename = self.replace_all(filename, ["<", ">", "/", "\\", "|", ":", "*", "?"])
        save_path = os.path.join(_save_path, filename)

        with open(save_path, "wb") as f:
            f.write(img_bytes)

    @property
    def timestamp(self):
        return str(int(time.time() * 1000))

    @property
    def uuid(self):
        return str(uuid.uuid4())

    @staticmethod
    def md5(data: bytes):
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def replace_all(origin: str, content: list):
        result = origin
        for r_content in content:
            result = result.replace(r_content, "")
        return result

    @property
    def random(self):
        return str(random.random())

    @staticmethod
    def parse_jquery(content: str):
        return json.loads(content.split("(", 1)[1][:-1])

    def before_process(self) -> dict:
        pass

    def captcha_process(self) -> bytes:
        pass

    def feedback_process(self, captcha_text: str) -> bool:
        pass

    def process(self, index):
        st = time.time()
        proxy = self.proxy()
        if proxy:
            self.session.proxies = proxy
        try:
            self.before_params = self.before_process()
        except Exception as e:
            print('ERROR[BEFORE-PROCESS]: {}'.format(e))
            return
        try:
            captcha_bytes = self.captcha_process()
            if captcha_bytes is None and not self._captcha_url:
                print('ERROR[CAPTCHA-PROCESS-TERMINAL]: '
                      'To implement <captcha_process> or define the <captcha_url> parameters, both should choose one.')
                self.should_stop = True
                return
            if captcha_bytes is None and self._captcha_url:
                captcha_bytes = self.session.get(self._captcha_url).content
            captcha_text = self.platform.request(captcha_bytes)
            if b'<!DOCTYPE html>' in captcha_bytes:
                print('ERROR[CAPTCHA-PROCESS]: CAPTCHA BYTES ERROR [{}]'.format(captcha_bytes[0: 20]))
                return
            if captcha_text is None:
                print('ERROR[CAPTCHA-PROCESS]: CAPTCHA TEXT IS NONE')
                return
            if captcha_text == "":
                print('ERROR[CAPTCHA-PROCESS]: CAPTCHA TEXT IS BLANK')
                return
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print('ERROR[CAPTCHA-PROCESS]: {}'.format(e))
            return
        captcha_assert, assert_msg = self.validate(captcha_text)
        if not captcha_assert:
            print('ERROR[VALIDATE-PROCESS]: {}'.format(assert_msg))
            return
        try:
            if self.delay > 0:
                time.sleep(self.delay)
            captcha_assert = self.feedback_process(captcha_text=captcha_text)
        except Exception as e:
            print('ERROR[FEEDBACK-PROCESS]: {}'.format(e))
            return
        captcha_assert = True if captcha_assert is None else captcha_assert
        if captcha_assert:
            self.true_count += 1
            self.save(label=captcha_text, img_bytes=captcha_bytes, result_assert=captcha_assert)
        else:
            self.false_count += 1
            if self.save_false:
                if self.platform.service_type == ServiceType.LianZhong:
                    self.platform.report()
                self.save(label=captcha_text, img_bytes=captcha_bytes, result_assert=captcha_assert)
        acc = self.true_count / (self.true_count + self.false_count)
        msg = "{} | 识别结果: [{}] - [{}] - 准确率: [{:.4f}] | 总耗时: [{} ms]".format(
            index, captcha_text, ASSERT_MAP[captcha_assert], acc, (time.time() - st) * 1000
        )
        if self.session.proxies:
            msg = "{} | 使用代理: [{}]".format(msg, self.session.proxies.get('http'))
        print(msg)

    def start(self, num=1000):
        self.init()
        for i in range(num):
            if self.should_stop:
                break
            self.process(i)


if __name__ == '__main__':
    pass
