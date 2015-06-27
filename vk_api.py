from http.cookiejar import CookieJar
import urllib
from urllib.request import urlopen
import urllib.parse
from form_parser import FormParser
import requests
import logging
import json
import http.cookiejar
from time import sleep

# logging.basicConfig(level=logging.DEBUG)


class VKapi():
    def __init__(self):
        self.method_call_template = "https://api.vk.com/method/{}"
        self.access_token = None

    def auth(self, email, password, app_id, scope):
        """
        Auth method that contains two part:
        1) enter login and password via oauth2 (_auth_user)
        2) garant access to requested scopes (_give_access)
        Input:
        @email    -- email or mob/phone
        @password --  your vk pass
        @app_id   -- yours app id
        @scpoe    -- list of scpoes to get accsess to
                     For ex.: [friends, offline]

        Return:
        dict with access_token, user_id, expires_in
        """

        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                             urllib.request.HTTPRedirectHandler())


        # Authorizate user
        html, url = self._auth_user(email, password, app_id, scope, opener)
        logging.debug(html, url)

        # If application was not already authorized
        if urllib.parse.urlparse(url).path != "/blank.html":
            # Need to give access to requested scope
            url = self._give_access(html, opener)

        # If not success even after giving access -> error
        if urllib.parse.urlparse(url).path != "/blank.html":
            raise RuntimeError(
                '''Bad responce from oauth server.
                An error occured while obtaining access_token
                Check your login and password''')

        # Split query parameters to key, value pairs
        def split_key_value(kv_pair):
            """
            Split string by "=" in pairs
            """
            kv = kv_pair.split("=")
            return kv[0], kv[1]

        answer = dict(split_key_value(kv_pair)
                      for kv_pair in urllib.parse.urlparse(url).fragment.split("&"))
        if "access_token" not in answer or "user_id" not in answer \
                or "expires_in" not in answer:
            raise RuntimeError(
                "Missing access token or users id values in answer.")

        return {"access_token": answer["access_token"],
                "user_id": answer["user_id"],
                "expires_in": answer["expires_in"]}

    def _auth_user(self, email, password, client_id, scope, opener):
        """
        Additional method for initial auth
        """
        response = opener.open(
            "https://oauth.vk.com/oauth/authorize?" +
            "redirect_uri=https://oauth.vk.com/blank.html&" +
            "response_type=token&" +
            "client_id={}&scope={}&display=mobile".format(client_id, ",".join(scope)))

        html = response.read().decode("utf-8")

        # Parse user authorization form
        parser = FormParser()
        parser.feed(html)
        parser.close()

        if not parser.form_parsed or parser.url is None \
                or "pass" not in parser.params or "email" not in parser.params:
            raise RuntimeError(
                "Something wrong with page. Unable parse VK authorization form")
        # Set forms parameters, need to be filled by user
        parser.params["email"] = email
        parser.params["pass"] = password

        # logging.debug(parser.method)
        # logging.debug(parser.params)
        # logging.debug(parser.url)
        r = opener.open(
            parser.url, urllib.parse.urlencode(parser.params).encode("utf-8"))

        return r.read(), r.geturl()

    def _give_access(self, html, opener):
        """
        Garant access to requested scopes
        """
        parser = FormParser()
        parser.feed(html.decode("utf-8"))
        parser.close()

        if not parser.form_parsed or parser.url is None:
            raise RuntimeError(
                "Something wrong with a parser. Unable parse VK application authorization form")

        r = opener.open(
            parser.url, urllib.parse.urlencode(parser.params).encode("utf-8"))

        return r.geturl()

    def call_api(self, method_name, method_params, access_token=None):
        if access_token:
            method_params["access_token"] = access_token
        if self.access_token:
            method_params["access_token"] = self.access_token
        r = requests.get(
            self.method_call_template.format(method_name), params=method_params)
        sleep(0.1)
        return r.json()

    def get_friends(self, user_id, params=None):
        """
        Get list of friends for user
        When user is deleted or deactivated and etc.
        Cause KeyError because there is no field "response"
        """
        if not params:
            params = {}
            params["fields"] = "city,domain"
            params["v"] = "5.33"
            # params["count"] = "10"
        params["user_id"] = user_id
        res_dict = self.call_api(
            "friends.get", params)
        # logging.debug(res_dict)

        res_dict = res_dict["response"]
        logging.debug(res_dict["count"])
        return res_dict

    def get_user(self, user_id, params=None):
        """
        Get ldetailed user info
        No errors handling "https://vk.com/dev/errors"
        Cause KeyError because there is no field "response"
        """
        if not params:
            params = {}
            params["fields"] = "photo_id"
            params["v"] = "5.33"
        params["user_id"] = user_id
        res_dict = self.call_api(
            "users.get", params)
        logging.debug(res_dict["response"])
        return res_dict["response"]

    def get_photo_by_id(self, photo_id, params=None):
        """
        Get info about photo by photo id
        No errors handling "https://vk.com/dev/errors"
        Cause KeyError because there is no field "response"
        """
        if not params:
            params = {}
            params["v"] = "5.33"
            params["extended"] = "1"
        params["photos"] = photo_id
        res_dict = self.call_api(
            "photos.getById", params)
        logging.debug(res_dict["response"][0]["likes"])
        return res_dict["response"]


if __name__ == '__main__':
    app_id = "???"
    user = "???"
    password = "???"
    app_scope = ["friends"]

    v = VKapi()
    # res = v.auth(user, password, app_id, app_scope)
    # print(res)
    v.get_friends("???")
    v.get_user("???")
    v.get_photo_by_id("???")
