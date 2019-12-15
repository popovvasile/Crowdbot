from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

from helper_funcs.misc import delete_messages

from requests.exceptions import RequestException
from requests.models import Response
from modules.shop.helper.strings import strings
from modules.shop.helper.keyboards import back_btn

from math import ceil


def set_page_key(update, context, name: str = "page"):
    try:
        context.user_data[name] = int(update.callback_query.data)
    except ValueError:
        context.user_data[name] = 1


class APIPaginatedPage(object):
    def __init__(self, resp: Response):
        if resp.status_code != 200:
            raise RequestException
        else:
            self.data = resp.json()

    def start(self, update, context, title: str, no_item_str: str):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context)
        # Title of paginated page
        context.user_data['to_delete'].append(
            context.bot.send_message(update.effective_chat.id,
                                     title.format(self.data["items_total"]),
                                     ParseMode.MARKDOWN))

        if self.data["items_total"] == 0:
            context.user_data['to_delete'].append(
                context.bot.send_message(update.effective_chat.id,
                                         no_item_str))

    def send_pagin(self, update, context,
                   back_button_data="back_to_main_menu"):
        # todo pass callback_data for back_button instead of button
        if self.data["total_pages"] > 1:
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    f"|{num['page']}|"
                    if num["page"] == context.user_data["page"]
                    else "..." if num["page"] is None else num["page"],
                    callback_data=str(num["page"]))
                  for num in self.data["iter_pages"]]] +
                [[back_btn(back_button_data, context=context)]])
        else:
            # kb = keyboards["back_to_main_menu_keyboard"]
            kb = InlineKeyboardMarkup([[back_btn(back_button_data, context=context)]])
        context.user_data["to_delete"].append(
            context.bot.send_message(update.effective_chat.id,
                                     context.bot.lang_dict["shop_admin_current_page"].format(
                                         context.user_data["page"]),
                                     reply_markup=kb,
                                     parse_mode=ParseMode.MARKDOWN))


class Pagination(object):
    def __init__(self, page, per_page, all_data):
        self.page = page
        self.per_page = per_page
        self.all_data = all_data
        self.total_pages = ceil(len(self.all_data) / self.per_page)

    def page_content(self):
        if self.page == 1:
            data_to_send = self.all_data[:self.per_page]
        else:
            last_on_prev_page = (self.page - 1) * self.per_page
            data_to_send = [
                i for i in self.all_data[last_on_prev_page:
                                         last_on_prev_page + self.per_page]]
        return data_to_send

    def keyboard(self, btns=None):
        btns = list() if not btns else btns
        # self.total_pages = ceil(len(self.all_data) / self.per_page)
        pages_keyboard = [[]] + btns
        # if only one page don't show pagination
        if self.total_pages <= 1:
            pass
        # if total pages count <= 8 - show all 8 buttons in pagination
        elif 2 <= self.total_pages <= 8:
            for i in range(1, self.total_pages + 1):
                pages_keyboard[0].append(
                    InlineKeyboardButton('|' + str(i) + '|', callback_data=i)
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
                    pages_keyboard[0].append(InlineKeyboardButton(
                        '...', callback_data=layout[num - 1] + 1
                        if num > layout.index(self.page)
                        else layout[num + 1] - 1))
                else:
                    pages_keyboard[0].append(
                        InlineKeyboardButton(
                            '|' + str(i) + '|', callback_data=i)
                        if i == self.page else
                        InlineKeyboardButton(str(i), callback_data=i))
        return InlineKeyboardMarkup(pages_keyboard)

    def send_pagin(self, update, context, btns=None, text=None):
        if self.total_pages > 1:
            context.user_data['to_delete'].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    f"{text}\n\n*Current page:* `{self.page}`"
                    if text else f"*Current page:* `{self.page}`",
                    reply_markup=self.keyboard(btns),
                    parse_mode=ParseMode.MARKDOWN))
