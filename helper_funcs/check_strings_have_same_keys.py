# from helper_funcs.lang_strings.strings import ru, en

import json
# todo make a proper check strings script

# def check_dicts():
#     for key in en:
#         if key in ru:
#             pass
#         else:
#             ru[key]=en[key]
#     for key in ru:
#         if key in en:
#             pass
#         else:
#             en[key]=ru[key]
#     data = {"en": en,
#             "ru": ru}
#     with open('languages.json', 'w') as fp:
#         json.dump(data, fp, sort_keys=True, indent=4, ensure_ascii=False)

def check_strings_1():
    with open('languages.json', 'r') as f_in:
        lang_dict = json.load(f_in)

        for key in lang_dict["en"]:
            if key in lang_dict["ru"]:
                continue
            else:
                lang_dict["ru"][key] = lang_dict["en"][key]
        for key in lang_dict["ru"]:
            if key in lang_dict["en"]:
                if lang_dict["ru"][key].count("{}") != lang_dict["en"][key].count("{}"):
                    lang_dict["ru"][key] = lang_dict["en"][key]
            else:
                lang_dict["en"][key] = lang_dict["ru"][key]

        with open('languages2.json', 'w') as fp:
            json.dump(lang_dict, fp, sort_keys=True, indent=4, ensure_ascii=False)


check_strings_1()

def check_strings_2():
    with open('languages.json', 'r') as f_in:
        lang_dict = json.load(f_in)

        for key in lang_dict["en"]:
            if key in lang_dict["de"]:
                continue
            else:
                lang_dict["de"][key] = lang_dict["en"][key]
        for key in lang_dict["de"]:
            if key in lang_dict["en"]:
                if lang_dict["de"][key].count("{}") != lang_dict["en"][key].count("{}"):
                    lang_dict["de"][key] = lang_dict["en"][key]
            else:
                lang_dict["en"][key] = lang_dict["de"][key]

        with open('languages2.json', 'w') as fp:
            json.dump(lang_dict, fp, sort_keys=True, indent=4, ensure_ascii=False)


check_strings_2()
