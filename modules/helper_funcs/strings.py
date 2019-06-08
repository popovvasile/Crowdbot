user_mode_help_admin = """
 Click "ON" to turn on the user view and interact with the chatbot as an non-admin user.
  
 Click "OFF" to return to the normal mode
"""
user_mode_on_finish = "Great! Now you can return to the main menu and"\
                      " you'll see it as non-admin users do (except the 'User view button'."
user_mode_off_finish = "User view is turned off! Now you can use the main menu as admin"
user_mode_str = "User view"

send_message_module_str = "Send a message"
send_message_button_1 = "Send message"
send_message_button_2 = "Inbox messages"
send_message_1 = "What do you want to tell us?"
send_message_2 = "Thank you! Your message has been sent to the chatbot owner!"
send_message_3 = "What do you want to tell your users?\n"\
                         "We will forward your message to all your users."
send_message_4 = "Great! Send me a new message or click 'Done'"
send_message_5 = "Thank you! We've sent your message to your users!"
send_message_6 = "You have no incoming messages yet"
send_message_admin = """
Send a message to your users or check the messages sent by the users to you
"""
send_message_user = """
Here you can send a message to the chatbot owner
"""


send_donation_request_1 = "What do you want to tell your users?\n"\
                           "We will forward your message to all your users,\n" \
                           "together with a 'Donate' button"
send_donation_request_2 = "Great! Send me a new message or click 'Done'"
send_donation_request_3 = "Thank you! We've sent your message to your users!"
send_donation_request = "Send donation request"
cancel_button_survey = "Cancel survey"
donate_button = "Donate"
back_button = "Back"
done_button = "Done"
create_button = "Create"
delete_button = "Delete"
send_button = "Send"
results_button = "Results"
menu_button = "Menu"
allow_donations_button = "Allow donations"
configure_button = "Configure"
ask_donation_button = "Ask users for donation"
title_button = "Title"
description_button = "Description"
currency_button = "Currency"
delete_donation_button = "Delete this donation"
great_text = "Great!"
create_button_button = "Create button"
edit_button = "EDIT"
start_button = "START"
main_survey_button = "MAIN SURVEY"
back_text = "To return to main menu, click 'Back' "
polls_affirmations = [
    "Cool",
    "Nice",
    "Doing great",
    "Awesome",
    "Okey dokey",
    "Neat",
    "Whoo",
    "Wonderful",
    "Splendid",
]
polls_str_1 = 'Hi! Please send me the title of your new poll'
polls_str_2 = "What kind of poll is it going to be?"
polls_str_3 = "Now, send me the first answer option"
polls_str_4 = "Next, please send me the first answer option."
polls_str_5 = "Now, send me another answer option or click DONE to publish."
polls_str_6 = "Uh oh, you're running out of options. You can only have one more option."
polls_str_7 = "Thank you! you can send this poll to your users by clicking 'Send' \n"
polls_str_8 = "You didn't create any polls yet. Please create your first poll"
polls_str_9 = "This is the list of the current polls. "
polls_str_10 = "Choose the poll that you want to send"
polls_str_11 = "Looks like there are yet no users to send this poll to. \n No polls sent :( "
polls_str_12 = "Your poll was sent to all you users! "
polls_str_13 = "Please choose the poll that you want to check"
polls_str_14 = "Please choose the poll that you want to delete"
polls_str_15 = "Click 'Back' if you want to cancel"
polls_str_16 = """You have no polls created yet. \n
Click "Create" to configure your first poll or "Back" for main menu"""
polls_str_17 = "Poll with title {} has been deleted from all chats."
polls_str_18 = """Click "Create" to configure a new poll or "Back" for main menu"""
polls_help_admin = """
Here you can:
 - Create a new poll
 - Delete_poll
 - Send a poll to all users 

"""
polls_module_str = "Polls"

pay_donation_str_admin = """
 Click:
  - Donate - to make a donation for this organization
  - Allow donations - to allow the users of this bot to donate for your organization 
  - Configure - to edit the current donation settings

"""
pay_donation_mode_str = "Donate"
pay_donation_str_1 = "First, tell us how much do you want to donate. Enter a floating point number"
pay_donation_str_2 = "Remember, we use {} as our primary currency"
allow_donation_text = "You didn't set up configurations so far. \n"\
                                 'Press "Allow donations" to configure your first donation option\n'\
                                 'or click "Back" for main menu'
pay_donation_str_4 = "Sorry,you can't donate on this chatbot yet"
pay_donation_str_5 = "You entered a wrong number. Please enter a valid amount of money "

manage_button_str_1 = "Please choose the button that you want to edit (or click /cancel)"
manage_button_str_2 = "You have no custom buttons to edit. Please create a button first"
manage_button_str_3 = "Please choose the part that you want to replace"
manage_button_str_4 = "Send me the new content to update the old one"
manage_button_str_5 = "Great! Your content has been changed!"
manage_button_str_6 = "Button creation was stopped"

edit_button_str_1 = "Please tell me a new text to be displayed above the menu keyboard"
edit_button_str_2 = "Thank you! Your description has been updated!"

