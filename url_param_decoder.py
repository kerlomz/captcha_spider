#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import json
import tkinter
from urllib import parse

# Charles 请求参数转换 dict
param = "content=1&tid=6716233397&lm=2539781&word=%E5%AE%9D%E9%A9%ACx3&rs10=0&rs1=0&t=0.8048427376809806"
data = parse.parse_qs(param)
data = {k: v[0] for k, v in data.items()}
data = json.dumps(data, indent=2)
print(data)
