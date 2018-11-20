import requests
import json

def get_proxy():
    new_proxy = requests.get('http://gimmeproxy.com/api/getProxy?anonymityLevel=1&country=US&supportsHttps=true&protocol=http')
    prox = json.loads(new_proxy.text)
    return prox['ipPort']

ofile = open('proxies.csv', 'w')

for i in range(100):
    proxy_ip = get_proxy()
    print('got proxy {}'.format(proxy_ip))
    ofile.write(proxy_ip)
    ofile.write('\n')

ofile.close()
