# PYTHON Flask demo

使用`Flask`和`gevent`写的一个demo

## 目录说明
.
├── daemon.py 创建守护进程的实现文件
├── main.py 是一个flask的WEB后台服务,使用gevent驱动
├── README.md
├── service_health_checker.py 健康检查，用于检查main,.py是否启动
└── service.yml.default 健康检查需要使用的配置文件

## 健康检查配置文件说明

```yaml
services:
  - name: web
    url: http://127.0.0.1:9999/healthcheck
    start_cmd: /usr/bin/python3 ${youpath}/main.py --start -d
    user: ${youuser}
```

servies是一个数组对象，每一个数组成员代表一个服务

name: 表示服务名
url: 服务暴露的用于健康检查的URL
start_cmd: 启动服务的命令
user: 该服务需要启动的用户

- 健康检查程序权限

健康检查程序需要运行在root用户下，因此start_cmd的调度会引起较大风险，应该严格控制service.yml文件的*访问权限*

- 健康检查原理

main.py 需要暴露一个web接口用于健康检查，service_health_checker会尝试访问该接口，若访问失败，则认为服务没有启动，并尝试启动。
*若服务未启动，健康检查程序启动该服务失败时不会立即进行重试，等下一次检查时进行重试*





