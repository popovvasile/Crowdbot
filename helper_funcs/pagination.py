from math import ceil
from telegram import InlineKeyboardButton, ParseMode, InlineKeyboardMarkup


def set_page_key(update, context, start_data=None, name: str = "page"):
    try:
        context.user_data[name] = int(update.callback_query.data)
    except ValueError:
        # This thing is for remember last page after you back to list
        if start_data:
            if update.callback_query.data == start_data:
                context.user_data[name] = 1
        else:
            context.user_data[name] = 1


class Pagination(object):
    def __init__(self, all_data, page=None, per_page=5):
        # self.context = context
        self.all_data = list(all_data)
        self.total_items = len(self.all_data)
        self.per_page = per_page
        self.total_pages = ceil(self.total_items / self.per_page)
        self.page = (1 if not page
                     else self.total_pages if page > self.total_pages
                     else page)
        self.content = self.page_content()

    def page_content(self):
        if self.page == 1:
            data_to_send = self.all_data[:self.per_page]  # .limit(self.per_page)
        else:
            last_on_prev_page = (self.page - 1) * self.per_page
            data_to_send = [i for i in self.all_data[last_on_prev_page:
                                                     last_on_prev_page
                                                     + self.per_page]]
        return data_to_send

    def keyboard(self, buttons=None):
        buttons = list() if not buttons else buttons
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

    def send_keyboard(self, update, context, buttons=None, text=""):
        if self.total_pages > 1:
            context.user_data['to_delete'].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"{text}\n\n*Current page:* `{self.page}`",
                    reply_markup=self.keyboard(buttons),
                    parse_mode=ParseMode.MARKDOWN))
        elif buttons or text:
            context.user_data['to_delete'].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"{text}\n\n*Current page:* `{self.page}`",
                    reply_markup=self.keyboard(buttons),
                    parse_mode=ParseMode.MARKDOWN))
