import itertools
import requests
import time
import json
from tqdm import tqdm
import os
from dotenv import load_dotenv
import vk
import yadisk
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def check_id(owner_id):
    api = vk.API(access_token=os.environ.get("token_vk"), v='5.131')
    t = api.users.get(user_ids=owner_id)
    if t == []:
        print('Введен неверный идентификатор ВК пользователя')
        exit()
    else:
        owner_id = t[0]['id']
    return owner_id

def check_token(token_ya):
    y = yadisk.YaDisk(token=token_ya)
    if y.check_token() == False:
        print('Введенный токен Яндекс Диска не валиден')
        exit()

def create_folder(folder_path, token_ya):
    host = 'https://cloud-api.yandex.net/v1/disk/resources/'
    params = {'path': folder_path}
    headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token_ya}'}
    response = requests.put(host, headers=headers, params=params)
    if response.status_code == 201:
        print("Папка создана")
    elif response.status_code == 409:
        print("Папка c таким названием существует")

def get_profile_photo(owner_id):
    owner_id = check_id(owner_id)
    VK_URL = 'https://api.vk.com/method/photos.get'
    params = {
    'owner_id': owner_id,
    'access_token': os.environ.get("token_vk"),
    'v':'5.131',
    'album_id': 'profile',
    'extended': 1
    }

    profile_photo_dict= requests.get(VK_URL, params).json()['response']['items']

    return profile_photo_dict

def profile_photo_sorted(owner_id):
    profile_photo_collection = {}
    for item in get_profile_photo(owner_id):
        sorted_item = sorted(item['sizes'], key=lambda x: (x['height'], x['width']))[-1]
        photo_url = sorted_item['url']
        photo_size_type = sorted_item['type']
        photo_name = item['likes']['count']
        if photo_name in dict.keys(profile_photo_collection):
            photo_name = photo_name + item['date']
        profile_photo_collection[photo_name] = {'url':photo_url, 'size':photo_size_type}
    return profile_photo_collection

def upload_photo(token_ya, photo_dict_):
    check_token(token_ya)
    folder_path = 'photo_vk_profile'
    create_folder(folder_path, token_ya)
    host = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'
    data = []
    for photo in tqdm(itertools.islice(photo_dict_, 0, 5)):
        params = {'path': f'/photo_vk_profile/{photo}', 'url': photo_dict_[photo]['url']}
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token_ya}'}
        requests.post(host, headers=headers, params=params)
        d = {"file_name": f'{photo}.jpg', "size": photo_dict_[photo]['size']}
        data.append(d)
        time.sleep(0.2)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    return


if __name__ == '__main__':
    owner_id = input('Введите идентификатор ВК пользователя:')
    photo_list_ = profile_photo_sorted(owner_id)
    token_ya = input('Введите token вашего Яндекс Диска:')
    upload_photo(token_ya, photo_list_)
