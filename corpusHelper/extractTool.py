import bs4


def table2json(soup):
    json_res = []
    # 获取表头行（第一个tr）
    header_row = soup.find_all('tr')[0]
    # 提取表头单元格（使用td而不是th）
    headers = [td.get_text(strip=True) for td in header_row.find_all('th')]  # 修正点1：使用td
    
    # 遍历数据行（从第二个tr开始）
    for row in soup.find_all('tr')[1:]:
        cells = row.find_all('td')
        # 确保单元格数量与表头一致
        if len(cells) != len(headers):
            continue  # 跳过格式异常的行

        item = {}
        for i, cell in enumerate(cells):
            # 使用表头作为键，去除单元格内容中的空白
            item[headers[i]] = cell.get_text(strip=True)  # 修正点2：直接使用预处理的headers

        json_res.append(item)

    return json_res
def table2text(soup):
    # Extract member variables
    text_res = []
    head = soup.find_all('tr')[0]
    rows = soup.find_all('tr')[1:]  # Skip the header row
    for row in rows:
        cells = row.find_all('td')
        item = {}
        for i in range(len(cells)):
            item[head.find_all('th')[i].text] = cells[i].text
        text_res.append(item)
    return text_res

def object_analyzer(soup):
    title = ''
    meta_api = ''
    system_capability = ''
    table = ''

    title_soup = soup.find('h4')
    meta_api_soup = soup

if __name__ == '__main__':
    with open('./test.html') as f:
        content = f.read()
        soup = bs4.BeautifulSoup(content)
        print(table2json(soup))