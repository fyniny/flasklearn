import os
import signal
import sys

def readpid(pid_file):
    if not os.path.exists(pid_file):
        return None
    
    with open(pid_file, 'r') as f:
        strpid = f.readlines(1)
    if len(strpid) < 1:
        return None

    try:
        ipid = int(strpid[0])
    except Exception:
        return None

    return ipid

def check_process(pid_file):
    """
    检查守护进程是否启动，返回False表示没有启动
    """
    ipid = readpid(pid_file)
    if ipid:
        try:
            os.kill(ipid, 0)
            return True
        except OSError as e:
            pass
    return False

def stop_daemon(pid_file):
    ipid = readpid(pid_file)
    if ipid:
        os.kill(ipid, signal.SIGKILL)
        os.remove(pid_file)

def daemonize(pid_file):
    """
    创建守护进程
    :param pid_file: 保存进程id的文件
    :return:
    """
    if check_process(pid_file):
        raise Exception('服务运行中')
    # 从父进程fork一个子进程出来
    pid = os.fork()
    # 子进程的pid一定为0，父进程大于0
    if pid:
        # 退出父进程，sys.exit()方法比os._exit()方法会多执行一些刷新缓冲工作
        sys.exit(0)

    # 子进程默认继承父进程的工作目录，最好是变更到根目录，否则回影响文件系统的卸载
    os.chdir('/')
    # 子进程默认继承父进程的umask（文件权限掩码），重设为0（完全控制），以免影响程序读写文件
    os.umask(0)
    # 让子进程成为新的会话组长和进程组长
    os.setsid()

    # 注意了，这里是第2次fork，也就是子进程的子进程，我们把它叫为孙子进程
    _pid = os.fork()
    if _pid:
        # 退出子进程
        sys.exit(0)

    # 此时，孙子进程已经是守护进程了，接下来重定向标准输入、输出、错误的描述符(是重定向而不是关闭, 这样可以避免程序在 print 的时候出错)

    # 刷新缓冲区先，小心使得万年船
    sys.stdout.flush()
    sys.stderr.flush()

    # dup2函数原子化地关闭和复制文件描述符，重定向到/dev/nul，即丢弃所有输入输出
    with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        os.dup2(read_null.fileno(), sys.stdin.fileno())
        os.dup2(write_null.fileno(), sys.stdout.fileno())
        os.dup2(write_null.fileno(), sys.stderr.fileno())

    if pid_file:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
