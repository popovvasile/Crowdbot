# #!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from telegram.ext import RegexHandler, CommandHandler, run_async, ConversationHandler, MessageHandler, Filters
from database import chats_table, tags_table
from ru_modules.helper_funcs.auth import if_admin

CHOOSING_TAGS = 1


class TagBot(object):   # TODO allow users to send messages to the bots admins
    # def __init__(self):
    #     chats_table = db['tags']

    @staticmethod
    def initiate_chat_id(update):
        chat_id = update.message.chat_id
        txt = ""
        if update.message.text:
            txt = txt + update.message.text
        elif update.message.caption:
            txt = txt + update.message.caption
        return chat_id, txt

    
    def handle_add(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        if update.message.chat.type == "group":
            bot.send_message(chat_id, "Please type the tags that you want to add to your chat," +
                             " like this (notice the /t command): \n" +
                             "/t #tag1 #tag2 ...")
        elif update.message.chat.type == "private":
            bot.send_message(chat_id, "Please type the tags that you want to add to your chat, like this: \n" +
                             "#tag1 #tag2 ...\n To cancel this command click /cancel")
        tags_names = []
        for chat in chats_table.find({"bot_id": bot.id}):
            if chat["tag"] in tags_names:
                pass
            else:
                tags_names.append(chat["tag"])
        response = "<b>Current list of tags used by other users:</b>"
        for tag in sorted(tags_names):
            response = response + "\n<b>" + tag + "</b>"
        bot.send_message(chat_id, response, parse_mode="HTML")

        return CHOOSING_TAGS

    def handle_add_tags(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        txt_split = txt.strip().split(" ")
        tags = []
        if "" in txt_split:
            txt_split.remove("")
        if "/t" in txt_split:
            txt_split.remove("/t")

        for word in txt_split:
            if word[0] == "#":
                tags.append(word)
        for tag in tags:
            if tag in ["#admin", "#user"]:
                bot.send_message(chat_id, "You can't assign this tag to yourself: {}".format(tag))
            else:
                name = ""
                chat = chats_table.find_one({"tag": tag, 'chat_id': chat_id})
                if update.message.chat.type == "private":
                    name = name + "Personal chat " + update.message.chat.first_name
                else:
                    name = name + "Group chat " + update.message.chat.title
                if chat is None:
                    chats_table.insert({'chat_id': chat_id,
                                        'name': name,
                                        'user_name': update.message.chat.full_name,
                                        "tag": tag,
                                        "bot_id": bot.id,
                                        'user_id': update.message.from_user.id})

                    tags_table.insert({"tag": tag, "bot_id": bot.id})
                bot.send_message(chat_id, name + " added with tag " + tag)
        return ConversationHandler.END

    
    def handle_rm_chat_tag(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        chats_list_of_dicts = chats_table.find({
                                    "chat_id": chat_id,
                                    "bot_id": bot.id})
        tags_list = [command['tag'] for command in chats_list_of_dicts]
        if "#admin" in tags_list:
            tags_list.remove("#admin")
        if "#user" in tags_list:
            tags_list.remove("#user")
        reply_keyboard = [tags_list]
        bot.send_message(chat_id, "Choose the tag that you want to delete from your chat."
                                  "To cancel this command click /cancel",
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSING_TAGS

    def handde_rm_chat_tag_final(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        tag = txt
        chat = chats_table.find_one({'tag': tag})
        if tag not in ['#admin', "#user"]:
            if chat is not None:
                if tag == chat["tag"]:
                    if chat['chat_id'] == chat_id:
                        chats_table.delete_one({"tag": tag, "chat_id": chat_id})
                        bot.send_message(chat_id, "Tag " + tag + "deleted from taglist.")
                    else:
                        bot.send_message(chat_id, "You can't delete a chat's tag from a different chat.")
            else:
                bot.send_message(chat_id, "This tag doesn't exist on TagList")

            return ConversationHandler.END
        else:
            bot.send_message(chat_id, "You can't delete this tag. This is not allowed. Choose another tag")

    
    def handle_rmtag(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        chats_list_of_dicts = chats_table.find({
                                    "chat_id": chat_id,
                                    "bot_id": bot.id})
        tags_list = [command['tag'] for command in chats_list_of_dicts]
        reply_keyboard = [tags_list]
        bot.send_message(chat_id,
                         "Please choose the tag that you want to delete. To cancel click /cancel"
                         "Remember, this tag will be deleted from all chats and users",
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSING_TAGS

    def handde_rmtag_final(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        tag = txt
        chat = chats_table.find_one({'tag': tag})
        if chat is not None:
            if tag == chat["tag"]:
                chats_table.delete({"tag": tag})
                tags_table.delete({"tag": tag})
                bot.send_message(chat_id, "Tag " + tag + "deleted from taglist.")
        else:
            bot.send_message(chat_id, "Tag doesn't exist on TagList")

        return ConversationHandler.END

    
    def handle_taglist(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        tags_names = []
        for chat in chats_table.find({"bot_id": bot.id}):
            if chat["tag"] in tags_names:
                pass
            else:
                tags_names.append(chat["tag"])
        tags_names = list(set(tags_names))
        response = "This is the list of tags assinged in your chatbot.\n To remove one of these tags, click /rmtag"
        for tag in sorted(tags_names):
            response = response + "\n<b>" + tag + "</b>"
        bot.send_message(chat_id, response, parse_mode="HTML")

    def handle_send(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        txt_split = txt.strip().split(" ")
        i = 0
        tags = []

        while "" in txt_split:
            txt_split.remove("")

        while i < len(txt_split) and txt_split[i][0] == "#":
            tags.append(txt_split[i].lower())
            i += 1
        if update.message.reply_to_message is None:
            approved = []
            rejected = []
            sent = []
            for tag in tags:
                chats = chats_table.find({"tag": tag})
                for chat in chats:
                    if chat['chat_id'] != chat_id:
                        if not any(sent_d['chat_id'] == chat['chat_id'] for sent_d in sent):
                            sent.append(chat['chat_id'])
                            approved.append(chat['name'])
                            bot.forward_message(chat['chat_id'], chat_id, update.message.message_id)
                            bot.send_message(chat_id,
                                             "Sent message to tags <i>" + ", ".join(tags) + "</i>",
                                             parse_mode="HTML")
                            return
                    else:
                        rejected.append(tag)
            if len(rejected) > 0:
                bot.send_message(chat_id,
                                 "Failed to send messages to tags <i>" + ", ".join(rejected) + "</i>",
                                 parse_mode="HTML")
                return
            return
        else:
            bot.send_message(chat_id, "Failed to send a message which is  a reply to another message")
        return

    
    def handle_mytags(self, bot, update):
        chat_id, txt = self.initiate_chat_id(update)
        mytags = chats_table.find({"chat_id": chat_id})
        if mytags.count() >= 1:
            bot.send_message(chat_id,
                             "This is the list of tags assigned to your chat:")
            for mytag in mytags:
                bot.send_message(chat_id, "{}".format(mytag["tag"]))
        else:
            bot.send_message(chat_id,
                             "You have no tags assigned to your chat. To add a tag, click /add_chat_tag")

    def cancel(self, bot, update):
        update.message.reply_text("Ok, no tags this time)")
        return ConversationHandler.END


__mod_name__ = "Tags"
__admin_help__ = """
 - /taglist to see the entire list of tags
 - /mytags  returns the tags assigned to you
 - /add_chat_tag  assign a tag to your chat
 - /rm_chat_tag  remove a tag assigned to you
 - /rmtag to remove the tag from all chats
 - #tag "some text"  -  to forward a message to everybody who has this hashtag
 To send a message to all users of the bot, use tag #all
 To send a message to all admins use #admin tag
 To send a message to all users use #user tag
"""
__visitor_help__ = """
 - /mytags  returns the tags assigned to you
 - /add_chat_tag  assign a tag to your chat
 - /rm_chat_tag  remove a tag assigned to you
"""

__admin_keyboard__ = [["/taglist", "/mytags"],
                      ["/add_chat_tag", "/rm_chat_tag"],
                      ["/rmtag", "/cancel"]]
__visitor_keyboard__ = [["/mytags", "/add_chat_tag"],
                     ["/rm_chat_tag", "/cancel"]]

ADD_TAGS_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[CommandHandler("add_chat_tag", TagBot().handle_add)],

    states={
        CHOOSING_TAGS: [MessageHandler(Filters.entity('hashtag'),
                                       TagBot().handle_add_tags)],
    },

    fallbacks=[CommandHandler('cancel', TagBot().cancel,
               MessageHandler(filters=Filters.command, callback=TagBot().cancel)),
               RegexHandler("^done$", TagBot().cancel, pass_user_data=True)]
)
RM_CHAT_TAGS_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[CommandHandler("rm_chat_tag", TagBot().handle_rm_chat_tag)],

    states={
        CHOOSING_TAGS: [MessageHandler(Filters.text, TagBot().handde_rm_chat_tag_final)],
    },

    fallbacks=[CommandHandler('cancel', TagBot().cancel,
               MessageHandler(filters=Filters.command, callback=TagBot().cancel))]
)


RM_TAGS_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[CommandHandler("rmtag", TagBot().handle_rmtag)],

    states={
        CHOOSING_TAGS: [MessageHandler(Filters.text, TagBot().handde_rmtag_final)],
    },

    fallbacks=[CommandHandler('cancel', TagBot().cancel,
               MessageHandler(filters=Filters.command, callback=TagBot().cancel))]
)


TAGLIST_HANDLER = CommandHandler("taglist", TagBot().handle_taglist)
MYTAGLIST_HANDLER = CommandHandler("mytags", TagBot().handle_mytags)
SEND_BY_HANSHTAG_HANDLER = RegexHandler("^\#", TagBot().handle_send)
