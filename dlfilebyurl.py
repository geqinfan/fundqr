import requests


def download(url, filename):
    req = requests.get(url)
    #    filename = url.split('/')[-1]
    if req.status_code != 200:
        print('下载异常')
        return
    try:
        with open(filename, 'wb') as f:
            # req.content为获取html的内容
            f.write(req.content)
            print('文件:%s 下载成功' % filename)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    url = 'http://static.cninfo.com.cn/finalpage/2023-01-20/1215717029.PDF'  # xxx为url，根据自己需求输入
    download(url, "1215717029.PDF")
