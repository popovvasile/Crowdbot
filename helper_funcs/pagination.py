from math import ceil
from telegram import InlineKeyboardButton, ParseMode, InlineKeyboardMarkup
from helper_funcs.lang_strings.help_strings import string_dict


# todo remember the page
def set_page_key(update, context, start_data, name: str = "page"):
    try:
        context.user_data[name] = int(update.callback_query.data)
    except ValueError:
        if update.callback_query.data == start_data:
            context.user_data[name] = 1


class Pagination(object):
    def __init__(self, context, per_page, all_data):
        self.context = context
        self.all_data = all_data
        self.per_page = per_page
        self.total_pages = ceil(self.all_data.count() / self.per_page)
        self.page = 1 if not context.user_data.get("page") \
            else self.total_pages \
            if self.context.user_data["page"] > self.total_pages \
            else self.context.user_data["page"]

    def page_content(self):
        if self.page == 1:
            data_to_send = self.all_data.limit(self.per_page)
        else:
            last_on_prev_page = (self.page - 1) * self.per_page
            data_to_send = [i for i in self.all_data[last_on_prev_page:
                                                     last_on_prev_page
                                                     + self.per_page]]
        return data_to_send

    def keyboard(self, buttons):
        # total_pages = ceil(self.all_data.count() / self.per_page)
        pages_keyboard = [[]] + buttons
        # if only one page don't show pagination
        if self.total_pages <= 1:
            pass
        # if total pages count <= 8 - show all 8 buttons in pagination
        elif 2 <= self.total_pages <= 8:
            for i in range(1, self.total_pages + 1):
                pages_keyboard[0].append(
                    InlineKeyboardButton(f"|{i}|", callback_data=i)
                    if i == self.page else
                    InlineKeyboardButton(str(i), callback_data=i))
        # if total pages count > 8 - create pagination
        else:
            arr = [i if i in range(self.page - 1, self.page + 3) else
                   i if i == self.total_pages else
                   i if i == 1 else
                   # str_to_remove
                   '' for i in range(1, self.total_pages + 1)]
            p_index = arr.index(self.page)
            layout = list(dict.fromkeys(arr[:p_index])) + \
                list(dict.fromkeys(arr[p_index:]))
            for num, i in enumerate(layout):
                if i == '':
                    pages_keyboard[0].append(
                        InlineKeyboardButton(
                            '...', callback_data=layout[num - 1] + 1
                            if num > layout.index(self.page) else
                            layout[num + 1] - 1))
                else:
                    pages_keyboard[0].append(
                        InlineKeyboardButton(f"|{i}|", callback_data=i)
                        if i == self.page else
                        InlineKeyboardButton(str(i), callback_data=i))
        return InlineKeyboardMarkup(pages_keyboard)

    def send_keyboard(self, update, buttons, text=""):
        cur_page_str = string_dict(
            self.context.bot)['current_page'].format(self.page)
        self.context.user_data['to_delete'].append(
            self.context.bot.send_message(update.effective_chat.id,
                                          f"{text}\n{cur_page_str}",
                                          reply_markup=self.keyboard(buttons),
                                          parse_mode=ParseMode.MARKDOWN))
