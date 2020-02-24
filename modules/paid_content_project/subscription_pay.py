from database import users_table


class MemberChecker():
    def check_subscription_and_kick(self, update, context):
        # context.user_data["subscription"]
        # for user in users_table.find({"bot_id": context.bot.id}):
        #     if user["id"] not in
        #
        # TODO check the members of the group/channel if they paid
        # TODO stop sending them content from bot- remove him from the subsribers list
        pass