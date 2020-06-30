#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import os
import requests
from constants import ServiceType, ConstAPI

_sess = requests.Session()
cwd = os.path.dirname(__file__)


class MuggleOCR(object):

    def __init__(self):
        from muggle_ocr import SDK, ModelType
        self.sdk = SDK(model_type=ModelType.Captcha)

    def request(self, img_bytes):
        return self.sdk.predict(img_bytes)


class BaiduOCR(object):

    def __init__(self):
        from aip import AipOcr
        self.aip_ocr = AipOcr(ConstAPI.Baidu.app_id, ConstAPI.Baidu.api_key, ConstAPI.Baidu.secret_key)

    def request(self, img_bytes):
        options = {
            'detect_direction': 'true',
            'language_type': 'CHN_ENG',
        }
        result = self.aip_ocr.basicGeneral(img_bytes, options)
        # result = self.aip_ocr.basicAccurate(img_bytes, options)
        if 'error_code' in result:
            return result['error_msg']
        words_results = result.get("words_result")
        if not words_results:
            return ""
        return words_results[0].get('words')


class LianZhong(object):
    def __init__(self, captcha_type):
        self.captcha_type = captcha_type
        self._url = 'http://v1-http-api.jsdama.com/api.php?mod=php&act=upload'
        self._report_url = "http://v1-http-api.jsdama.com/api.php?mod=php&act=error"
        self.username = ConstAPI.LianZhong.username
        self.password = ConstAPI.LianZhong.password
        self.last_id = ''

    def request(self, img_bytes):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            # 'Content-Type': 'multipart/form-data; boundary=---------------------------227973204131376',
            'Connection': 'keep-alive',
            'Host': 'v1-http-api.jsdama.com',
            'Upgrade-Insecure-Requests': '1'
        }

        files = {
            'upload': ("1.jpg", img_bytes, 'image/png')
        }

        data = {
            'user_name': self.username,
            'user_pw': self.password,
            'yzm_minlen': '1',
            'yzm_maxlen': '6',
            'yzmtype_mark': self.captcha_type,
            'zztool_token': ''
        }
        try:
            resp = _sess.post(self._url, headers=headers, data=data, files=files, verify=False).json()
            if not resp['data']:
                return None
            self.last_id = resp['data']['id']
            return resp['data']['val']
        except Exception as e:
            print(e)
            return None

    def report(self):
        data = {"user_name": self.username, "user_pw": self.password, "yzm_id": self.last_id}
        try:
            resp = requests.post(self._report_url, data=data)
            print(resp.json())
        except Exception as e:
            print(e)


class GetCaptchaText(object):
    def __init__(self, service_type: ServiceType, captcha_type=None):
        self.captcha_type = captcha_type
        self.service_type = service_type

        if self.service_type == ServiceType.LianZhong:
            self.api = LianZhong(self.captcha_type)
        elif self.service_type == ServiceType.BaiduOCR:
            self.api = BaiduOCR()
        elif self.service_type == ServiceType.MuggleOCR:
            self.api = MuggleOCR()
        else:
            raise ValueError('invalid service_type')

    def report(self):
        if self.service_type == ServiceType.LianZhong:
            report = getattr(self.api, "report")
            report()
        else:
            raise ValueError('Not support report')

    def request(self, img_bytes):
        if self.service_type == ServiceType.MuggleOCR:
            return self.api.request(img_bytes=img_bytes)

        elif self.service_type == ServiceType.LianZhong:
            return self.api.request(img_bytes)

        elif self.service_type == ServiceType.BaiduOCR:
            return self.api.request(img_bytes)


if __name__ == '__main__':
    # with open("test.jpg", "rb") as fp:
    #     captcha_bytes = fp.read()

    with open("test_cn.png", "rb") as fp:
        captcha_bytes = fp.read()
    r = BaiduOCR().request(captcha_bytes)
    print(r)
    # r = CnOCR().request(captcha_bytes)
    # print(r)
