import json


def read_json(path):
    return json.loads(open(path, encoding='utf-8').read())


def write_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def remove_tags(text: str):
    si = text.find('{')
    while si != -1:
        ei = text.find('}', si)
        if ei == -1:
            break
        text = text[:si] + text[ei+1:]
        si = text.find('{')

    si = text.find('<')
    while si != -1:
        ei = text.find('>', si)
        if ei == -1:
            break
        text = text[:si] + text[ei+1:]
        si = text.find('<')

    return text
