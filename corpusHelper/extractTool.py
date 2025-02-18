
def table2json(soup):
    # Extract member variables
    json_res = []
    head = soup.find_all('tr')[0]
    rows = soup.find_all('tr')[1:]  # Skip the header row
    for row in rows:
        cells = row.find_all('td')
        item = {}
        for i in range(len(cells)):
            item[head.find_all('th')[i].text] = cells[i].text
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