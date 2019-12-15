# ipo-watcher

自动跟踪科创板首发信息, 在招股书中发现特定关键字信息后, 发邮件通知.

# 安装与运行

纯python程序, 需要适配运行平台, 在src文件中放入浏览器驱动, 并重命名为`chromedriver.exe`.
修改src中配置文件`config.py`

# 注意

1. pdf转txt非常慢, 目前没找到好办法.