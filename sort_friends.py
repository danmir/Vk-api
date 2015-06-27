import logging
from vk_api import VKapi
from collections import OrderedDict
from operator import itemgetter

logging.basicConfig(level=logging.WARNING)


class SortFriends:

    def __init__(self):
        self.app_id = "???"
        self.app_scope = ["friends"]

    def raiting_func(self, adict):
        likes_count = int(adict["photo_likes"])
        num_of_friends = int(adict["num_of_friends"])
        return likes_count + num_of_friends

    def get_data(self, user_id, login, pswd):
        v = VKapi()
        res = v.auth(login, pswd, self.app_id, self.app_scope)
        v.access_token = res["access_token"]
        friends = v.get_friends(user_id)
        friends_count = friends["count"]

        for friend in friends["items"]:
            f_id = v.get_user(friend["id"])[0]
            try:
                logging.warning("{} {}".format(f_id["first_name"], f_id["last_name"]))
            except KeyError:
                logging.warning("??? ???")

            logging.debug("f_id {}".format(f_id))
            try:
                f_photo_info = v.get_photo_by_id(f_id["photo_id"])
                f_phtoto_likes = f_photo_info[0]["likes"]["count"]
            except KeyError:
                f_phtoto_likes = 0
            logging.debug("f_phtoto_likes {}".format(f_phtoto_likes))

            friend["photo_likes"] = f_phtoto_likes

            try:
                friends_of_f = v.get_friends(f_id["id"])
                friends_of_f_count = friends_of_f["count"]
            except KeyError:
                # User was deleted or smth. so no friends avaliable
                # print(friends_of_f)
                friends_of_f_count = 0
            logging.debug("friends_of_f_count {}".format(friends_of_f_count))
            friend["num_of_friends"] = friends_of_f_count

        logging.debug(friends)
        return friends

    def sort_data(self, friends):
        friends = friends["items"]
        logging.debug(friends)
        s_friends = sorted(friends, key=self.raiting_func, reverse=True)
        logging.debug(s_friends)
        return s_friends

if __name__ == '__main__':
    s = SortFriends()
    user_id = "???"
    user = "???"
    password = "???"
    friends = s.get_data(user_id, user, password)
    s.sort_data(friends)
