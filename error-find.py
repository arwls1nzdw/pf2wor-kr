import dataloader
import utils


def erase_tags(text):
    while True:
        start = text.find('{')
        end = text.find('}')
        if start == -1 or end == -1:
            break

        text = text[:start] + text[end+1:]

    return text


en = dataloader.get_data_en()['strings']
kr = dataloader.get_data_kr_patches()

token_en = "restoration".lower()
token_kr = '상태회복'

errors = {}
for k, v_en in en.items():
    if k not in kr:
        continue

    v_en = erase_tags(v_en.lower())
    if token_en not in v_en:
        continue

    v_kr = erase_tags(kr[k].lower())
    if v_en.count(token_en) > v_kr.count(token_kr):
        errors[k] = {
            'en': en[k],
            'kr': kr[k],
        }

    # if token_kr in kr[k]:
    #     errors[k] = {
    #         'en': en[k],
    #         'kr': kr[k],
    #     }

print(f'Found {len(errors)} errors')

utils.write_json(errors, f'errors.json')
