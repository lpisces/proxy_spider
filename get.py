#!/usr/bin/env python
# -*- coding:utf-8 -*- 

import requests
from bs4 import BeautifulSoup as bs
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import time

BASE_URL = 'http://www.kuaidaili.com/proxylist/'
PAGE = 10
TEST_URL = 'http://www.sina.com.cn/'
#TEST_URL = 'http://www.18684.com/'

def get_proxy(url):
  r = requests.get(url)
  soup = bs(r.text, 'html5lib')
  tr = soup.select("#index_free_list tbody tr")
  lst = []
  for t in tr:
    td = t.select("td")
    ip = td[0].text
    port = td[1].text
    anonymous = td[2].text
    method = td[4].text
    protocol = td[3].text
    position = td[5].text
    resp_time = td[6].text
    check_time = td[7].text
    lst.append((ip, port, anonymous, method, protocol, position, resp_time, check_time))
  return lst

def lst():
  proxy = []
  for i in range(1, PAGE + 1):
    url = BASE_URL + str(i)
    lst = get_proxy(url)
    proxy += lst * 3
  return proxy

def format(proxy):
  ip = proxy[0]
  port = proxy[1]
  protocol = proxy[4].split(",")
  proto = []
  for p in protocol:
    proto.append(p.replace(" ", ""))
  if 'HTTPS' in proto:
    pp = "%s://%s:%s" % ("https", ip, port)
  else:
    pp = "%s://%s:%s" % ("http", ip, port)
  return pp

def check(proxy, t = True, retry = 3):
  if t:
    pp = format(proxy)
  else:
    pp = proxy
  proxies = {"http":pp, "https":pp}
  try:
    r = requests.get(TEST_URL, proxies = proxies, verify=False, timeout=5)
    if r.status_code == 200:
      ret = True
    else:
      ret = False
  except Exception as e:
    ret = False
  msg = "%s:\t%s"
  print msg % (pp, str(ret))
  return ret

def pool():
  pool = ThreadPool(8)
  l = lst()
  r = pool.map(check, l)
  pool.close() 
  pool.join()
  ret = []
  for i in range(len(l)):
    if r[i]:
      ret.append(l[i])
  save(ret)

def save(lst, out = 'pool.txt'):
  proxy = []
  for i in lst:
    proxy.append(format(i))
  text = "\n".join(proxy) + "\n"
  with open(out, 'a+') as f:
    f.write(text)

def check_pool(out = 'pool.txt', retry = 10):
  print "check pool"
  with open(out, 'r') as f:
    lst = f.read()
  lst = list(set(lst.split("\n")))
  r = []
  cnt = 0
  for i in lst:
    if len(i) == 0:
      continue
    while cnt < retry:
      if check(i, False):
        r.append(i)
        break
      time.sleep(3)
      cnt += 1
  text = "\n".join(r) + "\n"
  with open(out, 'w') as f:
    f.write(text)

if __name__ == "__main__":
  pool()
  check_pool()