donations_edit_str_1 = "Test payment, Please ignore this message"
donations_edit_str_2 = "What do you want to do with this donation? (click /cancel to return)"
donations_edit_str_3 = "Yes, I am sure"
donations_edit_str_4 = "No, let's get back"
donations_edit_str_5 = "Are you sure that you want to delete this donation? "
donations_edit_str_6 = "Please choose what exactly do you want to edit (or click /cancel)"
donations_edit_str_7 = "Now, write a new title for this donation (or click /cancel)"
donations_edit_str_8 = "Now, write a short text for your donation- what your users have to pay for? (or click /cancel)"
donations_edit_str_9 = "Now, choose the currency of your donation (or click /cancel)"
donations_edit_str_10 = "Your donation has been updated"
donations_edit_str_11 = "Your donation has been deleted"
donations_edit_str_12 = "Please enter your new donation provider token"
donations_edit_str_13 = "Thank you! Your provider_token was changed successfully !"
donations_edit_str_14 = "Your provider token is wrong. Please check your provider token and send it again"

survey_str_1 = "Enter a title for your survey"
survey_str_2 = "Type your first question"
survey_str_3 = "You already have a survey with this title.\n"\
                                          "Please type another title for your survey"
survey_str_4 = "Type your next question or click DONE if you are finished"
survey_str_5 = "Dear user, a survey has been sent to you.\n"\
                                          "Please press START to answer to the questions"
survey_str_6 = "Created a survey with title: {}\n"\
                         "{}"\
                         "\nUntil next time!"
survey_str_7 = "This is the list of your current surveys:"
survey_str_8 = "Choose the survey that you want to see"
survey_str_9 = """You have no surveys created yet. \n
Click "Create" to configure your first survey or "Back" for main menu"""
survey_str_10 = 'Users full name: {},\nQuestion: {}\nAnswer :{} \n\n'
survey_str_11 = "Here is your requested data : \n {}"
survey_str_12 = "Your survey doesn't have any answers yet =/"
survey_str_13 = "Send your users a reminder to answer to your questions using the button 'Send'"
survey_str_14 = "This is the list of your current surveys:"
survey_str_15 = "Choose the survey that you want to delete"
survey_str_16 = """You have no surveys created yet. \n
Click "Create" to configure your first survey or "Back" for main menu"""
survey_str_17 = "The survey with the title '{}' has been deleted"
survey_str_18 = "This is the list of your current surveys:"
survey_str_19 = "Choose the survey that you want to send to your users"
survey_str_20 = "Dear user, a survey has been sent to you.\n" \
                "Please press START to answer to the questions"
survey_str_21 = "Looks like there are yet no users to send this survey to. "\
                                      "No surveys sent :( "
survey_str_22 = "Survey sent to all users!"
survey_str_23 = """You have no surveys created yet. \n
Click "Create" to configure your first survey or "Back" for main menu"""

create_donation_str_1 = "Test payment, Please ignore this message"
create_donation_str_2 = "Please enter a title for your donation"
create_donation_str_3 = """Please enter your donation provider token\n 1st Step: Go to @botfather and enter /mybots. 
Choose your bot and press “Payments”. Choose a provider. \nWe advise to use „Stripe“ because of low Acquiring 
comisson for European card. \n2nd Step: Authorize yourself in the chatbot of the chosen provider. Just follow 
instructions then you will get a token-access, that you should copy.\n3nd Step :Go back to your bot and create 
/newdonate. Paste your token, choose the currency, and minimal donation. \n
[Telegram's tutorial](https://core.telegram.org/bots/payments#getting-a-token)"""
create_donation_str_4 = "Enter a title for your donation"
create_donation_str_5 = "Your provider token is wrong. Please check your provider token and send it again"
create_donation_str_6 = "Write a short text for your donation campaign- what your users are donating for?"
create_donation_str_7 = "Now, Choose the currency of your payment"
create_donation_str_8 = "Congratulation! You can get payments from your audience.\n"\
                         "Do not forget to remind them of this."

answer_survey_str_1 = "Please answer the following question.\n\n"
answer_survey_str_2 = "Question:{}, Answer: {} \n"
answer_survey_str_3 = "Thank you for your responses!\n"
answer_survey_str_4 = "Until next time!"
survey_help_admin = """
 Here you can:
 -  Create a survey and ask your users any questions \n
 -  Delete a survey\n
 -  Send an invitation to answer to your survey\n
 -  Check the results of the survey

"""
survey_mode_str = "Surveys"

edit_button_button = "Edit a button"
edit_menu_text = "Edit menu text"
add_menu_buttons_help = """
Here you can:\n
- Create a custom button for your bot that will display images, files, voice, music or text.\n
- Delete an old button\n
- Edit the content of the button
"""
add_menu_buttons_str_1 = "Type a name for new button or choose one of the examples below. "\
                         "Please note that you can't modify the buttons available by default "
add_menu_buttons_str_2 = 'Now, send a text, an image, a video, '\
                                      'a document or a music file to display for your new button'
add_menu_buttons_str_3 = 'You already have a button with the same name. Choose another name'
add_menu_buttons_str_4 = 'Great! You can add one more file or text to display.\n'\
                                  'If you think that this is enough, click DONE'
add_menu_buttons_str_5 = 'Thank you! The button will be accessible by clicking \n {} in menu'
add_menu_buttons_str_6 ="Choose the button that button that you want to delete"
add_menu_buttons_str_7 =  """You have no buttons created yet. Create your first button by clicking "Create" """
add_menu_buttons_str_8 = 'Thank you! We deleted the button {}'
add_menu_buttons_str_9 = "Button creation was stopped"
add_menu_buttons_str_10 = "You can create a new button or return to menu"