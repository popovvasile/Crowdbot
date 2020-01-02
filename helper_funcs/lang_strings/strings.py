#!/usr/bin/env python
# -*- coding: utf-8 -*-
from database import chatbots_table

# Telegram emoji. Original names
emoji = dict(
    trash="🗑",
    recycle="♻️",
    white_check_mark="✅",
    hammer_and_wrench="🛠",
    x="❌",
    black_square_button="🔲",
    confused="😕",
    arrow_down="⬇️",
    arrow_right="➡️",
    money_with_wings="💸",
    gift_heart="💝",
    page_with_curl="📃",
    ticket="🎫",
    shirt="👔",
    ballot_box="🗳",
    plus="➕",
    gear="⚙️",
    bar_chart="📊",
    book="📖",
    bust_in_silhouette="👤",
    disappointed_relieved="😥",
    ok_hand="👌",
    family_mwgb="👨‍👩‍👧‍👦",
    email="📧",
    new="🆕")

ENG = dict(
    you_have_been_reg=", you have been registered as an authorized user of this bot.\n\n"
                      "Enter your password or click /cancel",
    no_pass_provided="No password provided. Please send a  valid password or click Back",
    wrong_pass_admin="Wrong password. Please send a  valid password or click Back",
    yes="YES",
    no="NO",
    register_str="Please write your email to register yourself as an admin for this bot",
    create_button_str="📌 Create",
    start_help="Welcome! My name is {} and I am ready to use!",
    my_channels="🛠My Channels",
    channels="Channels",
    buttons=" Buttons",
    shop="Shop",
    donations="Donations",
    messages="✉️ Messages ",
    add_channel='➕ Add a channel',
    remove_channel='🗑 Remove',
    post_on_channel='✍️ Write a post',
    channels_str_1='Here you can add and manage your groups and channels connected to this chatbot',
    channels_str_2='Choose a channel',
    channels_menu="What do you wan to do with your channel?",
    no_channels='You have no channel configured yet. Click "➕Add channel" to configure your first channel',
    wrong_channel_link_format='Send me link or username of your channel. \n' \
                              'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
    bot_is_not_admin_of_channel='Bot is not admin in this({}) channel. \n' \
                                'Add bot as admin to the channel and then back to this menu \n' \
                                'and send me link or username of your channel. \n' \
                                'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
    bot_is_not_admin_of_channel_2="Bot is not admin in this({}) channel or can't send message to the channel\n" \
                                  "So channel was deleted. Add bot as admin to the channel, \n" \
                                  "let it send message to the channel "
                                  "and then try again",
    channels_str_4="To add channel u need to add this bot as admin to your channel \n"
                   "and then back to this menu and send \n"
                   "link or username of your channel. \n"
                   "Send me link or username of your channel",
    allow_bot_send_messages='Allow the bot to send messages to the channel. \n'
                            'And than back to this menu and send username of channel',
    no_such_channel='There are no such channel. ',
    choose_channel_to_remove='Choose channel to 🗑 remove',
    channel_has_been_removed='Channel({}) has been deleted.',
    channel_added_success='Now send posts to the channel({}) using this commands.',
    choose_channel_to_post='Choose channel u want to post',
    post_message='Choose an action',
    send_post="What do you want to post on your channel({})?\n" \
              "We will forward your message to channel.",
    choose_channel_to_send_poll='Choose channel u want to send poll',
    choose_channel_to_send_survey='Choose channel u want to send survey',
    try_to_add_already_exist_channel='This channel already exists',

    users_module="👤 Users",
    users_module_help="Your bots users",
    show_user_categories_button="User categories",
    send_user_category_question_button="Ask users",
    add_user_category="Add category",
    send_user_category_16="You can add a new category of the users or return to menu",
    send_user_category_14="What category do you want to create?",
    send_user_category_15="Great! Now you can ask your users if they belong to the categories mentioned above!",
    send_user_category_17="User category has been deleted",
    send_category_question_3="What category do you associate with?",
    send_category_question_4="The category question has been sent to your users",
    send_category_question_5="You have no user categories created. \n"
                             "Please return to the user menu and create a category to assign your users to",
    users_help_admin="You can ask your users what category they belong to or create a new category",
    user_chooses_category="Thank you for your vote!",

    user_mode_help_admin="""
Press “Accept" to turn on the bot in the user mode. 
Press “Back" to return to the normal mode 
""",
    user_mode_on_finish="✅ Ready, now look at the bot in user mode",
    user_mode_off_finish="🔚 User mode is off",

    user_mode_str="Accept",
    user_mode_module="🕶️User view",
    send_a_post_to_channel='Write a post on the channel',

    promotion_send_message_module_str="✉️ Messages ",
    promotion_send_message_button_1="📤✉️ Send message",
    promotion_send_message_button_2="📥 Mailbox",
    promotion_send_message_1="✉️ Send message",
    promotion_send_message_2="Thanks, the homing pigeon's on its way. 🕊!",
    promotion_send_message_3="Write a message to users\n"
                             "You can send as well files of all kinds, video or audio messages",
    promotion_send_message_4="Write a new message and press '✅ Done",
    promotion_send_message_5="✅The message is sent",
    promotion_send_message_6="Forever alone 😉 ",

    promotion_send_message_admin="""
Messages
Send messages to users and get feedback
""",
    promotion_send_message_user="""
Write your message. I’ll read it.
""",
    delete_content="This content has been deleted from the button.",
    delete_button_str="🗑 Delete",
    delete_poll_button_str="🗑 Delete poll",
    delete_survey_button_str="🗑 Delete survey",
    delete_button_str_all="🗑 Delete all messages",
    delete_button_str_last_week="Delete for last week",
    delete_button_str_last_month="Delete for last month",
    view_message_str="Read",
    you_have_a_message_from="You have a message from {}",
    delete_message_str_1="Chosen messages have been deleted",
    send_message_module_str="✉️ Messages",
    send_message_button_1="✉️ Send message to users",
    send_message_button_2="📥 Mailbox",
    send_message_button_3="Message topics",
    send_message_button_4="✉️ Send message to admins",
    send_message_button_5="✉️ Send message to donators",
    send_message_button_6="❌ Blacklist",

    send_message_button_to_admin_anonim="✉️ Send anonymous message",
    send_message_button_to_admin="✉️ Send message",
    send_message_1="✉️ Send message ",
    send_message_to_users_text="✉️ Write a message for your users. You can send any kind of files, \n"
                               "voice and video messages, stickers and links",
    send_message_to_admins_text="✉️ Write a message for all admins of this bot. You can send any kind of files,\n "
                                "voice and video messages, stickers and links",
    send_message_to_donators_text="✉️ Write a message for every who donated money for you.\n"
                                  "You can send any kind of files, "
                                  "voice and video messages, stickers and links",
    send_message_from_user_to_admin_text="✉️ Write us a message.\n"
                                         "You can send any kind of files,\n "
                                         "voice and video messages, stickers and links",
    send_message_from_user_to_admin_anonim_text="✉️ Write us anonymous message.\n"
                                                "You can send any kind of files, "
                                                "voice and video messages, stickers and links. \n"
                                                "No inforpromotion_send_message_button_1mation to you account will be saved to the database",
    send_message_1_1="Choose the category of users to whom you want o send your message",

    send_message_12="What do you want to tell us about?",

    send_message_13="Choose a topic for you message",

    send_message_131="Write the subject of your message",
    block_button_str="Block user",
    # send_message_14="TEST",
    #
    # send_message_15="TEST",
    #
    # send_message_16="TEST",
    #
    # send_message_17="TEST",
    #
    # send_message_18="TEST",
    send_message_anonim="Would you like to send this message anonymously? \n"
                        "If yes, we wan't be able to respond to you",
    send_message_reply="Reply to your message: \n",
    add_message_category="Add topic",
    send_message_2="Thanks, the homing pigeon's on its way. 🕊!",
    send_message_3="Write a message to users\n"
                   "You can send as well files of all kinds, video or audio messages",
    send_message_4="Write a new message and press '✅ Done",
    send_message_5="✅The message is sent",
    send_message_6="Forever alone 😉 You didn't receive any messages yet",
    send_message_7="What do you want to answer to this user?",
    send_message_8="You can delete this message",
    send_message_9="Message has been canceled",
    send_message_answer_user="Dear user, here is the answer to your message",

    send_message_admin="""
Messages
Send messages to users and get feedback. 
You can send any kinds of files, video, audio or media messages.

""",
    send_message_user="""
Say Hello to the admin!
You can send any kinds of files, video, audio or media messages.
""",
    delete_messages_double_check="Are you sure?",
    send_donation_request_1="Tell everyone about the donation and how you will utilize the money\n" \
                            "The 'Donate' button will be attached to the message'",
    send_donation_request_2="Write a new message and press '✅ Done",
    send_donation_request_3="💸 The message is sent!",

    answer_button_str="Answer",
    send_donation_request_button="Send a 'Donate' button to users",
    cancel_button_survey="🔚 Cancel survey",
    donate_button="💸 Donate",
    back_button="🔙 Back",
    cancel_button="🛑 Cancel",
    remove_button="🗑 Remove",
    send_survey_to_channel='Survey to channel',
    send_poll_to_channel='Poll to channel',
    send_post_to_channel='Write a post',
    send_donation_to_channel="Send a 'Donate' button to channel",
    done_button="✅ Done",
    create_button=" 📌 Create",
    delete_button="🗑 Delete a button",
    send_button="📤 Send",
    send_poll_button="📤 Send poll",
    send_survey_button="📤 Send survey",
    results_button="📊 Results",
    menu_button="ℹ️ Menu",

    allow_donations_button=" 💰 Enable donations",
    disable_donations_button=" 💰 Disable donations",
    allow_shop_button=" 💰 Enable shop",
    disable_shop_button=" 💰 Disable shop",
    payment_configs="Configurations",

    payments_config_text_donations_enabled="Donations have been enabled for your users. "
                                           "Enter the configurations to set up a greeting message "
                                           "for those who want to donate for you",
    payments_config_text_donations_disabled="Donations have been disabled on this bot",
    payments_config_text_shop_enabled="A shop has been enabled for your users. "
                                           "Enter the configurations to  add your first product",
    payments_config_text_shop_disabled="The shop has been disabled on this bot",
    payments_config_text="Here you can configure your payments settings",
    change_payment_token="Edit payment token",
    change_donation_greeting="Edit description",
    change_donation_currency="Change currency",
    change_shop_greeting="Edit description",
    change_shop_currency="Change currency",
    configure_button="🛠 Settings",
    ask_donation_button="Ask users for donation",
    title_button="Name",
    description_button="Description",
    currency_button="Currency",
    payment_token_button="Provider token",
    delete_donation_button="🗑 Delete payment config",
    great_text="Well done!",
    create_button_button="📌 Create a button ",
    buttons_button="Buttons",
    edit_button="✏️ Edit the button",
    start_button="🏁 Start",
    main_survey_button="The shop survey",
    back_text="Press '🔙 Back ' to return to the menu ",
    polls_affirmations=[
        "OK",
        "Cool",
        "Great",
        "Perfectly",
        "Okeydokey",
        "Easy-peasy",
        "Yuhu",
        "Yo",
        "Good",
    ],
    polls_str_1='Write your question',
    polls_str_2="Choose poll type",
    polls_str_3="Enter the first answer",
    polls_str_4="Send a next one",
    polls_str_5="Enter the next answer and press'✅ Done'",
    polls_str_6="Oops, too many answers. There is one more option",
    polls_str_7="Thank you! Press '📤 Send' to allow users to take the poll.\n",
    polls_str_8="You haven't done the poll yet. Click 'Create'",
    polls_str_9="List of active polls",
    polls_str_10="Choose a poll to send to users",
    polls_str_11="Damn it, the poll is not sent 🤨 \n You have no users. Share the link of your bot in the social"
                 " networks and  online resource or invite your friends. \nSomebody will come along soon",
    polls_str_12="✅ The poll is sent",
    polls_str_13="Choose a poll to see 📊 the results",
    polls_str_14="🗑 Choose a poll to delete",
    polls_str_15="Press '🔙 Back' to cancel",
    polls_str_16=""" You haven't created a poll yet. \n
Click 'Create' or '🔙 Back'""",
    polls_str_17="🗑 Poll with name {} removed from all chats.",
    polls_str_18="These are the results. ",
    polls_str_18_1="You can create a new poll or return to menu",
    polls_str_19="Nobody voted yet. Let's wait for results",
    polls_str_20="You didn't create any polls yet. Create a new one and send it to your users",

    polls_help_admin="""
Here you can configure and create polls (with predefined choices) or surveys with open answers.

You can send them to your bot users or to your audience in groups and channels

""",
    polls_module_str="Poll",
    ask_for_extra_config="Please enter the text to be displayed above your poll",
    ask_for_extra_config_wrong="Somebody messed up! This poll type is not configured properly.",

    pay_donation_str_admin="""
Payments


""",
    payments_statistics_str="Payments tatistics",
    orders_str="Orders and purchases",
    edit_donation="Edit payment",
    pay_donation_mode_str="💸 Donate ",
    pay_donation_str_1="How much do you want to pay? \n"
                       "Enter the amount of money that you want to donate.\n"
                       "❗️ Cents and pennies separated by floating points, like this'10.50'.",

    pay_donation_str_2="The shop currency of the administrator ❗️ {}",
    allow_donation_text="Press '💰 Create a donation or press '🔙 Back'",
    pay_donation_str_4="Admin has not set up payments yet 🤷‍",
    pay_donation_str_5="Oops, you entered the wrong number. Try again.",

    add_menu_module_button="⚙️ Settings",
    manage_button_str_1="✏️Choose the button you want to edit or press '🔙 Back'",
    manage_button_str_2="Hopla, you haven't made the button yet. Press'📌 Create a button'",
    manage_button_str_3="✏️ Choose the content you want to replace",
    manage_button_str_4="Send a new content",
    manage_button_str_5="✅ Super! Content is updated",
    manage_button_str_6="🛑 You canceled the creation of a button.",

    edit_button_str_1="Enter a new 🤝 greeting for users",
    edit_button_str_2="✅ It's done.!")
