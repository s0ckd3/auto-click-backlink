import random
import time

import requests
from proxy_checker import ProxyChecker

import settings

session = requests.session()
checker = ProxyChecker()


def get_tmproxy():
    proxy = None
    proxy_keys = settings.TM_PROXY_KEYS
    while len(proxy_keys) > 0:
        try:
            proxy_key = random.choice(proxy_keys)
            res = session.post(
                'https://tmproxy.com/api/proxy/get-new-proxy',
                json={
                    "api_key": proxy_key,
                }
            ).json()
            print(res)
            if res['code'] == 0:
                proxy = res['data']['https']
            else:
                if len(proxy_keys) > 1:
                    proxy_keys.remove(proxy_key)
                    continue
                else:
                    res = session.post(
                        'https://tmproxy.com/api/proxy/get-current-proxy',
                        json={
                            "api_key": proxy_key,
                        }
                    ).json()
                    # if res['code'] == 0:
                    proxy = res['data']['https']
            if proxy:
                break
        except Exception as e:
            print(e, 'TM_PROXY')

    return proxy


def get_tinsoft_proxy():
    proxy = None
    proxy_keys = settings.PROXY_KEYS

    while len(proxy_keys) > 0:
        try:
            location = random.randrange(1, 15)
            proxy_key = random.choice(proxy_keys)
            res = session.get(
                f'https://proxy.tinsoftsv.com/api/changeProxy.php?key={proxy_key}',

            ).json()
            print(res)
            if res['success']:
                proxy = res['proxy']
            else:
                time.sleep(10)

                if len(proxy_keys) > 1:
                    proxy_keys.remove(proxy_key)
                    continue
                else:
                    res = session.get(
                        f'http://proxy.tinsoftsv.com/api/getProxy.php?key={proxy_key}',
                    ).json()
                    if res['success']:
                        proxy = res['proxy']
            if proxy:
                break
        except Exception as e:
            print(e, 'TINSOFT')


    return proxy


class GetProxy:
    def get_proxy(self):
        while True:
            proxy = get_tmproxy()
            if not proxy:
                proxy = get_tinsoft_proxy()
                if not proxy:
                    with open('proxies.txt') as f:
                        for proxy in f:
                            is_live = checker.check_proxy(proxy)
                            if is_live:
                                print(f'{proxy} :: {is_live}')
                                return proxy
                            else:
                                print(f'{proxy} Dead')

                else:
                    return proxy
            else:
                return proxy
