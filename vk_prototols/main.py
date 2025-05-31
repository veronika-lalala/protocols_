from datetime import datetime

import requests

USER_ID = "438647624"

def get_friends (token,id=USER_ID):
    try:
        response = requests.get(
            "https://api.vk.com/method/friends.get",
            params={
                "user_id": id,
                "access_token": token,
                "v": "5.199",
                "fields": "first_name,last_name,domain",

            }
        ).json()

        if "response" in response:
            friends = response["response"]["items"]
            print(f"Найдено друзей: {len(friends)}")
            print("--------------------------------")

            for friend in friends:
                name = f"{friend['first_name']} {friend['last_name']}"
                link = f"https://vk.com/{friend.get('domain', 'id' + str(friend['id']))}"
                print(f"{name} | {link}")
        else:
            print("Ошибка:", response.get("error", "Неизвестная ошибка"))

    except Exception as e:
        print("Ошибка запроса:", e)


def get_followers( count, token,user_id=USER_ID):

    try:

        response = requests.get(
            "https://api.vk.com/method/users.getFollowers",
            params={
                "user_id": user_id,
                "access_token": token,
                "v": "5.199",
                "count": count,
                "fields": "first_name,last_name,domain,photo_50"
            },
            timeout=10
        ).json()

        if "response" in response:
            followers = response["response"]["items"]
            print(f"Найдено подписчиков: {len(followers)}")
            print("----------------------------------------")

            for follower in followers:
                name = f"{follower['first_name']} {follower['last_name']}"
                link = f"https://vk.com/{follower.get('domain', 'id' + str(follower['id']))}"
                print(f"{name} | {link}")


        else:
            error_msg = response.get("error", {}).get("error_msg", "Неизвестная ошибка")
            print(f"Ошибка API: {error_msg}")
            return None


    except Exception as e:
        print(f"Ошибка запроса:", e)


def get_subscriptions(count, token, user_id=USER_ID):

    try:

        response = requests.get(
            "https://api.vk.com/method/users.getSubscriptions",
            params={
                "user_id": user_id,
                "access_token": token,
                "v": "5.199",
                "count": count,
                "extended": 1,
                "fields": "description,activity,members_count"
            },
            timeout=10
        ).json()

        if "response" in response:
            items = response["response"]["items"]


            print(f"Подписки пользователя (ID: {user_id})")
            print("=" * 50)
            print(f"Всего подписок: {len(items)}")
            print("=" * 50)

            for sub in items:

                href=""
                if 'screen_name' in sub:
                    href=f"https://vk.com/{sub['screen_name']}"
                print(f"{sub['name']} | {href}")



        else:
            error_msg = response.get("error", {}).get("error_msg", "Неизвестная ошибка")
            print(f"Ошибка: {error_msg}")


    except Exception as e:
        print(f"Ошибка запроса:", e)


def get_photo_albums(count,token, user_id=USER_ID):

    try:
        response = requests.get(
            "https://api.vk.com/method/photos.getAlbums",
            params={
                "owner_id": user_id,
                "access_token": token,
                "v": "5.199",
                "count": count,
                "need_system": 1
            },
            timeout=10
        ).json()


        if "response" in response:
            albums = response["response"]["items"]


            print(f"Всего альбомов: {len(albums)}")
            print("=" * 50)

            for album in albums:
                size = album.get('size', 0)
                print(f"{album['title']}| Фото: {size} шт.")



        else:
            error_msg = response.get("error", {}).get("error_msg", "Неизвестная ошибка")
            print(f"Ошибка: {error_msg}")

    except Exception as e:
        print(f"Ошибка запроса:{str(e)}")

def show_help():
    print("\nДоступные команды:")
    print("  friends - показать друзей")
    print("  followers N - показать N подписчиков (по умолчанию 100)")
    print("  subscriptions N - показать N подписок (по умолчанию 100)")
    print("  albums N - показать N фотоальбомов (по умолчанию 100)")
    print("  help - показать эту справку")
    print("  q - выход")


def main():
    with open("token.txt")as f:
        token=f.readline()
    print("VK Data Fetcher")
    print("Введите команду (help для справки)")

    while True:
        command = input("\n> ").strip().lower()

        if command == 'q':
            print("Выход из программы")
            break

        elif command == 'help':
            show_help()

        elif command == 'friends':
            get_friends(token)

        elif command.startswith('followers'):
            try:
                count = int(command.split()[1]) if len(command.split()) > 1 else 100
                get_followers(count,token)
            except ValueError:
                print("Ошибка: введите число после команды")

        elif command.startswith('subscriptions'):
            try:
                count = int(command.split()[1]) if len(command.split()) > 1 else 100
                get_subscriptions(count,token)
            except ValueError:
                print("Ошибка: введите число после команды")

        elif command.startswith('albums'):
            try:
                count = int(command.split()[1]) if len(command.split()) > 1 else 100
                get_photo_albums(count,token)
            except ValueError:
                print("Ошибка: введите число после команды")

        else:
            print("Неизвестная команда. Введите 'help' для справки")

if __name__=="__main__":
    main()