import sys, threading

# kth-timeoutdecorator
# This code is modified from https://mail.python.org/pipermail/python-list/2004-May/260937.html ,but it doesn't work!
# Used work of Angel Hair
# license: MIT, see LICENSE for more details.
# https://github.com/Angel-Hair/kth-timeoutdecorator

class TimeoutException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class KThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False
    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)
    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None
    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace
    def kill(self):
        self.killed = True
    def raisetimeout(self):
        """Here must throw an exception by the thd, because the exception thrown by the decorator cannot be caught | 这里一定要由thd抛出异常，因为修饰器抛出的异常无法被捕获"""
        raise TimeoutException('function run too long, time limit exceeded.')

def timeout(seconds=None):
    """Add a timeout parameter to a function | 超时修饰器
    
    :param seconds: optional time limit in seconds . If None is passed, no timeout is applied. | 时间限制参数，单位为秒(s)，如果未赋直，则函数会正常运行不受影响。
    """
    def timeout_decorator(func):
        if not seconds:
            return func
        def _new_func(oldfunc, result, oldfunc_args, oldfunc_kwargs):
            result.append(oldfunc(*oldfunc_args, **oldfunc_kwargs))
        def _(*args, **kwargs):
            result = []
            new_kwargs = {
                'oldfunc': func,
                'result': result,
                'oldfunc_args': args,
                'oldfunc_kwargs': kwargs
            }
            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)
            thd.start()
            thd.join(seconds)
            if sys.version_info >= (3, 9):
                alive = thd.is_alive()
            else:
                alive = thd.isAlive()
            thd.kill()
            if alive:
                thd.raisetimeout()
                return None
            else:
                return result[0]
        _.__name__ = func.__name__
        _.__doc__ = func.__doc__
        return _
    return timeout_decorator
