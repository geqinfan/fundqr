import os.path
import re
import sys
import webbrowser

import pdfplumber
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS


# with pdfplumber.open('D:\\Documents\\南方稳健成长证券投资基金2022年第3季度报告.pdf') as pdf:
def readStocks(file):
    """
    if not os.path.exists(file):
        print(f'文件{file}不存在')
        return -1
    """
    with pdfplumber.open(file) as pdf:
        # print(type(pdf))
        # print(type(pdf.pages), len(pdf.pages))

        i = 1
        stocks = {}
        for page in pdf.pages:
            # print(i, end=' ')
            j = 0
            for table in page.extract_tables():
                # print(table)
                j += 1
                if len(table[0]) == 1:
                    continue
                if table[0][1] != '股票代码' and not table[0][1].isdecimal():
                    continue
                for row in table:
                    if not row[0]:
                        continue
                    if row[0].isdecimal() and row[1].isdecimal() and len(row[1]) >= 5:
                        amount = int(re.sub(',', '', row[3]))  # 去掉持仓数据的‘，’符号
                        stock = row[1] + ' ' + row[2]
                        stocks[stock] = amount
            '''
            if j == 0:
                print()
            '''
            i += 1
    return stocks


def make_visualization(curqr, stocks, prepositions, curpositions):
    """Make visualization of positions data"""
    my_style = LS('#333366', base_style=LCS)
    my_style.title_font_size = 24
    my_style.label_font_size = 14
    my_style.major_label_font_size = 18

    my_config = pygal.Config()
    my_config.x_label_rotation = 45
    my_config.show_legend = False
    my_config.truncate_label = 15
    my_config.show_y_guides = False
    my_config.width = 1000

    chart = pygal.Bar(my_config, style=my_style)

    pathname = os.path.split(curqr)[0]
    filename = os.path.split(curqr)[1]
    print('filename:', filename)
    filebasename = os.path.splitext(filename)[0]
    print('filebasename:', filebasename)
    chart.title = filebasename + '持仓数据'
    chart.x_labels = stocks

    chart.add('', prepositions)
    chart.add('', curpositions)

    filebasename = filebasename + '.svg'
    renderfilename = pathname + '\\' + filebasename
    print(renderfilename)
    chart.render_to_file(renderfilename)
    print('生成文件:', renderfilename)
    webbrowser.open_new_tab(renderfilename)


def analyseStock(curqr, preqr):
    try:
        curStockDict = readStocks(curqr)
        # print(result1)
        # stockSet1 = set(result1.keys())
        # print(stockSet1)

        preStockDict = readStocks(preqr)
        # print(result2)
    except FileNotFoundError:
        print(f'文件:{curqr}或文件:{preqr}不存在')
        return
    print(os.path.basename(curqr))
    print(os.path.basename(preqr))

    stocks, prepositions, curpositions = [], [], []
    for key in preStockDict:
        if key not in curStockDict:
            print(f'{key} 退出前十重仓股')
            stocks.append([key])
            preposition={
                'value':preStockDict[key],
                'label':'退出前十重仓股'
            }
            prepositions.append(preposition)
            curpositions.append(0)

    for key in curStockDict:
        if key not in preStockDict:
            print(f'{key} 新进入前十重仓股，持仓：{curStockDict[key]}')
            stocks.append([key])
            curposition = {
                'value': curStockDict[key],
                'label': '新进入前十重仓股'
            }
            curpositions.append(curposition)
            prepositions.append(0)
        else:
            print('{0} 现持仓：{1},比上季增加（正）或减少（负）：{2}'.format(
                key, curStockDict[key], curStockDict[key] - preStockDict[key]))
            stocks.append([key])
            curposition = {
                'value': curStockDict[key],
                'label': '持仓变化：{}'.format(curStockDict[key] - preStockDict[key])
            }
            curpositions.append(curposition)
            prepositions.append(preStockDict[key])
    make_visualization(curqr, stocks, prepositions,curpositions)


def dealDirectory(path):
    """
    处理一个目录里每个基金季报文件，根据文件名分离出基金名字，然后以基金名字为键，文件名字列表为值加入一个字典，并返回该字典
    :param path:包含基金季报文件的目录
    :return:
    """
    if not os.path.exists(path):
        print(f'路径{path}不存在')
        return
    lst = os.listdir(path)
    pdfFileLst = []
    for filename in lst:
        if filename.endswith('.pdf') and '基金' in filename:
            pdfFileLst.append(filename)
    # print(pdfFileLst)
    fund_dict = {}  # fund_dict是一个字典，字典的key是基金名字，字典的value是该基金对应的文件列表
    for filename in pdfFileLst:
        # ret = re.match(r"(.*)(\d{4}).*(\d).*", filename)
        ret = re.match(r"(.*)(\d{4}).*", filename)
        if ret is None:
            print('Error:can not extract fund name from file: ', filename)
            return

        fund = ret.group(1)  # fund是从文件名里匹配取出的基金名称
        if fund in list(fund_dict.keys()):  # fund_dict里有该基金记录
            fund_dict[fund].append(filename)  # filename添加到对应基金的文件列表中
        else:  # filename是一个新基金的季报文件
            fund_dict[fund] = [filename]  # 插入新记录
    # print(fund_dict)
    return fund_dict


def main():
    if len(sys.argv) == 1:
        print(f'用法1：{sys.argv[0]} 存放基金季度报告文件的目录，当前目录用.表示，目录如含空格，则把目录用双引号包围')
        print(f'用法2：{sys.argv[0]} 基金当前季度报告的文件名 基金前一季度报告的文件名')
        return
    elif len(sys.argv) == 2:
        path = sys.argv[1]
        fund_dict = dealDirectory(path)
        for qrLst in fund_dict.values():
            if len(qrLst) < 2:
                print(f'警告：基金季报文件太少了，至少得有最近两个季报的文件。基金名：{fundName}')
                print()
                continue
            analyseStock(os.path.join(sys.argv[1], qrLst[-1]), os.path.join(sys.argv[1], qrLst[-2]))
            print()
        return
    elif len(sys.argv) == 3:
        analyseStock(sys.argv[1], sys.argv[2])
    else:
        print('参数个数不对')
        return


if __name__ == '__main__':
    main()
