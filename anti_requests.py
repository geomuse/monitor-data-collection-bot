import requests , socks , socket , time , warnings , pickle
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from loguru import logger
import pandas as pd

logger.add("log/error.log", level="ERROR", rotation="10 MB", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

warnings.filterwarnings("ignore")

class ws_bot:
    def __init__(self) -> None:
        ...

    def requests_initial(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        return headers

class monitor_proxy_server:
    def __init__(self) -> None:
        pass
    
    def __generate_proxy_server(self):
        proxy_list = pd.read_csv('socks5_proxies.txt',header=None)
        proxy_list[0] = proxy_list[0].apply(lambda text : str(text).split(":"))
        proxy_ips, proxy_ports = [] , []
        for _ in range(len(proxy_list)):
            proxy_ip , proxy_port = proxy_list[0][_]
            proxy_ips.append(proxy_ip) , proxy_ports.append(int(proxy_port))
        return proxy_ips , proxy_ports

    def session_initial(self,proxy):
        ip , port = proxy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[ 500, 502, 503, 504 ],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.proxies = {
                'http': f'socks5://{ip}:{port}',
                'https': f'socks5://{ip}:{port}'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # 'Accept-Language': 'en-US,en;q=0.9',
        }
        session.headers.update(headers)
        session.verify = False # InsecureRequestWarning: Unverified HTTPS request is being made to host 'checkip.amazonaws.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
        return session
    
    def check_response(self,response) -> str:
        if response.status_code == 200:
            return response.text
        else : 
            print(f'请求失败,status.code : {response.status_code}')

    def check_response_time(self,start,end):
        response_time = end - start
        print('请求响应时间:', response_time)
        return response_time
    
    def requests_check_the_proxy_server(self):
        proxy_ip , proxy_port = self.__generate_proxy_server()
        support_proxy = []
        for ip , port in zip(proxy_ip,proxy_port):
            session = self.session_initial((ip,port))
            time.sleep(5)
            try :
                start = time.time()
                try :
                    response = session.get('https://checkip.amazonaws.com/')
                except Exception as e :
                    continue
                end = time.time()
                response = self.check_response(response=response)
                if response : 
                    response_time = self.check_response_time(start=start,end=end)
                    if response_time < 15 :
                        print(f'{ip} have been mark.')
                        support_proxy.append((ip,port))
                
            except Exception as e : 
                logger.error(f'{e}')

        if not support_proxy :
            print('support proxy empty please update.')
        else : 
            with open('support_proxy.pkl', 'wb') as file:
                pickle.dump(support_proxy, file)        
        return support_proxy

class anti_ws_bot(ws_bot):
    
    def __init__(self) -> None:
        super(ws_bot,self).__init__()
    
    def configure_proxy_server(self,proxy):
        proxy_ip = proxy[0]  # 代理服务器IP地址
        proxy_port = proxy[1] # 代理服务器端口号
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port)
        socket.socket = socks.socksocket
        # print('configure_proxy_server done.')

    def session_initial(self,proxy):
        ip , port = proxy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[ 500, 502, 503, 504 ],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.proxies = {
                'http': f'socks5://{ip}:{port}',
                'https': f'socks5://{ip}:{port}'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # 'Accept-Language': 'en-US,en;q=0.9',
        }
        session.headers.update(headers)
        session.verify = False # InsecureRequestWarning: Unverified HTTPS request is being made to host 'checkip.amazonaws.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
        return session

    def requests_initial(self,proxy):
        self.configure_proxy_server(proxy)
        headers = super().requests_initial()
        proxies = {
            # 'http': 'http://proxy_host:proxy_port', # for HTTP requests.
            'http': f'socks5://{proxy[0]}:{proxy[1]}',
            'https': f'socks5://{proxy[0]}:{proxy[1]}' # for socks5
        }
        return headers , proxies

if __name__ == '__main__':

    w , check_proxy = anti_ws_bot() , monitor_proxy_server()
    url = 'https://checkip.amazonaws.com/'
    proxy = check_proxy.requests_check_the_proxy_server()

    for ip , port in proxy :
        print('进行实际爬虫测试.')
        try :
            headers , proxies = w.requests_initial((ip,port))
            r = requests.get(url,headers=headers,verify=False)
            if r.status_code == 200 :
                print(r.text)
                print('requests is work.')
            else :
                print(f'请求失败,r.status.code : {r.status_code}')
                logger.error(f'请求失败,r.status.code : {r.status_code}')
        except Exception as e :
            logger.error(f'{e}')

        # try :    
        #     session = w.session_initial((ip,port))
        #     r = session.get(url)
        #     if r.status_code == 200 :
        #         print(r.text)
        #         print('session is work.')
        #     else :
        #         print(f'请求失败,r.status.code : {r.status_code}')
        #         logger.error(f'请求失败,r.status.code : {r.status_code}')
        # except Exception as e :
        #     logger.error(f'{e}')