ENG.update(
    donations_edit_str_1="Test donation. Ignore it",
    donations_edit_str_2="What to do with the payment? Or press '🔙 Back",
    donations_edit_str_3="Yes, I'm sure.",
    donations_edit_str_4="No, cancel",
    donations_edit_str_5="🗑 Are you sure you want to delete this payment?",
    donations_edit_str_6="What exactly do you want to change? Or press '🔙 Back'",
    donations_edit_str_7="Write a new title for the payment. Or press '🔙 Back'",
    donations_edit_str_8="Write a small description. It will be shown to your users when they enter payments",
    donations_edit_str_9=" Choose the shop currency. Or press '🔙 Back'",
    donations_edit_str_10="✅ It’s in the bag!",
    donations_edit_str_11="🗑 The payment is deleted",
    donations_edit_str_12="Enter a new token of your payment system",
    donations_edit_str_13="✅ New token updated!",
    donations_edit_str_14="Wrong token. Check it and send it again.",
    thank_donation="Thank you for donation!",

    survey_str_1="Enter a name for the survey",
    survey_str_2="Write the first question",
    survey_str_3="The question with this name is already.\n" \
                 "Think of another name",
    survey_str_4="Write the next question or  press '✅ Done'",
    survey_str_5="Hi, please take the survey. It won't be long.\n" \
                 "Press '🏁 Start' to begin",
    survey_str_6="Created a survey called: {}\n" \
                 "{}" \
                 "\n Thanks, come again!",
    survey_str_7="This is a list of active surveys:",
    survey_str_8="Choose a survey to check 📊 results",
    survey_str_9=""" You haven't created a survey yet. \n
Press "Create" or '🔙 Back'""",
    survey_str_10='The name of the user: {},\nQuestion: {}\nAnswer :{} \n\n',
    survey_str_11="The data you requested: \n {}",
    survey_str_12="Wait until someone answers. =/",
    survey_str_13="Click '📤 Send' to remind users of the survey",
    survey_str_14="List of surveys:",
    survey_str_15="🗑 Choose a survey to delete ",
    survey_str_16="""You haven't created a survey yet. \n,
Press "Create" or '🔙 Back'""",
    survey_str_17="🗑 Survey called '{}' removed",
    survey_str_18="List of active surveys:",
    survey_str_19="Choose the survey you want to send to users",
    survey_str_20="Hi, please take the survey..\n" \
                  "Press '🏁 Start' to begin ",
    survey_str_21="Damn it, the survey is not sent 🤨 \n you have no users. Share the link of your bot in the social"
                  "networks and  online resource or invite your friends. Somebody will come along soon ",
    survey_str_22="✅ The survey is sent.",
    survey_str_23="""You haven't done the survey yet.\n
Press "Create" or '🔙 Back'""",
    survey_str_24="Survey has been deleted. You can create a new one or return to menu",

    create_donation_str_1="Test donation. Ignore it",
    create_donation_str_2="✏️ Write the name of the donation",
    create_donation_str_3="""To get a token payment system, follow the instructions:
https://telegra.ph/Guide-Connect-donations-07-03
Insert the token: \n""",
    create_donation_str_4="✏️ Write the title of the donation",
    create_donation_str_5="Wrong token. Check it and send again.",
    create_donation_str_6="Tell everyone about the donation and how you will utilize the money",
    create_donation_str_7="Choose the shop currency",
    create_donation_str_8="✅Great! Now you can accept payments from bot users. ❗ ️Users only need a Bank card.\n" \
                          "Don't forget to tell about it.",

    answer_survey_str_1="Please answer the question.\n\n",
    answer_survey_str_2="Question:{}, Answer: {} \n",
    answer_survey_str_3="☺️ Thank you for answering.\n",
    answer_survey_str_4="See you later!",
    survey_help_admin="""
Surveys
""",
    survey_mode_str="❔ Surveys",
    polls_mode_str="❓ Polls",

    edit_button_button="✏️ Edit a button",
    edit_menu_text="🤝 Change the greeting",
    add_menu_buttons_help="""
Here you can configure your payments settings and your shop
""",
    add_menu_buttons_help_visitor="Choose the product that you want to buy",
    add_menu_buttons_str_1="Write the name of the button or choose from the template.",
    add_menu_buttons_str_1_1="Write the name of your new button",
    link_button_str="Button with a link",
    simple_button_str="Button with content",
    choose_button_type_text="Какую кнопку ты хочешь создать для своего меню?\n\n"
                            "Кнопку со ссылкой по которой могут пройти пользователи\n"
                            "или кнопку с контентом который будет появляться в чате при клике?",
    add_menu_buttons_str_2='Send text, picture, document, video or music. ' \
                           '❗️ The text added to the description is not displayed in the button.',
    add_menu_buttons_str_2_link="Send a link for this button. On click, your users will be redirected to this link",
    add_menu_buttons_str_3='A button with this name already exists. Think of another name.',
    add_menu_buttons_str_4="Great! Add something else.\n'\
'or press '✅ Done'",
    add_menu_buttons_str_5='✅Done! The button will be available in the title menu \n {}',
    add_menu_buttons_str_6="🗑 Choose the button to delete ",
    add_menu_buttons_str_7="""Oops. You don't have buttons yet. Click "Create""",
    add_menu_buttons_str_8='🗑 Button {} removed',
    add_menu_buttons_str_9="🛑 You canceled the creation of a button.",
    add_menu_buttons_str_10="You can create a new button or return to menu",
    add_button="Add",
    add_button_content="Or add content to the button",
    my_groups="🛠My Groups",
    groups="Groups",
    add_group='➕ Add a group',
    remove_group='🗑 Remove',
    post_on_group='✍️ Write a post',
    groups_str_1='Groups',
    groups_str_2='Choose a group',
    groups_menu="What do you wan to do with your group?",
    no_groups='You have no group configured yet. Click "➕Add group" to configure your first group',
    wrong_group_link_format='Send me link or username of your group. \n' \
                            'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
    bot_is_not_admin_of_group='Bot is not admin in this({}) group. \n' \
                              'Add bot as admin to the group and then back to this menu \n' \
                              'and send me link or username of your group. \n' \
                              'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
    bot_is_not_admin_of_group_2="Bot is not admin in this({}) group or can't send message to the group\n" \
                                "So group was deleted. Add bot as admin to the group, \n" \
                                "let it send message to the group "
                                "and then try again",
    groups_str_4="To add group u need to add this bot as admin to your group \n"
                 "and then back to this menu and send \n"
                 "link or username of your group. \n"
                 "Send me link or username of your group",
    allow_bot_send_messages='Allow the bot to send messages to the group. \n'
                            'And than back to this menu and send username of group',
    no_such_group='There are no such group. ',
    choose_group_to_remove='Choose group to 🗑 remove',
    group_has_been_removed='Channel({}) has been deleted.',
    group_added_success='Now send posts to the group({}) using this commands.',
    choose_group_to_post='Choose group u want to post',
    post_message='Choose an action',
    send_post="What do you want to post on your group({})?\n" \
              "We will forward your message to group.",
    choose_group_to_send_poll='Choose group u want to send poll',
    choose_group_to_send_survey='Choose group u want to send survey',
    try_to_add_already_exist_group='This group already exists',
    send_survey_to_group='Survey to group',
    send_poll_to_group='Poll to group',
    send_post_to_group='Write a post',
    send_donation_to_group="Send a 'Donate' button to group",
    add_group_str="To add a new group- \n"
                  "1)Add this bot as admin to your group\n"
                  "2)Write /start command to add this group to the chatbot",

    add_product_button="Add product",
    edit_product="Edit product",
    delete_product="Delete product",
    create_product="Create product",
    add_products_str_1="Type the title for your new product",
    add_products_price="Type the price in the following format: 10.50",
    add_products_str_description="Type the products description, pictures and parameters."
                                 " You can add any type of files or text here",
    add_products_str_description_add="Add some more files or text or click DONE",
    add_products_str_title_taken="This title is already taken. Please write another one",
    add_products_str_currency="Now, type your currency",
    add_products_str_correct_format_price="Please type the price in a correct format",
    add_products_str_shipment="Great! Now, choose the type of this product- with shipment or without",
    add_products_str_added="Product with the name {} has been added",

    create_shop_str_1="TEST payment",
    create_shop_str_2="Send me the title of your new shop",
    create_shop_str_3="Send me the payment token from BotFather settings",
    create_shop_str_4="Send me the title of your new shop",
    create_shop_str_5="This token is wrong. Please send a valid payment token",
    create_shop_str_6="Now, send a description of you new shop. You can add any information you want about it.",
    create_shop_str_7="Choose the primary currency of your shop",
    create_shop_str_8="Your new shop has been created. Now your users can see it in their menu",

    thank_purchase="Thank you for your purchase!",
    products_str_choose_the_product_to_del="Choose the product to delete",
    no_products="You have no products in your shop",
    products_deleted_str="Chosen products have been deleted",
    add_products_products_deleted_str="You can add a new item to your shop or return to shop menu",
    payment_configure_button="Configure Payments",
    add_products_str_deleted="Item {} has been deleted from your shop",
    products="Products",
    buy_button="Buy",
    hello_group="Hello group",


    users_menu_str="Здесь вы можете увидеть своих юзеров",
    statistic_btn_str=f"{emoji['bar_chart']} Статистика",
    users_list_btn_str=f"{emoji['book']} Список юзеров",
    admins_btn_str=f"{emoji['bust_in_silhouette']} Администраторы",
    user_temp="{}"
              "\n*Время старта:* `{}`",
    registered_admin_temp="{}"
                          "\n*Email:* {}"
                          "\n*Время старта:* `{}`",
    not_registered_admin_temp="*Email:* {}"
                              "\n_Ещё не зарегестрирован_",
    no_users_str=f"{emoji['disappointed_relieved']} У вас ещё нет юзеров",
    no_admins_str="Вы единственный администратор",
    users_layout_title="*Список ваших юзеров.*"
                       "\n*Всего юзеров:* `{}`",
    admins_layout_title="*Список администраторов.*"
                        "\n*Всего админов:* `{}`",
    current_page="\n*Текущая траница:* `{}`",
    # delete_admin_button_str=f"{emoji['x']} Удалить"
    admin_deleted_blink=f"{emoji['white_check_mark']} Админ Успешно Удалён",
    confirm_delete_admin_str="_Вы уверены что хотите удалть админа?_",
    # resend_password_btn_str="Переотправить пароль"
    add_admin_btn_str=f"{emoji['plus']} Добавить администратора",
    next_email_request="Enter E-Mail addresses of the other admins. "
                       "They'll get a one-time password that they have to send to your bot."
                       "If you are ready — press 'continue' ",
    add_already_exist_admin=f"{emoji['ok_hand']} "
                            "Admin => {} already exist. ",

    wrong_email="Oops. Wrong E-mail. Try again.",
    admins_added_blink=f"{emoji['white_check_mark']} Админы успешно добавлены",
    enter_new_admin_email="Enter E-Mail addresses of the admins. "
                          "They'll get a one-time password that they have to send to your bot."
                          "If you are ready — press 'Add' ",
    donation_statistic_btn_str=f"{emoji['bar_chart']} Donation Statistic",
    donations_history_button="Show History",
    donation_history_title="*Donations history*\n\n",
    donation_statistic_template=f"{emoji['money_with_wings']} *Donates statistic*"
                                "\n\n*For today* "
                                "\n`{today_str}`"
                                "\n_Donates Quantity:_ `{today_count}`"
                                "\n_Collected:_ `{today_amount}`"

                                "\n\n*For week*"
                                "\n*From:* `{week_from}`"
                                "\n*To:* `{today_str}`"
                                "\n_Donates Quantity:_ `{week_count}`"
                                "\n_Collected:_ `{week_amount}`"

                                "\n\n*For month*"
                                "\n*From:* `{month_from}`"
                                "\n*To:* `{today_str}`"
                                "\n_Donates Quantity:_ `{month_count}`"
                                "\n_Collected:_ `{month_amount}`"

                                "\n\n*All time:*"
                                "\n*First donate:*"
                                "\n`{first_donate}`"
                                "\n*Last donate:* "
                                "\n`{last_donate}`"
                                "\n_Donates Quantity:_ `{all_count}`"
                                "\n_Collected:_ `{all_amount}`",
    donation_history_item_temp="{}"
                               "\n*Amount:* `{} {}`"
                               "\n*Date:* `{}`",
    no_donations=f"{emoji['disappointed_relieved']} No donations",
    users_statistic_template=f"{emoji['family_mwgb']} *New Users*"
                             "\n\n*For today* "
                             "\n`{}`"
                             "\n_New subscribers:_ `{}`"

                             "\n\n*For week* "
                             "\n*From:* `{}`"
                             "\n*To:* `{}`"
                             "\n_New subscribers:_ `{}`"

                             "\n\n*For month* "
                             "\n*From:* `{}`"
                             "\n*To:* `{}`"
                             "\n_New subscribers:_ `{}`"

                             "\n\n*For all time*"
                             "\n*First subscriber:*"
                             "\n`{}`"
                             "\n*Last subscriber:* "
                             "\n`{}`"
                             "\n_Total subscribers:_ `{}`",
    donations_count_str=f"{emoji['money_with_wings']} *Донаты Юзера:* "
                            "{}",
    message_temp="<b>User's name:</b> {}, \n\n<b>Time:</b> {}",
    message_count_str="\n_Total messages:_ `{}`",
    channels_statistic_template="<b>Channel:<b>"
)

