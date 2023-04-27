import requests
import time
import json
from tqdm import tqdm
import os
from dotenv import load_dotenv

from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
token_vk = os.environ.get("token_vk")
#token_ya = os.environ.get("token_ya")


def create_folder(folder_path):
    host = 'https://cloud-api.yandex.net/v1/disk/resources/'
    params = {'path': folder_path}
    headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token_ya}'}
    response = requests.put(host, headers=headers, params=params)
    if response.status_code == 201:
        print("Папка создана")
    elif response.status_code == 409:
        print("Папка c таким названием существует")


def get_profile_photo(token_vk, owner_id):
    VK_URL = 'https://api.vk.com/method/photos.get'
    params = {
    'owner_id': owner_id,
    'access_token': token_vk,
    'v':'5.131',
    'album_id': 'profile',
    'extended': 1
    }

    profile_photo_dict= requests.get(VK_URL, params).json()['response']['items']

    return profile_photo_dict

def profile_photo_sorted(token_vk, owner_id):
    profile_photo_collection = []
    photo_names = []
    for item in get_profile_photo(token_vk, owner_id):
        sorted_item = sorted(item['sizes'], key=lambda x: (x['height'], x['width']))
        photo_url = sorted_item[-1]['url']
        photo_size = sorted_item[-1]['height'] * sorted_item[-1]['width']
        photo_size_type = sorted_item[-1]['type']
        photo_name = item['likes']['count']
        if photo_name in photo_names:
            photo_name = photo_name + item['date']
        photo_names.append(photo_name)
        profile_photo_collection.append([photo_name, photo_url, photo_size_type, photo_size])
    profile_photo_collection.sort(key=lambda x: x[3], reverse=True)
    return profile_photo_collection

def upload_photo(token_ya, photo_list_,qnty_to_load):
    create_folder('/photo_vk_profile')
    host = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'
    data = []
    for photo in tqdm(photo_list_[0:(qnty_to_load)]):
        params = {'path': f'/photo_vk_profile/{photo[0]}', 'url': photo[1]}
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token_ya}'}
        requests.post(host, headers=headers, params=params)
        d = {"file_name": f'{photo[0]}.jpg', "size": photo[2]}
        data.append(d)
        time.sleep(0.2)
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)
    return

if __name__ == '__main__':
    owner_id = input('Введите идентификатор ВК пользователя: ')
    token_ya = input('Введите token вашего Ядекс Диска: ')
    photo_list_ = profile_photo_sorted(token_vk, owner_id)
    data = upload_photo(token_ya, photo_list_, 5)
