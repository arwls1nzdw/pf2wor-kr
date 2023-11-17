import json

from dataloader import get_data_kr, get_data_bp

bp = get_data_bp()
bpFilenameMap = dict(
    map(lambda p: (p.filename.split('/')[-1], p), bp.filelist))


def http_get(url):
    from urllib import request
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"}
    req = request.Request(url, headers=headers)
    res = request.urlopen(req)
    html = res.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def to_jbp_name(text):
    text_filter = [
        ('`', ''),
        (',', ''),
        ("'", ''),
        ('-', '')
    ]
    for f in text_filter:
        text = text.replace(f[0], f[1])
    return ''.join(map(lambda s: s.capitalize(), text.split(' ')))


def postprocess_td(td):
    for br in td.find_all('br'):
        br.replace_with('\n')
    for li in td.find_all('li'):
        li.replace_with('\n'+li.text)


def get_jbp_descKey(name, suffixes, postfixes):
    suffixes = [''] + suffixes
    postfixes = [''] + postfixes

    get_desc_key = [
        lambda jbpdata: jbpdata['Data']['m_Description']['m_Key'],
        lambda jbpdata: jbpdata['Data']['m_Description']['Shared']['stringkey']
    ]
    for sf, pf in zip(suffixes, postfixes):
        jbpname = f"{sf}{to_jbp_name(name)}{pf}.jbp"
        jbp = bpFilenameMap.get(jbpname)
        if jbp is not None:
            break
        if jbp is None:
            continue

        jbpdata = json.loads(bp.read(jbp).decode('utf-8'))
        for get_desc_key_func in get_desc_key:
            try:
                desc_key = get_desc_key_func(jbpdata)
                break
            except:
                continue
        else:
            continue
        if desc_key in get_data_kr()['strings']:
            yield desc_key
    return


def scrap_spell():
    soup = http_get(
        "https://namu.wiki/w/Pathfinder:%20Wrath%20of%20the%20Righteous/%EC%A0%84%ED%88%AC/%EC%A3%BC%EB%AC%B8")
    trlist = soup.find_all('tr')
    tdlist = list(map(lambda tr: tr.find_all('td'), trlist))

    changes = {}
    for i, tr in enumerate(trlist):
        if not (len(tdlist[i]) == 1 and i > 0 and len(tdlist[i-1]) == 9):
            continue

        td_meta = tdlist[i-1]
        td_desc = tdlist[i]

        postprocess_td(td_desc[0])

        name = td_meta[0].text
        desc = td_desc[0].text

        suffixes = ['Ritual']
        postfixes = ['Cast', 'Base', 'Ability']
        for desc_key in get_jbp_descKey(name, suffixes, postfixes):
            changes[desc_key] = desc

    return changes


def scrap_feats():
    soup = http_get(
        "https://namu.wiki/w/Pathfinder:%20Wrath%20of%20the%20Righteous/%EC%A0%84%ED%88%AC/%ED%94%BC%ED%8A%B8")
    trlist = soup.find_all('tr')
    tdlist = list(map(lambda tr: tr.find_all('td'), trlist))

    changes = {}
    for i in range(len(trlist)):
        td = tdlist[i]
        if len(td) != 4:
            continue
        name = td[0].text
        name = name.replace('[자세]', '')
        postprocess_td(td[2])
        desc = td[2].text
        if name == "이름":
            continue

        suffixes = []
        postfixes = ['Feature', 'MythicFeat', 'Selection']

        for desc_key in get_jbp_descKey(name, suffixes, postfixes):
            changes[desc_key] = desc

    return changes