RUS = dict(
    you_have_been_reg=", ты зарегистрирован как админ бота. \n\n"
                      "Введи одноразовый пароль из письма.",
    no_pass_provided="Ты не ввел пароль. Введи пароль который ты получил в письме или нажми 'Назад'",
    wrong_pass_admin="Неверный пароль Введи пароль который ты получил в письме или нажми 'Назад'",

    yes="ДА",
    no="НЕТ",
    register_str="Пожалуйста введите свой эмайл чтобы зарегестрироваться в качестве админа",
    start_help="Привет! Меня зовут {}. Управляй мной в этом меню. "
               "Подключи свой канал, проводи опросы, принимай сообщения и донаты.\n "
               "Добавь контент в кнопки через «🛠Настройки» \n ",
    my_channels="🛠 Управлять каналом",
    add_channel="➕ Добавить канал",
    remove_channel="🗑Удалить ",
    post_on_channel=" ✍️Сделать пост",
    channels_menu="📱 Каналы",
    channels_str_1='Каналы',
    channels_str_2='Выбери канал:',
    # Нажми "➕ Добавить канал" или "🔙 Назад"
    no_channels='Нажми "➕ Добавить канал", чтобы подключить канал или "🔙 Назад"',
    wrong_channel_link_format='Отправь Ссылку или Юзернейм твоего канала.' \
                              'Например "https://t.me/name" или "t.me/name", или "@name", или просто "name"',
    bot_is_not_admin_of_channel=' Сделай этого бота админом канала ({}) и возвращайся обратно в бот. ' \
                                'Отправь Ссылку или Юзернейм канала. ' \
                                'Например "https://t.me/name" или "t.me/name", или "@name", или просто "name"',
    bot_is_not_admin_of_channel_2="Бот не админ канала ({}) или у него нет прав для отправки сообщений." \
                                  "'Разреши боту отправлять сообщения в канал. "
                                  "Зайди в свой канал и в списке админов нажми на бота." \
                                  "Возвращайся обратно в бот и отправь Cсылку или Юзернейм канала",
    channels_str_4="Чтобы подключить бота к каналу:\n"
                   "• Зайди в настройки канала\n"
                   "• Добавь этого бота в админы каналы\n"
                   "• Вернись обратно и отправь боту ссылку на Канал или его Юзернейм\n",
    allow_bot_send_messages='Разреши боту отправлять сообщения в канал. '
                            'Зайди в свой канал и в списке админов нажми на бота' \
                            'Вернись обратно в бот и отправь Ссылку или Юзернейм канала ',
    no_such_channel='Такого канала нет',
    choose_channel_to_remove='Выбери канал, чтобы 🗑 удалить.',
    channel_has_been_removed='Канал({}) удалён.',
    channel_added_success='✅ Канал({}) усешно добавлен.',
    choose_channel_to_post='Выбери канал, чтобы сделать пост',
    post_message='Выбери действие',
    send_post="Напиши пост для канала({})?\n" \
              "Мы отправим почтового голубя 🕊 ",
    choose_channel_to_send_poll='Выбери канал, чтобы отправить опрос',
    choose_channel_to_send_survey='Выбери канал, чтобы отправить открытый опрос',
    try_to_add_already_exist_channel='✅ Этот канал уже добавлен',

    users_module="👤 👨‍👩‍👧‍👦Юзеры",
    users_module_help="Юзеры бота",
    add_user_category="Добавить группу",
    show_user_categories_button="Группы юзеров",
    send_user_category_question_button="Опросить юзерв",
    send_user_category_16="Добавь новую группу юзеров",
    send_user_category_14="Напиши название группы",
    send_user_category_15="✅ Готово! Вернись в 👨‍👩‍👧‍👦Юзеры\n ."
                          "Нажми «Опросить юзеров», чтобы они добавили себя в группу.",
    send_user_category_17="🗑 Название группы удалено",

    send_category_question_3="Выбери группу. От этого зависит контент,"
                             " которые ты получаешь и в какой почтовый ящик приходят твои сообщения",
    send_category_question_4="✅Опрос отправлен",
    users_help_admin="Добавь группу юзеров чтобы сортировать их сообщения.\n"
                     "Например, ты хочешь продать рекламный пост."
                     " Создай группу юзеров «Реклама» и получай предложения в этот почтовый ящик.",
    user_chooses_category="✅Спасибо",
    user_mode_help_admin="""
Нажми «Подтвердить», чтобы включить бота в режиме юзера.

        Нажми «Назад», чтобы вернутся в нормальный режим
        """,

    user_mode_on_finish="✅ Готово, посмотри на бота глазами юзера",
    user_mode_off_finish="🔚 Режим юзера выключен",
    user_mode_str="Подтвердить",
    user_mode_module="🕶️Режим юзера",
    delete_message_str_1="🗑 Сообщения удалены",
    view_message_str="Прочитать",
    send_message_module_str="✉️ Сообщения",
    send_message_button_1="✉️ Сообщение всем",
    send_message_button_2="📥 Входящие",
    send_message_button_3="Почтовые ящики",
    send_message_button_4="✉️ Сообщение админам",
    send_message_button_5="✉️ Сообщение донарам",
    send_message_button_6="❌ Черный список",
    send_message_button_to_admin_anonim="✉️ Анонимное сообщение",
    send_message_button_to_admin="✉️ Отправить сообщение",
    you_have_a_message_from="Вам пришло сообщение от {}",

    send_message_12="Напиши сообщение. Админ его прочитает",
    send_message_13="Выбери тему сообщения",
    # send_message_14="TEST",
    # send_message_15="TEST",
    # send_message_16="TEST",
    # send_message_17="TEST",
    # send_message_18="TEST",
    add_message_category="Добавить ящик",
    send_message_1="✉️ Сообщение",
    send_message_to_users_text="✉️ Напиши сообщение пользователям. Ты можежшь так же отпралять любые файлы, "
                               "стикеры, голососовые и видео сообщения",
    send_message_to_admins_text="✉️ Напиши сообщение админам этого бота. Ты можежшь так же отпралять любые файлы, "
                                "стикеры, голососовые и видео сообщения",
    send_message_to_donators_text="✉️ Напиши сообщение тем кто задонатил тебе. "
                                  "Отправляй любые файлы, "
                                  "стикеры, голососовые и видео сообщения",
    send_message_from_user_to_admin_anonim_text="✉️ Напиши нам ананомное сообщение. \n"
                                                "Отправляй любые файлы, "
                                                "стикеры, голососовые и видео сообщения. \n"
                                                "Все твой данные будут в полной конфиденциальности."
                                                " Никакие данные о твоем телеграмм аккаунте не будут сохранены",
    send_message_from_user_to_admin_text="✉️ Напиши нам сообщение. \n"
                                         "Отправляй любые файлы, "
                                         "стикеры, голососовые и видео сообщения. ",
    send_message_1_1="Выбери группу юзеров, которая получит это сообщение",
    send_message_2="Спасибо, почтовый голубь в пути 🕊!",
    send_message_3="Напиши сообщение юзерам\n"
                   "Отправляй файлы любого формата, фотографии, голосовое или аудио сообщение",
    send_message_4="Напиши ещё сообщение или нажми '✅ Готово'",
    send_message_5="✅ Спасибо, почтовый голубь в пути 🕊 ",
    send_message_6="😉 Полковнику никто не пишет ",
    send_message_7="Что ты хочешь ответить этому пользователю?",
    send_message_8="Ты можешь удалить это сообщение",
    send_message_9="Сообщение отменено",
    send_message_answer_user="Вам пришел ответ на твое прошлое сообщение",

    send_message_anonim="Хочешь отправить это сообщение аннонимно?\n"
                        "Если ты ответишь да, мы не сможем тебе ответить",
    send_message_admin="""
Сообщения.
Отправляй любые сообщения, файлы, аудио, видео или фотографии.
""",
    send_message_user="""
Напиши сообщение. Я прочту.
Отправляй любые сообщения, файлы, аудио, видео или фотографии.
""",
    send_message_reply="Ответ на ваше сообщение: \n",
    delete_messages_double_check="Ты уверен, что хочешь удалить сообщения?",

    send_donation_request_1="Напиши юзерам куда ты потратишь деньги. ",
    send_donation_request_2="Напиши ещё сообщение или нажми '✅ Готово'",
    send_donation_request_3="💸 Отправлено",
    answer_button_str="Ответить",
    cancel_button_survey="🔚 Отменить опрос",
    cancel_button="🛑 Отменить",
    remove_button="🗑 Удалить",
    send_survey_to_channel='Отправить от. опрос на канал',
    send_poll_to_channel='Отправить опрос на канал',
    send_post_to_channel='Запостить',
    send_donation_to_channel="Напомнить о донатах в канал",
    donate_button='💸 Задонатить',
    back_button="🔙 Назад",
    done_button="✅ Готово",
    create_button="📌 Создать",
    delete_content="🗑Контент удален ",
    delete_button="🗑 Удалить кнопку",
    delete_button_str="🗑 Удалить",
    delete_button_str_all="Удалить все сообщения",
    delete_button_str_last_week="🗑Удалить за последнюю неделю",
    delete_button_str_last_month="🗑Удалить за последний месяц",
    send_button="📤 Отправить",
    results_button="📊 Результаты",
    menu_button="ℹ️ Меню",
    allow_donations_button=" 💰 Создать донат",
    configure_button="🛠 Настройки",
    ask_donation_button="Напомнить о донатах",
    title_button="Название",
    description_button="Описание",
    currency_button="Валюта",
    payment_token_button="Токен оплаты",

    delete_donation_button="🗑 Удалить донат",
    great_text="Отлично!",
    create_button_button="📌 Создать кнопку",
    edit_button="✏️ Редактировать кнопку",
    start_button="🏁 Старт",
    main_survey_button="Основной опрос",
    back_text="Нажми '🔙 Назад ', чтобы вернуться в меню ",
    polls_affirmations=[
        "Норм",
        "Круто",
        "Отлично",
        "Прекрасно",
        "Оки доки"
        "Юхуу",
        "Йоу",
        "Хорошо",
    ],
    ask_for_extra_config="Напиши текст который будет появляться над опросом:",
    ask_for_extra_config_wrong="Кто-то напартачил! Опрос сделан не правильно",

    polls_str_1='Напиши свой вопрос',
    polls_str_2="Выбери тип опроса",
    polls_str_3="Введи первый вариант ответа",
    polls_str_4="Отправь второй ответ",
    polls_str_5="Введи ещё ответ или нажми '✅ Готово'",
    polls_str_6="Упс, слишком много вариантов. Остался последний",
    polls_str_7="Нажми '📤 Отправить', чтобы юзеры прошли опрос.",
    polls_str_8="Нажми '❓ Опросить' или '🔙 Назад'",
    polls_str_9="Список опросов",
    polls_str_10="Выбери опрос, чтобы '📤 отправить'",
    polls_str_11="Блин, опрос не отправлен 🤨\n У тебя ещё нет юзеров.\n"
                 "Вставь ссылку на бота в соц. сетях или пригласи друзей. \n "
                 "Скоро кто-нибудь придёт",
    polls_str_12="✅ Опрос отправлен",
    polls_str_13="Выбери опрос для просмотра 📊 результатов",
    polls_str_14="🗑 Выбери опрос, чтобы удалить",
    polls_str_15="Нажми '🔙 Назад' для отмены",
    polls_str_16="""Нажми '❓ Опросить' или '🔙 Назад'""",
    polls_str_17="Опрос {} удален из всех чатов.",
    polls_str_18="Вот результаты.",
    polls_str_18_1="Проведи новый опрос или вернись в главное меню",
    polls_str_19="Никто не проголосовал. Ждем результатов",
    polls_str_20="У тебя еще нет опросов. Создай новый опрос чтобы отправить его юзерам",
    polls_help_admin="""
Опросы 
""",
    polls_module_str="Опрос",

    pay_donation_str_admin="""
Платежи
""",
    pay_donation_mode_str=" Задонатить",
    pay_donation_str_1="Сколько хочешь задонатить?\n"
                       "❗️ Центы и копейки через запятую.\nВведи сумму:",
    pay_donation_str_2="❗️ Основная валюта админа {}",
    allow_donation_text="""Хопла, ты ещё не создал донат. \n 
       Нажми '💰Создать донат' или нажми '🔙 Назад'""",
    pay_donation_str_4="🤷‍♂️ Админ не настроил платежи.",
    pay_donation_str_5="Упс, ты ввёл неправильное число. Попробуй ещё раз. \n",
    manage_button_str_1="✏️Выбери кнопку, чтобы её отредактировать или нажми '🔙 Назад'",
    manage_button_str_2="Хопла, ты ещё не сделал кнопку. Нажми '📌 Создать кнопку'",
    manage_button_str_3="✏️ Выбери контент чтобы заменить его",
    manage_button_str_4="Отправь новый контент",
    manage_button_str_5="✅ Супер! Контент обновлён",
    manage_button_str_6="🛑 Ты отменил создание кнопки",

    edit_button_str_1="Напиши новое приветствие для юзеров")
