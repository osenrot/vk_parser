import sys
import requests
import time
import numpy as np
from config import access_token, user_id, api_version
from tqdm import tqdm


class VkException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class VKUser:
    """
    Находит город, родной город и то же для друзей.
    """

    def __init__(self, access_token, user_id, api_version):
        try:
            self.access_token = access_token
            self.user_id = user_id
            self.api_version = api_version
            self.city, self.home_town, self.deactivated, self.is_closed = self.get_base_info([self.user_id])

            if self.deactivated == '' and self.is_closed == '':
                self.are_friends_accessible, self.friends_info, self.friends_count = self.get_friends_info(self.user_id)
            else:
                self.are_friends_accessible, self.friends_info, self.friends_count = '', '', ''

            self.result = {'user_id': self.user_id,
                           'city': self.city,
                           'home_town': self.home_town,
                           'deactivated': self.deactivated,
                           'is_closed': self.is_closed,
                           'are_friends_accessible': self.are_friends_accessible,
                           'friends_count': self.friends_count,
                           'friends_info': self.friends_info}
        except VkException as error:
            sys.exit(error)

    def make_request_url(self, method_name, parameters, using_access_token=False):
        """https://vk.com/dev/api_requests"""

        req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}'.format(method_name=method_name,
                                                                                          api_v=self.api_version,
                                                                                          parameters=parameters)

        if using_access_token:
            req_url = '{}&access_token={token}'.format(req_url, token=self.access_token)
        return req_url

    def get_base_info(self, user_ids):
        """https://vk.com/dev/users.get"""
        r = requests.get(self.make_request_url('users.get',
                                               'user_ids={}&fields=city,home_town,deactivated,is_closed'.format(','.join(map(str, user_ids))),
                                               True)).json(strict=False)
        if 'error' in r.keys():
            raise VkException('Error message: {} Error code: {}'.format(r['error']['error_msg'],
                                                                        r['error']['error_code']))
        r = r['response'][0]

        return (r.get('city', {'title': ''})['title'],
                r.get('home_town', ''),
                r.get('deactivated', ''),
                r.get('is_closed', ''))

    def get_friends_info(self, user_id):
        """https://vk.com/dev/friends.get
        Принимает идентификатор пользователя
        """
        r = requests.get(self.make_request_url('friends.get',
                                               'user_id={}&fields=uid,city,home_town,deactivated,is_closed'.format(user_id),
                                               True)).json(strict=False)

        if 'error' in r.keys() and r.get('error', {'error_code': None})['error_code'] == 15:
            return False, [], 0
        elif 'error' in r.keys():
            raise VkException('Error message: {} Error code: {}'.format(r['error']['error_msg'],
                                                                        r['error']['error_code']))
        else:
            return (True,
                    [{'city': item.get('city', {'title': ''})['title'],
                      'home_town': item.get('home_town', ''),
                      'deactivated': item.get('deactivated', ''),
                      'is_closed': item.get('is_closed', '')} for item in r['response']['items']],
                    r['response']['count'])


if __name__ == '__main__':
    # chosen_ids = np.random.choice(np.arange(500000000), 100000, replace=False)
    # with open('chosen_ids.txt', 'w') as f:
    #     for id in chosen_ids:
    #         print(id, file=f, sep=',')

    with open('chosen_ids.txt', 'r') as f:
        chosen_ids = []
        for line in f.readlines():
            chosen_ids.append(int(line))

    with open('vk_users_cities_with_friends.txt', 'a') as f:
    #     for id in tqdm(chosen_ids[17791:]):
    #         a = VKUser(access_token, id, api_version)
    #         print(a.result, file=f)
    #         time.sleep(0.6)

        i = 0
        while i <= 100000:
            id = chosen_ids[i]
            print('Trying to get {} user'.format(i))
            try:
                a = VKUser(access_token, id, api_version)
                print(a.result, file=f)
                print('Successful!')
                time.sleep(0.6)
                i += 1
            except Exception as e:
                if e.message == 'Error message: Rate limit reached Error code: 29':
                    print('Rate Exception caught, sleeping for 10 minutes')
                    time.sleep(600)
                    print('Woke up')
                else:
                    raise e

