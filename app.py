#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>


if __name__ == '__main__':
    # Type - 1
    # from spiders.demo import Baidu
    # project = Baidu()
    # project.configuration(
    #     save_false=True,
    #     headers={
    #         "Cookie": "填入自己的Cookie"
    #     }
    # )
    # project.start(num=100000)

    # Type - 2
    from utils import Project, ServiceType, Charset
    project = Project(
        captcha_length=5,
        captcha_charset=Charset.ALPHANUMERIC,
        service_type=ServiceType.MuggleOCR,
        captcha_url="https://ad.vivo.com.cn/api/common/captcha/image?time=1594025331953"
    )
    project.start(1000)