RUS.update(

    edit_button_str_2="✅ Дело сделано!",
    edit_donation="Редактировать",

    donations_edit_str_1="Тестовый платёж. Не обращай внимание",
    donations_edit_str_2="Что сделать с платежом? Или нажми '🔙 Назад'",
    donations_edit_str_3="Да, уверен",
    donations_edit_str_4="Нет, отменить",
    donations_edit_str_5="🗑 Уверен, что хочешь удалить возможность донатить?",
    donations_edit_str_6="Что именно ты хочешь изменить? Или нажми '🔙 Назад'",
    donations_edit_str_7="Напиши новое название доната или нажми '🔙 Назад'",
    donations_edit_str_8=" Напиши новое описание доната или нажми '🔙 Назад'",
    donations_edit_str_9=" Выбери новую валюту расчёта или нажми '🔙 Назад'",
    donations_edit_str_10="✅ Дело в шляпе",
    donations_edit_str_11="🗑 Донат удалён.",
    donations_edit_str_12="Введи новый токен твоей платёжной системы",
    donations_edit_str_13="✅ Токен обновлён!",
    donations_edit_str_14="Неверный токен. Проверь его и отправь снова.",
    thank_donation="Спасибо за подержку!",
    send_donation_request_button="Напомнить юзерам о донатах",
    survey_str_1="Назови опрос. Юзеры ответят в развёрнутой форме",
    survey_str_2="Напиши первый вопрос",
    survey_str_3="Вопрос с таким названием уже есть.\n" \
                 "Придумай другое название",
    survey_str_4="Напиши ещё вопрос или нажми '✅ Готово'",
    survey_str_5="Привет, пройди опрос. Это недолго.\n" \
                 "Нажми '🏁 Старт', чтобы начать ",
    survey_str_6="Создан опрос: {}\n" \
                 "{}" \
                 "\n✅Спасибо",
    survey_str_7="Список активных опросов с открытым ответом:",
    survey_str_8="Выбери опрос, чтобы проверить 📊 результаты",
    survey_str_9=""" Ты ещё не создал опрос. \n
Нажми "Создать", или '🔙 Назад'""",
    survey_str_10='Имя юзера: {},\nВопрос: {}\nОтвет :{} \n\n',
    survey_str_11="Данные, которые ты хотел: \n {}",
    survey_str_12="Подожди, пока ещё никто не ответил =/",
    survey_str_13="Нажми '📤 Отправить', чтобы напомнить юзерам об опросе",
    survey_str_14="Список активных опросов с открытым ответом:",
    survey_str_15="🗑 Выбери опрос для удаления ",
    survey_str_16="""Ты ещё не создал опрос. \n
Нажми "❓ Опросить", или '🔙 Назад'""",
    survey_str_17="🗑 Опрос '{}' удалён",
    survey_str_18="Список активных опросов с открытым ответом:",
    survey_str_19="Выбери опрос, чтобы отправить юзерам",
    survey_str_20="Привет, пройди опрос.\n" \
                  "Нажми '🏁 Старт', чтобы начать ",
    survey_str_21="Упс, опрос не отправлен 🤨 \n"
                  "У тебя ещё нет юзеров. Вставь ссылку на бота в соц. сетях или пригласи друзей. \n"
                  "Скоро кто-нибудь придёт 🐣",
    survey_str_22="✅ Опрос отправлен",
    survey_str_23="""Ты ещё не сделал опрос.\n
Нажми "Создать", или '🔙 Назад'""",
    survey_str_24="🗑Опрос удален. Создай новый или перейди в главное меню",
    create_donation_str_1="Тестовый платёж. Не обращай внимание",
    create_donation_str_2="Назови донат",
    create_donation_str_3="""Как получить токен платёжной системы:\n 
https://telegra.ph/Gajd-Podklyuchit-donaty-07-03
После прочтения инструкции, вернись к своему боту и вставь платежный токен.
""",
    create_donation_str_4="Назови донат",
    create_donation_str_5="Неверный токен. Проверь его и отправь снова.",
    create_donation_str_6="Напиши для юзров. На что ты потратишь их донаты?",
    create_donation_str_7="Выбери основную валюту расчёта",
    create_donation_str_8="✅Отлично! Теперь ты можешь принимать платежи от юзеров \n"
                          "❗️Юзерам нужна лишь банковская карта.\n Не забудь рассказать об этом.",

    answer_survey_str_1="Пройди опрос, это недолго .\n",
    answer_survey_str_2="Вопрос:{}, Ответ: {} \n",
    answer_survey_str_3="☺️ Спасибо за ответы!\n",
    answer_survey_str_4="Увидимся!",
    survey_help_admin="""
Опрос с открытым ответом
""",
    create_button_str="📌 Создать",
    survey_mode_str="❔ Открытые опросы",
    add_menu_module_button="🛠 Настройки",
    edit_button_button="✏️ Редактировать кнопку",
    edit_menu_text="🤝 Изменить приветствие",
    add_menu_buttons_help="""
🛠Настройки\n
Нажми "📌 Создать кнопку", чтобы добавить контент
""",
    link_button_str="Кнопка со ссылкой",
    simple_button_str="Кнопка с контентом",
    choose_button_type_text="Какую кнопку ты хочешь создать для своего меню?\n"
                            "Кнопку со ссылкой по которой могут пройти пользователи\n"
                            "или кнопку с контентом который будет появляться в чате клике?",
    add_menu_buttons_str_1="Напиши или выбери название новой кнопки",
    add_menu_buttons_str_1_1="Напиши название новой кнопки",

    add_menu_buttons_str_2='Отправь текст, картинку, документ, видео или музыку. \n '
                           '❗️ Не добавляй описание в всплывающем окне. \n '
                           'Чтобы сделать описание, добавь отдельно картинку и текст.',
    add_menu_buttons_str_2_link="Отправь ссылку по которой пройдут твой пользователи, когда нажмут на эту кнопу",

    add_menu_buttons_str_3="Кнопка с этим названием уже есть.\n"
                           "Придумай что-то другое",
    add_menu_buttons_str_4="Отлично! Добавь что-нибудь ещё.\n или нажми  '✅ Готово' ",
    add_menu_buttons_str_5='✅Сделано! Кнопка {} уже в главном меню',
    add_menu_buttons_str_6="🗑 Выбери кнопку, чтобы удалить ",
    add_menu_buttons_str_7="""Упс. У тебя ещё нет кнопок. Нажми "📌  Создать кнопку""",
    add_menu_buttons_str_8='🗑 Кнопка {} удалена',
    add_menu_buttons_str_9="🛑 Ты отменил создание кнопки",
    add_menu_buttons_str_10="Создай новую кнопку или возвращайся в главное меню",

    add_button="Добавить",
    add_button_content="Или добавить контент в кнопку",
    my_groups="🛠 Управлять группуми",
    add_group="➕ Добавить группу",
    remove_group="🗑Удалить ",
    post_on_group=" ✍️Сделать пост",
    groups_menu="📱 Группы",
    groups_str_1='Группы',
    groups_str_2='Выбери группу:',
    # Нажми "➕ Добавить группу" или "🔙 Назад"
    no_groups='Нажми "➕ Добавить группу", чтобы подключить группу или "🔙 Назад"',
    wrong_group_link_format='Отправь Ссылку или Юзернейм твоей групы.' \
                            'Например "https://t.me/name" или "t.me/name", или "@name", или просто "name"',
    bot_is_not_admin_of_group=' Сделай этого бота админом группуа ({}) и возвращайся обратно в бот. ' \
                              'Отправь Ссылку или Юзернейм группуа. ' \
                              'Например "https://t.me/name" или "t.me/name", или "@name", или просто "name"',
    bot_is_not_admin_of_group_2="Бот не админ группуа ({}) или у него нет прав для отправки сообщений." \
                                "'Разреши боту отправлять сообщения в группу. "
                                "Зайди в свой группу и в списке админов нажми на бота." \
                                "Возвращайся обратно в бот и отправь Cсылку или Юзернейм группуа",
    groups_str_4="Чтобы подключить бота к группуу:\n"
                 "• Зайди в настройки группуа\n"
                 "• Добавь этого бота в админы группуы\n"
                 "• Вернись обратно и отправь боту ссылку на Групп или его Юзернейм\n",
    allow_bot_send_messages='Разреши боту отправлять сообщения в группу. '
                            'Зайди в свой группу и в списке админов нажми на бота' \
                            'Вернись обратно в бот и отправь Ссылку или Юзернейм группуа ',
    no_such_group='Такого группуа нет',
    choose_group_to_remove='Выбери группу, чтобы 🗑 удалить.',
    group_has_been_removed='Группа({}) удалён.',
    group_added_success='✅ Группа({}) усешно добавлен.',
    choose_group_to_post='Выбери группу, чтобы сделать пост',
    post_message='Выбери действие',
    send_post="Напиши пост для группуа({})?\n" \
              "Мы отправим почтового голубя 🕊 ",
    choose_group_to_send_poll='Выбери группу, чтобы отправить опрос',
    choose_group_to_send_survey='Выбери группу, чтобы отправить открытый опрос',
    try_to_add_already_exist_group='✅ Эта группа уже добавлена',
    send_survey_to_channel='Отправить от. опрос в группу',
    send_poll_to_channel='Отправить опрос в группу',
    send_post_to_channel='Запостить',
    send_donation_to_channel="Напомнить о донатах в группу",

    add_product_button="Add product",
    edit_product="Edit product",
    delete_product="Delete product",
    create_product="Create product",
    add_products_str_1="add_products_str_1",
    add_products_str_2="add_products_str_2",
    add_products_str_3="add_products_str_3",
    add_products_str_4="add_products_str_4",
    add_products_str_5="add_products_str_5",
    add_products_str_6="add_products_str_6",
    add_products_str_7="add_products_str_7",


    #SHOP
    # MAIN MENU
    shop_admin_start_message="👋 Добро пожаловать в админку",
    shop_admin_add_product_btn=f"{emoji['plus']} Добавить товар",
    # delete_product_btn="➖ Удалить товар",
    shop_admin_orders_btn="📩 Заказы",
    # add_brand_btn="👚 Добавить бренд",
    shop_admin_brands_btn=f"{emoji['shirt']} Бренды",
    # add_category_btn="👜 Добавить категорию",
    shop_admin_products_btn="🗳 Товары",
    shop_admin_trash_btn="🗑 Корзина",
    shop_admin_manage_admins_btn=f"{emoji['gear']} Управлять админам",
    # ADDING PRODUCT
    shop_admin_adding_product_start="Отправьте изображение товара",
    shop_admin_send_more_photo="Отправь ещe изображение или продолжай"
                               "\nДобавлено {} файлов",
    shop_admin_continue_btn=f"Продолжить {emoji['arrow_right']}",
    shop_admin_set_brand="Выберите бренд товара",
    shop_admin_set_category="Выберете категерию товара",
    shop_admin_set_price=f"{emoji['money_with_wings']} *Укажите цену товара*",
    shop_admin_price_is_not_int="Цена должна быть целым числом."
                                "\nПришлите цену товара",
    shop_admin_set_description="\n_Напишите описание товара_",
    shop_admin_confirm_add_product="Добавить товар в магазин?",
    shop_admin_adding_product_finished="🤘 Товар успешно добавлен",

    # ORDERS HANDLER
    shop_admin_no_orders="Ещё нет ни одного заказа",
    shop_admin_orders_title="*Список заказов*"
                            "\n_Количество заказов:_ `{}`"
    f"\n{emoji['white_check_mark']} - "
    f"_Отметить заказ как выполненный. "
                            "Товар с заказа будет убран с "
                            "магазина и отмечен как проданый_"
    f"\n{emoji['trash']} - _Удалить заказ_"
    f"\n{emoji['x']} - _Отменить выполненный заказ."
    f"Товар с заказа будет возвращён на полки магазина_",
    shop_admin_order_temp="*Id Заказа:* `{}`"
                          "\n*Время:* `{}`"
                          "\n*Статус заказа:* `{}`"
                          "\n\n*Имя:* `{}`"
                          "\n*Номер:* `{}`"
                          "\n*Цена:* `{}`"
                          "\n\n*Товар:\n*"
                          "{}",
    shop_admin_order_status_new="🔴 Новый",
    # order_status_false="♻️️ В процессе",
    shop_admin_order_status_true=f"{emoji['white_check_mark']} Выполненный",
    shop_admin_all_products_exist="👌🏿 Все продукты в наличии",
    shop_admin_some_product_not_exist="📛 Некоторых товаров уже нет в наличии",
    shop_admin_empty_order="⚠️ Пустой заказ",
    # product_status_true="В наличии ✅",
    # product_status_false="Нет в наличии ⛔",
    # to_process_btn="♻",
    shop_admin_to_done_btn=emoji["white_check_mark"],
    shop_admin_to_trash_btn=emoji['trash'],
    shop_admin_cancel_btn=emoji["x"],
    shop_admin_edit_btn=emoji["hammer_and_wrench"],
    # confirm_to_process="*Уверены что хотите поместить данный заказ "
    #                    "в обработку??*"
    #                    "\n_Весь товар с заказа будет убран с магазина и
    #                    будет ожидать своего покупателя."
    #                    "\nВы сможете в дальнейшем отменить данный
    #                    заказ и товар вернёться на полки"
    #                    " интернет магазина_",
    # to_process_yes="♻ В Обратобку",
    shop_admin_confirm_to_done="*Уверены что хотите отметить данный заказ "
                               "как выполненный??*"
                               "\n_Товар с заказа будет убран с магазина "
                               "и отмечен как проданный."
                               "\nВы сможете в дальнейшем отменить данный заказ "
                               "и товар вернёться на полки"
                               " интернет магазина_",
    shop_admin_to_done_yes=f"{emoji['white_check_mark']} В Выполненные",
    shop_admin_confirm_to_trash_new="*Уверены что хотите удалить данный заказ??*"
                                    "\n_Данный заказ является новым и не обработаным."
                                    "\nУдаление данного заказа "
                                    "не влечёт никаких изменений."
                                    "\nУбедитесь что клиент точно отказался от покупки_",
    # confirm_to_trash_process="*Уверены что хотите отменить данный заказ??*"
    #                      "\n_Данный заказ находится в обработке."
    #                      "\nВесь товар будет возвращён
    #                      на полки интернет магазина."
    #                      "\nУбедитесь что клиент точно
    #                      отказался от покупки_",
    # confirm_to_trash_done="*Уверены что хотите отменить данный заказ??*"
    #                       "\n_Данный заказ находится в выполненых."
    #                       "\nВесь товар будет возвращён
    #                       на полки интернет магазина.",
    shop_admin_to_trash_yes="🗑 В Корзину",
    shop_admin_confirm_cancel="*Уверены что хотите отменить данный заказ??*"
                              "\n_Данный заказ является выполненным."
                              "\nОтмена данного заказа вернёт товар на "
                              "полки магазина и переместит заказ в Новые."
                              "\nУбедитесь что клиент точно отказался от покупки_",
    shop_admin_cancel_yes=f"{emoji['x']} Отменить",
    shop_admin_edit_menu="*Заказ не может быть завершён пока в "
                         "нём присутствуют проданные товары.*"
    f"\n{emoji['x']} - _Убрать товар из заказа_",
    # EDIT ORDER
    shop_admin_choose_products_title="*Выбирите товар для добавления в заказ*"
                                     "\n_Количество товаров:_ `{}`",

    # PRODUCTS HANDLER
    shop_admin_no_products="В магазине ещё нет товаров",
    shop_admin_products_title="*Список товаров*"
                              "\n_Количество товаров:_ `{}`",
    shop_admin_product_template="*Артикул Товара:* `{}`"
                                "\n*Наличие:* `{}`"
                                "\n*Бренд:* `{}`"
                                "\n*Категория:* `{}`"
                                "\n*Цена:* `{}`"
                                "\n*Размеры*: \n{}",
    shop_admin_full_product_template="*Артикул Товара:* `{}`"
                                     "\n*Наличие:* `{}`"
                                     "\n*Имя*: `{}`"
                                     "\n*Бренд:* `{}`"
                                     "\n*Категория:* `{}`"
                                     "\n*Описание*: `{}`"
                                     "\n*Цена:* `{}`"
                                     "\n*Скидочная цена:* `{}`"
                                     "\n*Размеры*: \n{}",
    shop_admin_product_temp_for_order_item="*Артикул Товара:* `{}`"
                                           "\n*На складе:*\n `{}`"
                                           "\n*Бренд:* `{}`"
                                           "\n*Категория:* `{}`"
                                           "\n*Цена:* `{}`"
                                           "\n*Размер*: \n{}",
    shop_admin_confirm_to_trash_product="*Уверены что хотите удалить данный товар??*"
                                        "\n_С данным товаром отсутсвуют заказы._",
    # EDIT PRODUCT
    shop_admin_edit_product_menu="\n_Тут можно редактировать товар_",
    shop_admin_set_discount_btn=f"{emoji['gift_heart']} Скидка",
    shop_admin_set_price_btn=f"{emoji['money_with_wings']} Цена",
    shop_admin_set_description_btn=f"{emoji['page_with_curl']} Описание",
    shop_admin_set_name_btn=f"{emoji['ticket']} Имя",

    shop_admin_change_name="*Введите новое имя для товара*",
    shop_admin_name_length_error="*В имени должно быть не больше 1000 символов в длину*",
    shop_admin_description_below=f"Описание ниже {emoji['arrow_down']}",
    shop_admin_set_discount_price=f"{emoji['gift_heart']} "
    f"*Укажите скидочную цену для товара*",
    shop_admin_sizes_menu_btn=f"{emoji['ballot_box']} Размеры",
    shop_admin_add_size_btn=f"{emoji['plus']} Добавить размер",
    shop_admin_set_new_sizes="\n*Укажите новые размеры*",
    # BRANDS
    shop_admin_brands_title="*Список брендов*"
                            "\n_Количество брендов:_ `{}`",
    shop_admin_no_brands="_Пакажи мнэ брэнд, ааааа хачу_",
    shop_admin_edit_brand_menu="\n_Тут можно редактировать бренд_",
    shop_admin_brand_template="*Имя:* `{}`"
                              "\n*Цена:* `{}`",
    shop_admin_set_brand_price=f"{emoji['money_with_wings']} "
    f"*Укажите цену за кг бренда*",

    # TRASH
    shop_admin_trash_start=f"{emoji['trash']} *Тут хранятся удалённые вещи*",
    shop_admin_trash_orders_title=f"{emoji['trash']} *Список удалённых заказов*"
    "\n_Количество заказов:_ `{}`",
    shop_admin_restore_btn=f"{emoji['recycle']} Восстановить",

    # BLINKS
    # moved_to_process_blink="♻ Заказ успешно помещён в обработку",
    shop_admin_moved_to_done_blink=f"{emoji['white_check_mark']} "
    f"Заказ успешно помещён в выполненные",
    shop_admin_moved_to_trash_blink="🗑 Заказ успешно помещён в корзину",
    shop_admin_order_canceled_blink=f"{emoji['x']} Заказ успешно отменён",
    shop_admin_item_removed_blink="Товар успешно удалён из заказа",
    shop_admin_item_added_blink=f"{emoji['white_check_mark']} "
    f"Товар успешно добавлен в заказ",
    shop_admin_order_restored_blink=f"{emoji['recycle']} Заказ восстановлён",
    shop_admin_product_restored_blink=f"{emoji['white_check_mark']} "
    f"Товар снова в продаже",
    shop_admin_size_removed_blink="Размер удалён",
    shop_admin_sizes_added_blink=f"{emoji['white_check_mark']} "
    f"Размеры успешно добавлены",
    # description_changed_blink=f"{emoji['white_check_mark']} "
    #                            "Описание успешно изменено",
    # EXCEPTIONS
    shop_admin_api_off=f"{emoji['confused']} Апи сейчас не работает - "
    f"обратитесь в поддержку",
    shop_admin_exception_in_adding_product=f"{emoji['confused']} "
    f"Обнаружен сбой при обработке изображения. "
    f"Обратитесь к Юре",
    shop_admin_image_exception=f"{emoji['confused']} "
    f"Не удалось отправить изображение товара."
    "\n_Проверьте товар в магазине по артикулу_",
    shop_admin_image_brand_exception=f"{emoji['confused']} "
    f"Не удалось отправить лого бренда."
    "\n_Проверьте лого бренда в магазине_",
    shop_admin_something_gone_wrong=f"{emoji['confused']} Видимо что-то пошло не так."
    "\nОбратитесь в поддержку",
    shop_admin_timed_out=f"{emoji['confused']} Превышено время ожидания",
    shop_admin_try_later="\nПопробуйте начать позже -> /start",
    # PAGINATION
    shop_admin_current_page="*Текущая траница:* `{}`",
    # BACK BUTTON
    shop_admin_back_btn="🔙 Назад",
    create_shop_str_3="Пришлите токен оплаты из настроек бота в BotFather",

    create_shop_str_1="TEST payment",
    create_shop_str_2="Send me the title of your new shop",
    create_shop_str_4="Send me the title of your new shop",
    create_shop_str_5="This token is wrong. Please send a valid payment token",
    create_shop_str_6="Now, send a description of you new shop. You can add any information you want about it.",
    create_shop_str_7="Choose the primary currency of your shop",
    create_shop_str_8="Your new shop has been created. Now your users can see it in their menu",

    channels="Channels",
    groups="Groups",
    payment_configure_button="Configure Payments",
    buttons_button="Buttons",
    polls_mode_str="❓ Polls",
    messages="✉️ Messages ",
    donations="Donations",
    shop="Shop",
    payments_config_text="Here you can configure your payments settings",
    block_button_str="Block user",

    users_menu_str="Здесь вы можете увидеть своих юзеров",
    statistic_btn_str=f"{emoji['bar_chart']} Статистика",
    users_list_btn_str=f"{emoji['book']} Список юзеров",
    admins_btn_str=f"{emoji['bust_in_silhouette']} Администраторы",
    user_temp="{}"
              "\n*Время старта:* `{}`",
    registered_admin_temp="{}"
                          "\n*Email:* {}"
                          "\n*Время старта:* `{}`",
    not_registered_admin_temp="*Email:* {}"
                              "\n_Ещё не зарегестрирован_",
    no_users_str=f"{emoji['disappointed_relieved']} У вас ещё нет юзеров",
    no_admins_str="Вы единственный администратор",
    users_layout_title="*Список ваших юзеров.*"
                       "\n*Всего юзеров:* `{}`",
    admins_layout_title="*Список администраторов.*"
                        "\n*Всего админов:* `{}`",
    current_page="\n*Current page:* `{}`",
    # delete_admin_button_str=f"{emoji['x']} Удалить"
    admin_deleted_blink=f"{emoji['white_check_mark']} Админ Успешно Удалён",
    confirm_delete_admin_str="_Вы уверены что хотите удалть админа?_",
    # resend_password_btn_str="Переотправить пароль"
    add_admin_btn_str=f"{emoji['plus']} Добавить администратора",
    next_email_request="Раздельными сообщениями отправь почту других админов. "
                       "\nОни получат одноразовый пароль для авторизации. "
                       "\nНажми `Добавить`, когда всех укажешь.\n",
    add_already_exist_admin=f"{emoji['ok_hand']} "
                            "Админ {} уже добавлен. ",
    wrong_email="Упс. Неверный E-mail. Попробуй ввести снова.",
    admins_added_blink=f"{emoji['white_check_mark']} Админы успешно добавлены",
    enter_new_admin_email="Раздельными сообщениями напиши почту новых админов."
                          "\nОни получат одноразовый пароль для авторизации.",
    donation_statistic_btn_str=f"{emoji['bar_chart']} Donation Statistic",
    donations_history_button="Show History",
    donation_history_title="*Donations history*\n\n",
    donation_statistic_template=f"{emoji['money_with_wings']} *Donates statistic*"
                                "\n\n*For today* "
                                "\n`{today_str}`"
                                "\n_Donates Quantity:_ `{today_count}`"
                                "\n_Collected:_ `{today_amount}`"
                                
                                "\n\n*For week*"
                                "\n*From:* `{week_from}`"
                                "\n*To:* `{today_str}`"
                                "\n_Donates Quantity:_ `{week_count}`"
                                "\n_Collected:_ `{week_amount}`"
                                
                                "\n\n*For month*"
                                "\n*From:* `{month_from}`"
                                "\n*To:* `{today_str}`"
                                "\n_Donates Quantity:_ `{month_count}`"
                                "\n_Collected:_ `{month_amount}`"
                                
                                "\n\n*All time:*"
                                "\n*First donate:*"
                                "\n`{first_donate}`"
                                "\n*Last donate:* "
                                "\n`{last_donate}`"
                                "\n_Donates Quantity:_ `{all_count}`"
                                "\n_Collected:_ `{all_amount}`",
    donation_history_item_temp="{}"
                               "\n*Amount:* `{} {}`"
                               "\n*Date:* `{}`",
    no_donations=f"{emoji['disappointed_relieved']} No donations",
    users_statistic_template=f"{emoji['family_mwgb']} *New Users*"
                             "\n\n*For today* "
                             "\n`{}`"
                             "\n_New subscribers:_ `{}`"

                             "\n\n*For week* "
                             "\n*From:* `{}`"
                             "\n*To:* `{}`"
                             "\n_New subscribers:_ `{}`"

                             "\n\n*For month* "
                             "\n*From:* `{}`"
                             "\n*To:* `{}`"
                             "\n_New subscribers:_ `{}`"

                             "\n\n*For all time*"
                             "\n*First subscriber:*"
                             "\n`{}`"
                             "\n*Last subscriber:* "
                             "\n`{}`"
                             "\n_Total subscribers:_ `{}`",
    donations_count_str=f"{emoji['money_with_wings']} *Донаты Юзера:* "
                        "{}",
    message_temp="<b>User's name:</b> {}, \n\n<b>Time:</b> {}",
    message_count_str="\n*Всего сообщений:* `{}`"
)

string_dict_dict = {"ENG": ENG,
                    "RUS": RUS}


