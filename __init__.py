import web
import socket
from typing import Union, Any, Optional

mappings = ()
WebApp = web.application()
Function = type(lambda: ...)


class DefaultSite:
    GET: object = ...
    POST: object = ...


def site(_get: Union[object, Function] = lambda self: ...,
         _post: Union[object, Function] = lambda self: ...,
         mapping: str = '/') -> None:
    """
    用于创建默认站点，一般用于定义网站的/index
    :rtype: None
    :param _get: 当以GET访问时，调用的方法，值为一个函数，该函数需带一个 self 参数，若值为object，则在访问时直接返回该值。
    :param _post: 当以POST访问时，调用的方法，值为一个函数，该函数需带一个 self 参数，若值为object，则在访问时直接返回该值。
    :param mapping: 应为一个正则表达式，默认为'/'，代表访问该站点时的接口，正则表达式所匹配的内容将会分组传入 _ge t和 _post 的参数。

    >>> # example 1
    >>> # from webnew import *
    >>> site('Hello, GET.', 'Hello, POST.')
    >>> run(globals())

    >>> # example 2
    >>> # from webnew import *
    >>> site(lambda self, name: f'Hello, {name}.', mapping='/(.+)')
    >>> run(globals())
    """
    global mappings
    mappings += (mapping, 'DefaultSite')

    if isinstance(_get, Function) and isinstance(_post, Function):
        DefaultSite.GET, DefaultSite.POST = _get, _post
    elif isinstance(_get, object) and isinstance(_post, object):
        DefaultSite.GET, DefaultSite.POST = lambda self: _get, lambda self: _post
    elif isinstance(_get, Function) and isinstance(_post, object):
        DefaultSite.GET, DefaultSite.POST = _get, lambda self: _post
    elif isinstance(_get, object) and isinstance(_post, Function):
        DefaultSite.GET, DefaultSite.POST = lambda self: _get, _post
    else:
        raise TypeError(f'Type GET:"{type(_get)}" or POST:"{type(_post)}" can\'t be used.')


def newSite(class_, mapping: str = '/') -> None:
    """
    用于创建新的站点，原理为调用传入类里的 GET 和 POST 方法。
    :rtype: None
    :param class_: 应为一个类，至少包含 GET 和 POST 方法中的一个用于处理GET和POST请求，至少需带一个 self 参数。
    :param mapping: 应为一个正则表达式，默认为'/'，代表访问该站点时的接口，正则表达式所匹配的内容将会分组传入 class_ 的 GET 和 POST 的参数。

    >>> # example 1
    >>> # from webnew import *
    >>> class index:
    ...     GET = lambda self: 'Hello, GET.'
    ...     POST = lambda self: 'Hello, POST.'
    >>> newSite(index)
    >>> run(globals())

    >>> # example 2
    >>> # from webnew import *
    >>> site('<!DOCTYPE HTML><meta charset="utf-8" /><h1>请传入文件路径</h1>')
    >>> class open_file:
    >>>     @staticmethod
    ...     def GET( path):
    ...         try: return open(path, encoding='utf-8')
    ...         except Exception as e: return f'<!DOCTYPE HTML><meta charset="utf-8" /><h1>{e}</h1>'
    >>> newSite(open_file, '/(.+)')
    >>> run(globals())
    """
    global mappings
    mappings += (mapping, class_.__name__)


def newSites(*sites: tuple[Any, str]) -> None:
    """
    用于一次新建多个站点。
    :rtype: None
    :param sites: 形式为 ((class_, mapping), ...)，意为循环执行 newSite(class_, mapping)。

    >>> # example
    >>> # from webnew import *
    >>> site('<a href="/page_1">Go to page 1</a>')
    >>> class page_1: GET = lambda self: '<a href="/page_2">Go to page 2</a>'
    >>> class page_2: GET = lambda self: '<a href="/">Go to index</a>'
    >>> newSites((page_1, '/page_1'), (page_2, '/page_2'))
    >>> run(globals())
    """
    for i in sites:
        newSite(i[0], i[1])


def debug(mode: bool = True) -> None:
    """
    用于设置网站是否调试，不调用debug()时默认为调试。
    :rtype: None
    :param mode: 应为布尔值，当为True时启用调试模式，为False时关闭，若调试模式启用，Python后端出现任何错误时会在此网页上报错。
    """
    web.config.debug = mode


def reset() -> None:
    """
    用于重新加载 WebApp 对象的值。（WebApp可能会在未来的版本中替换为一个函数，reset()也可能会随之删除）

    >>> # example
    >>> # from webnew import *
    >>> site()
    >>> print(WebApp.browser())  # 输出不固定
    <web.browser.AppBrowser object at 0x00000136C15E0E80>
    >>> reset()
    >>> print(WebApp.browser())  # 输出不固定
    <web.browser.AppBrowser object at 0x00000136C15E0D90>
    """
    global WebApp
    WebApp = web.application(mappings, globals())


def run(globals_=None) -> None:
    """
    用于运行服务器。
    :param globals_: 凡是调用 run() 都应传入 globals() 。
    """
    if globals_ is None:
        globals_ = globals()
    global WebApp
    WebApp = web.application(mappings, globals_)
    print(f'http://{socket.gethostbyname(socket.gethostname())}:8080/')
    WebApp.run()


def open_web() -> None:
    import webbrowser
    webbrowser.open(f'http://{socket.gethostbyname(socket.gethostname())}:8080/')


try:
    import requests as ret


    class request:
        @staticmethod
        def GET(ip: str = socket.gethostbyname(socket.gethostname()), localhost: int = 8080, mapping: str = '/') -> \
                Optional[ret.Response]:
            try:
                return ret.get(f'http://{ip}:{localhost}{mapping}')
            except ret.exceptions.ConnectionError:
                return None

        @staticmethod
        def POST(ip: str = socket.gethostbyname(socket.gethostname()), localhost: int = 8080, mapping: str = '/') -> \
                Optional[ret.Response]:
            try:
                return ret.post(f'http://{ip}:{localhost}{mapping}')
            except ret.exceptions.ConnectionError:
                return None

except ImportError:
    def GET():
        ...


    def POST():
        ...
