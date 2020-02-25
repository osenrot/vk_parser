import sys
import requests
from config import access_token, user_id, api_version


class VkException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class VKUser:
    """
    Находит друзей, находит общих друзей
    """

    def __init__(self, access_token, user_id, api_version):
        try:
            self.access_token = access_token
            self.user_id = user_id
            self.api_version = api_version
            self.city, self.home_town = self.get_base_info([self.user_id])
            self.friends_info, self.friends_count = self.get_friends_info(self.user_id)
        except VkException as error:
            sys.exit(error)

    def make_request_url(self, method_name, parameters, using_access_token=False):
        """read https://vk.com/dev/api_requests"""

        req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}'.format(method_name=method_name,
                                                                                          api_v=self.api_version,
                                                                                          parameters=parameters)

        if using_access_token:
            req_url = '{}&access_token={token}'.format(req_url, token=self.access_token)
        return req_url

    def get_base_info(self, user_ids):
        """read https://vk.com/dev/users.get"""
        r = requests.get(self.make_request_url('users.get',
                                               'user_ids={}&fields=city,home_town'.format(','.join(map(str, user_ids))),
                                               True)).json()
        if 'error' in r.keys():
            raise VkException('Error message: {} Error code: {}'.format(r['error']['error_msg'],
                                                                        r['error']['error_code']))
        r = r['response'][0]
        # Проверяем, если id из settings.py не деактивирован
        if 'deactivated' in r.keys():
            raise VkException("User deactivated")

        return r['city']['title'], r['home_town']

    def get_friends_info(self, user_id):
        """
        read https://vk.com/dev/friends.get
        Принимает идентификатор пользователя
        """
        r = requests.get(self.make_request_url('friends.get',
                                               'user_id={}&fields=uid,city,home_town'.format(user_id),
                                               True)).json()['response']

        # r = list(filter((lambda x: 'deactivated' not in x.keys()), r['items']))

        return {item['id']: (item.get('city', {'title': ''})['title'],
                             item.get('home_town', '')) for item in r['items']}, r['count']


if __name__ == '__main__':
    a = VKUser(access_token, user_id, api_version)
    print(a.user_id)
    print(a.city)
    print(a.home_town)
    print(a.friends_info)
    print(a.friends_count)
