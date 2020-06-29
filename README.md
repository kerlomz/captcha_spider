# 简易验证码爬虫框架

一般的验证码获取流程分为三大步骤

1. 前置请求, 获取验证码相关参数
2. 验证码请求, 获取验证码
3. 校验请求, 通过官网判定验证码是否正确

通过继承 Project 类实现具体的流程 ```utils.Project```
```def before_process()-> dict```, 返回其他流程需要的参数字典, 通过 ```self.before_params``` 访问
```def captcha_process() -> Tuple[bytes, str]```, 返回验证码图片bytes和识别后的内容
```def feedback_process() -> bool```, 返回验证码反馈情况，是否正确


在 const.json 文件中补充自己的 **联众账号** 和 **百度API** 以及样本**保存的路径**
```json
{
  "baidu":  {
    "app_id":  "app_id",
    "api_key": "api_key",
    "secret_key": "secret_key"
  },
  "lianzhong": {
    "username": "username",
    "password": "password"
  },
  "target_dir": "D:/Samples"
}
```

编写流程：

1. 补充const.json
2.  在spiders包下面新建自己的爬虫可以参考demo.py
3.  在app.py中执行



该框架会执行整个爬虫及校验流程，对接联众平台如果识别错误会自动调用错误上报接口返还点数，框架为了方便开发学习使用，请勿用于非法途径。demo.py 例子不针对任何网站。