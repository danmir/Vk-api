from sort_friends import SortFriends
import argparse
import sys
import logging

# logging.basicConfig(level=logging.DEBUG)


class CLI():

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='Sort friends in vk.com', description="Sort all friends on vk.com by popularity")
        parser.add_argument(
            "--password", "-p", type=str, help="Password", required=True)
        parser.add_argument(
            "--login", "-l", type=str, help="Login", required=True)
        parser.add_argument(
            "--id", "-i", type=str, help="vk id Ex:10624879", required=True)
        self.parser = parser

    def get_frinds(self, namespace):
        print("Рейтинг друзей по сумме количества лайков за аватарку и количеству друзей")
        print("Время выполнеия зависит от количества друзей")
        print("Еще можно слать не более 3-х запросов в секунду к api")

        s = SortFriends()
        user_id = namespace.id
        user = namespace.login
        password = namespace.password
        friends = s.get_data(user_id, user, password)
        res = s.sort_data(friends)

        for friend, count in zip(res, list(range(1, friends["count"] + 1))):
            print(count, " ", friend["first_name"], " ", friend["last_name"])
            print("Лайков: {} Друзей: {}".format(
                friend["photo_likes"], friend["num_of_friends"]))


if __name__ == '__main__':
    i_interface = CLI()
    parser = i_interface.parser
    namespace = parser.parse_args(sys.argv[1:])
    i_interface.get_frinds(namespace)
