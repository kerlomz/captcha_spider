#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>


if __name__ == '__main__':
    # Type - 1
    from spiders.demo import Baidu
    project = Baidu()
    project.configuration(
        save_false=True,
        headers={
            "Cookie": "填入自己的Cookie"
        }
    )
    project.start(num=100000)

    # Type - 2
    # from utils import Project, ServiceType, Charset
    # project = Project(
    #     captcha_length=4,
    #     captcha_charset=Charset.ALPHABET,
    #     service_type=ServiceType.Kerlomz,
    #     captcha_url="https://en.exmail.qq.com/cgi-bin/getverifyimage"
    # )
    # project.start(1000)