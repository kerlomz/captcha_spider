#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import json
from typing import Tuple
from utils import Project, ServiceType, ProxyType


class Baidu(Project):
    """
    定义自己的类
    """

    def __init__(self):
        super().__init__()
        # 选择识别服务 [MuggleOCR, BaiduOCR, LianZhong]
        self.service_type = ServiceType.MuggleOCR
        # 联众的验证码类型
        self.captcha_type = "1105"

        # 前置页面 （验证码出现的页面，用于获取相关参数）
        self.before_url = "https://tieba.baidu.com/f/commit/commonapi/getVcode"
        # 验证码页面 用于获取验证码
        self.captcha_url = "https://tieba.baidu.com/cgi-bin/genimg"
        # 提交页面 用于校验验证码是否准确
        self.feedback_url = "https://tieba.baidu.com/f/commit/commonapi/checkVcode"

    def before_process(self, retry=0) -> dict:
        """
        前置页面，获取验证码需要 captcha_vcode_str 参数，return 参数字典提供后面流程调用
        :param retry: 重试计数
        :return: 参数字典
        """
        payload = {
            "content": "1",
            "tid": "6716233397",
            "lm": "2539781",
            "word": "\u5b9d\u9a6cx3",
            "rs10": "0",
            "rs1": "0",
            "t": "0.8048427376809806"
        }
        r = self.session.post("https://tieba.baidu.com/f/commit/commonapi/getVcode", data=payload)
        resp = r.text
        resp_json: dict = json.loads(resp)
        if 'captcha_vcode_str' in resp_json.keys():
            captcha_vcode_str = resp_json.get('captcha_vcode_str')
            return {"captcha_vcode_str": captcha_vcode_str}
        else:
            print(resp_json)
            return {}

    def captcha_process(self) -> Tuple[bytes, str]:
        """
        :return: 返回两个参数：验证码bytes内容, 返回验证码标签
        """
        if not self.before_params.get('captcha_vcode_str'):
            raise ValueError('captcha_vcode_str is miss')
        captcha_bytes = self.session.get(
            self.captcha_url + "?{}".format(self.before_params['captcha_vcode_str'])
        ).content

        captcha_text = self.platform.request(captcha_bytes)
        return captcha_bytes, captcha_text

    def feedback_process(self, captcha_text: str) -> bool:
        """
        :param captcha_text: 验证码识别结果
        :return: 返回验证状态 [验证码正确, 验证码错误]
        """
        if not captcha_text:
            return False
        if len(captcha_text) != 4:
            return False
        if not self.before_params['captcha_vcode_str']:
            raise ValueError('miss captcha_vcode_str')
        payload = {
            "captcha_vcode_str": self.before_params['captcha_vcode_str'],
            "captcha_code_type": "1",
            "captcha_input_str": captcha_text,
            "fid": "2539781"
        }
        r = self.session.post(self.feedback_url, data=payload)
        if '{"anti_valve_err_no":0}' in r.text:
            return True
        else:
            r.encoding = "gbk"
            print(r.text)
            return False


if __name__ == '__main__':
    pass