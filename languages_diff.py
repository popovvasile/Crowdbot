import json
from pprint import pprint


# def check_strings_1():
#     great_dict = dict(conflicts=[], not_in_new=[], not_in_old=[])
#     with open('languages.json', 'r') as f_old:
#         with open('languages_new.json', 'r') as f_new:
#             data_new = json.load(f_new)
#             data_old = json.load(f_old)
#             for lang in ["en", "ru", "de"]:
#                 old_lang_dict = data_old[lang]
#                 new_lang_dict = data_new[lang]
#                 for old in old_lang_dict:
#                     if old not in new_lang_dict:
#                         great_dict["not_in_new"].append(old)
#                     elif old_lang_dict[old] != new_lang_dict[old]:
#                         great_dict["conflicts"].append({
#                             "key": old,
#                             "old": old_lang_dict[old],
#                             "new": new_lang_dict[old],
#                             "lang": lang
#                         })
#                 for new in new_lang_dict:
#                     if new not in old_lang_dict.keys():
#                         great_dict["not_in_old"].append(new)
#                     elif old_lang_dict[new] != new_lang_dict[new]:
#                         great_dict["conflicts"].append({
#                             "key": new,
#                             "old": old_lang_dict[new],
#                             "new": new_lang_dict[new],
#                             "lang": lang
#                         })
#         with open('conflicts.json', 'w') as conflicts_f:
#             json.dump(great_dict, conflicts_f, sort_keys=False, indent=4, ensure_ascii=False)
#     pprint(great_dict)
#
#
# check_strings_1()
# data = {"en":{}, "ru":{}, "de":{}}
# with open('languages.json', 'r') as f_old:
with open('conflicts.json', 'r') as f_conflicts:
    data = json.load(f_conflicts)["conflicts"]
    conflicts = []
    keys = []
    for conf in data:
        if conf["key"] not in keys:
            conflicts.append(conf)
            keys.append(conf["key"])
    with open('new_conflicts.json', 'w') as conflicts_f:
        json.dump(conflicts, conflicts_f, sort_keys=False, indent=4, ensure_ascii=False)
