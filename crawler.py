import requests
from bs4 import BeautifulSoup as BS

url = 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&code=202001&name=%E5%8D%97%E6%96%B9%E7%A8%B3%E5%81%A5&orgId=jjjl0000033&keywords=#fund'
req = requests.get(url)
html = req.text
# print(html)
soup = BS(html, 'html.parser')
for link in soup.find_all('a', href=True):
    print(type(link))
    print(link.text)
    print(link['href'])
