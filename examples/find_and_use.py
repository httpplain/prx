"""Find working proxies and use them concurrently.

Note: Pay attention to Broker.serve(), instead of the code listed below.
      Perhaps it will be much useful and friendlier.
"""

import asyncio
from urllib.parse import urlparse

import aiohttp

from proxybroker import Broker, ProxyPool
from proxybroker.errors import NoProxyError


async def fetch(url, proxy_pool, timeout, loop):
    resp, proxy = None, None
    try:
        print('Waiting a proxy...')
        proxy = await proxy_pool.get(scheme=urlparse(url).scheme)
        print('Found proxy:', proxy)
        proxy_url = 'http://%s:%d' % (proxy.host, proxy.port)
        _timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
            timeout=_timeout, loop=loop
        ) as session, session.get(url, proxy=proxy_url) as response:
            resp = await response.text()
    except (
        aiohttp.errors.ClientOSError,
        aiohttp.errors.ClientResponseError,
        aiohttp.errors.ServerDisconnectedError,
        asyncio.TimeoutError,
        NoProxyError,
    ) as e:
        print('Error!\nURL: %s;\nError: %r\n', url, e)
    finally:
        if proxy:
            proxy_pool.put(proxy)
        return (url, resp)


async def get_pages(urls, proxy_pool, timeout=10, loop=None):
    tasks = [fetch(url, proxy_pool, timeout, loop) for url in urls]
    for task in asyncio.as_completed(tasks):
        url, content = await task
        print('%s\nDone!\nURL: %s;\nContent: %s' % ('-' * 20, url, content))


def main():
    loop = asyncio.get_event_loop()

    proxies = asyncio.Queue()
    proxy_pool = ProxyPool(proxies)

    judges = [
        'http://httpbin.org/get?show_env',
        'https://httpbin.org/get?show_env',
    ]

    providers = [
        'http://www.proxylists.net/',
        'http://ipaddress.com/proxy-list/',
        'https://www.sslproxies.org/',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
        'https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt',
        'https://proxyspace.pro/http.txt',
        'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt',
        'https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt',
        'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
        'https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/free.txt',
        'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/https.txt',
        'https://raw.githubusercontent.com/httpplain/browser/main/list.txt',
        'https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt',
        'https://raw.githubusercontent.com/NotUnko/autoproxies/main/proxies/https',
        'https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/https.txt',
        'https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt',
        'https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt',
        'https://api.openproxylist.xyz/http.txt',
        'https://proxy1.bf/proxy.txt',
        'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks4.txt',
        'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks5.txt',
        'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt',
        'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt',
        'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
        'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/https.txt',
        'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt',
        'https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt',
        'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
        'https://raw.githubusercontent.com/httpplain/browser/main/cn.txt',
        'https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt',
        'https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt',
        'https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt',
        'https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt',
        'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt',
        'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt',
        'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt',
        'https://raw.githubusercontent.com/tuanminpay/live-proxy/master/http.txt',
        'https://raw.githubusercontent.com/casals-ar/proxy-list/main/https',
        'https://raw.githubusercontent.com/casals-ar/proxy-list/main/http',
        'https://raw.githubusercontent.com/andigwandi/free-proxy/main/proxy_list.txt',
        'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt',
        'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt',
        'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt',
        'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
        'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt',
        'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt',
        'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
        'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt',
    ]

    broker = Broker(
        proxies,
        timeout=8,
        max_conn=200,
        max_tries=3,
        verify_ssl=False,
        judges=judges,
        providers=providers,
        loop=loop,
    )

    types = [('HTTP', ('Anonymous', 'High'))]
    countries = ['US', 'UK', 'DE', 'FR']

    urls = [
        'http://httpbin.org/get',
        'http://httpbin.org/redirect/1',
        'http://httpbin.org/anything',
        'http://httpbin.org/status/404',
    ]

    tasks = asyncio.gather(
        broker.find(types=types, countries=countries, strict=True, limit=10),
        get_pages(urls, proxy_pool, loop=loop),
    )
    loop.run_until_complete(tasks)

    # broker.show_stats(verbose=True)


if __name__ == '__main__':
    main()
