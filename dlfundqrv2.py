import os
import sys
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


"""
Request URL，服务器端处理客户查询请求的接口
打开巨潮资讯网，定位到基金页面，打开浏览器的开发者工具（F12），选择NetWork，选择Fetch/XHR，此时在页面输入基金代码，点击查询，此时在devtools中可以看到，返回了一个query，
在对应的Headers标签页可以查到Request URL
在referer指向的URL处也可以查到
具体可参见这篇文章：用python批量获取公募基金季报pdf，https://blog.51cto.com/u_14328065/2849058
"""


def dlfundqr(maxfilenum=1):
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

    configfile = '基金代码配置文件.txt'
    if not os.path.exists(configfile):
        print(f'文件:{configfile} 不存在')
        exit(-1)

    with open(configfile) as file_object:
        contents = file_object.read()
        funds = eval(contents)

        for item in funds:
            params = {
                'pageNum': 1,
                'pageSize': 30,
                'stock': item['jjdm'] + ',' + item['orgId'],  # referer中stock参数的值
                'isHLtitle': True
            }

            """
            referer:客户端请求的URL，获取方法是在巨潮资讯网首页顶端输入基金代码点击搜索按钮，在得到的页面中点击最新公告右端的更多>，查看点出的页面地址栏信息
            """
            # referer = 'http://www.cninfo.com.cn/new/disclosure/stock?stockCode=' + item['jjdm'] + '&orgId=' + item['orgId']
            referer = 'http://www.cninfo.com.cn/new/disclosure/'
            # print('referer:', referer)

            headers = {
                'Accept': '*/*',
                'Referer': referer,
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
            }

            pattern = item['pattern']
            # print(pattern)
            announce_dicts = get_announce_dicts(url, params, headers)
            dictslen = len(announce_dicts)
            dlfilenum = 0
            for i in range(dictslen):
                '''
                print('%2d secCode:%s secName:%s 公告日期：%d 公告标题：%s' % (
                    i + 1, announce_dicts[i]['secCode'], announce_dicts[i]['secName'], announce_dicts[i]['announcementTime'],
                    announce_dicts[i]['announcementTitle']))
                '''
                # if announce_dicts[i]['announcementTitle'].find(code[1]) != -1:

                title = announce_dicts[i]['announcementTitle']
                # print(title)
                ret = re.match(pattern, title)
                if ret is None:
                    # print("Error:文件模式匹配失败")
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
                    # print(quarter)
                    adjustfilename = ret.group(1) + ret.group(2) + '年第' + quarter + '季度报告.pdf'
                    pdffileurl = 'http://static.cninfo.com.cn/' + announce_dicts[i]['adjunctUrl']
                    # print(pdffileurl)
                    download(pdffileurl, adjustfilename)
                    dlfilenum += 1
                    if dlfilenum == maxfilenum:
                        break
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


def main():
    if len(sys.argv) == 1:
        dlfundqr()
        return
    elif len(sys.argv) == 2:
        try:
            dlfundqr(int(sys.argv[1]))
        except ValueError:
            print("最大下载文件数参数必须是整数")
        return
    else:
        print('参数个数不对')
        return


if __name__ == '__main__':
    main()
