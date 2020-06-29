#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
from spiders.demo import Baidu


if __name__ == '__main__':

    project = Baidu()
    project.configuration(
        save_false=True,
        headers={
            "Cookie": "填入自己的Cookie"
        }
    )
    project.start(num=100000)
