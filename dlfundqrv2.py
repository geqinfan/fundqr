import os
import requests
import re

from dlfilebyurl import download


def getfileurl(url, params):
    headers = {
        'Accept': '*/*',
        'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&code=202001&name=%E5%8D%97%E6%96%B9%E7%A8%B3%E5%81%A5&orgId=jjjl0000033,',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }
    response = requests.request("POST", url, params=params, headers=headers)
    print(type(response))
    print(response.status_code)
    print(response.text)
    response_dict = response.json()
    print(response_dict.keys())
    print(response_dict['fileUrl'])
    return response_dict


# url = 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&code=202001&name=%E5%8D%97%E6%96%B9%E7%A8%B3%E5%81%A5&orgId=jjjl0000033#fund'
# url = 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&code=202001&name=南方稳健&orgId=jjjl0000033'
# url = url.encode('utf-8')


def get_announce_dicts(url, params, headers):
    response = requests.request("POST", url, params=params, headers=headers)
    response_dict = response.json()
    announce_dicts = response_dict['announcements']
    return announce_dicts


url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

configfile='基金代码配置文件.txt'
if not os.path.exists(configfile):
    print(f'文件:{configfile} 不存在')
    exit(-1)

with open(configfile) as file_object:
    contents = file_object.read()
    fundcodes = eval(contents)

    for _, code in fundcodes.items():
        params = {
            'pageNum': 1,
            'pageSize': 30,
            'stock': code[0],
            'isHLtitle': True
        }

        referer = 'http://www.cninfo.com.cn/new/disclosure/stock?stockCode=' + code[0].split(sep=',')[0] + '&orgId=' + \
                  code[0].split(sep=',')[1]

        headers = {
            'Accept': '*/*',
            'Referer': referer,
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        }

        announce_dicts = get_announce_dicts(url, params, headers)

        for i in range(len(announce_dicts)):
            '''
            print('%2d secCode:%s secName:%s 公告日期：%d 公告标题：%s' % (
                i + 1, announce_dicts[i]['secCode'], announce_dicts[i]['secName'], announce_dicts[i]['announcementTime'],
                announce_dicts[i]['announcementTitle']))
            '''
            # if announce_dicts[i]['announcementTitle'].find(code[1]) != -1:
            pattern = code[1]
            title = announce_dicts[i]['announcementTitle']
            #print(pattern)
            #print(title)
            ret = re.match(pattern, title)
            if ret is None:
                #print("Error:文件模式匹配失败")
                pass
            else:
                quarter = ret.group(3)
                if quarter == '一':
                    quarter = '1'
                if quarter == '二':
                    quarter = '2'
                if quarter == '三':
                    quarter = '3'
                if quarter == '四':
                    quarter = '4'
                #print(quarter)
                adjustfilename = ret.group(1) + ret.group(2) + '年度第' + quarter + '季度报表.pdf'
                pdffileurl = 'http://static.cninfo.com.cn/' + announce_dicts[i]['adjunctUrl']

                download(pdffileurl, adjustfilename)
                '''
                url = 'http://www.cninfo.com.cn/new/announcement/bulletin_detail'
                print(url)
                params2 = {
                    'announceId': announce_dicts[i]['announcementId'],
                    'flag': False,
                    'announceTime': '2023-01-20'
                }
                response_dict=getfileurl(url,params2)
                download(response_dict['fileUrl'],announce_dicts[i]['announcementTitle'])
                '''
