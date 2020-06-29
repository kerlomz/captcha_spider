#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import os
import uuid
import time
import json
import random
import hashlib
from constants import target_dir, ProxyType, ASSERT_MAP, ServiceType
from requests import Session
from typing import Tuple
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

    def __init__(self, service_type: ServiceType = None, captcha_type=None):
        self.service_type = service_type if service_type else ServiceType.MuggleOCR
        self.captcha_type = captcha_type if captcha_type else "1105"
        self.project_path: str = os.path.join(target_dir, self.__class__.__name__)
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

    def init(self):
        self.platform: GetCaptchaText = GetCaptchaText(service_type=self.service_type, captcha_type=self.captcha_type)

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

    def captcha_process(self) -> Tuple[bytes, str]:
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
            captcha_bytes, captcha_text = self.captcha_process()
            if b'<!DOCTYPE html>' in captcha_bytes:
                print('ERROR[CAPTCHA-PROCESS]: CAPTCHA BYTES ERROR [{}]'.format(captcha_bytes[0: 20]))
                return
            if not captcha_text:
                print('ERROR[CAPTCHA-PROCESS]: CAPTCHA TEXT IS NONE')
                return
        except Exception as e:
            print('ERROR[CAPTCHA-PROCESS]: {}'.format(e))
            return
        try:
            if self.delay > 0:
                time.sleep(self.delay)
            captcha_assert = self.feedback_process(captcha_text=captcha_text)
        except Exception as e:
            print('ERROR[FEEDBACK-PROCESS]: {}'.format(e))
            return
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
            self.process(i)


if __name__ == '__main__':
    pass
