from helper_funcs.lang_strings.strings import RUS, ENG
import json


def check_dicts():
    for key in ENG:
        if key in RUS:
            pass
        else:
            RUS[key]=ENG[key]
    for key in RUS:
        if key in ENG:
            pass
        else:
            ENG[key]=RUS[key]
    data = {"ENG": ENG,
            "RUS": RUS}
    with open('languages.json', 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4, ensure_ascii=False)
check_dicts()