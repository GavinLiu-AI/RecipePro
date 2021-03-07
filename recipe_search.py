import tweepy
import time
import logging
from datetime import datetime
import pickle
import os

API_KEY = 'Os4mmoHxVlTDexaoBI6pPltYb'
API_SECRET = 'PCgtTiGWubdnp1fHyDpPyP3PdopULxsc3i34KMELABPkslYHy3'
ACCESS_TOKEN = '1368266407125733376-BIH1qjjXngmnOZwmjQZzfVJLoCizMI'
ACCESS_SECRET = '2OBxdizhvn5mY0WG3UwlFDWNbQt2G9PUhXKdkUznrRtIM'

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
user = api.me()
FILE_DIR = os.path.dirname(os.path.abspath(__file__))


# Load recipe map
def load_map():
    with open(FILE_DIR + '\\recipe-map\\recipes.pkl', 'rb') as f:
        data = pickle.load(f)
        print('Recipe map loaded')
        return data


def save_last_recipe(recipe):
    with open(FILE_DIR + '\\recipe-map\\last_recipe.pkl', 'wb') as f:
        print('\nLast recipe saved')
        print(recipe)
        pickle.dump(recipe, f)


def load_last_recipe():
    with open(FILE_DIR + '\\recipe-map\\last_recipe.pkl', 'rb') as f:
        data = pickle.load(f)
        print('\nLast recipe loaded')
        print(data)
        return data


def search_recipe(search):
    recipe_map = load_map()

    result = [key for key, value in recipe_map.items() if search in value]
    recipe = [value for _, value in recipe_map.items() if search in value]

    print('\nFound: ')
    for r in recipe:
        print(r)

    return result


def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def get_page(index, total_page):
    return '(' + str(index + 1) + '/' + str(total_page) + ')'


def send_recipe():
    print('\nSearching for: ', direct_message)

    result = search_recipe(direct_message)

    if result:
        # Break results into chunks of 4
        result = [result[i:i + 4] for i in range(0, len(result), 4)]

        total_page = len(result)
        for index, recipe_group in enumerate(result):
            # Upload images and get media_ids
            media_ids = []
            for recipe in recipe_group:
                res = api.media_upload('images/' + str(recipe))
                media_ids.append(res.media_id)

            # Tweet with multiple images
            status_text = 'Recipes for ' + direct_message + ' ' + get_page(index, total_page)
            api.update_status(status=status_text, media_ids=media_ids)
            if index == len(result) - 1:
                print('\nAll recipes tweeted. DONE!')
            else:
                print('\nTweeted some recipes, more to go!')
            time.sleep(5)

        api.send_direct_message(sender_id,
                                'I found the recipes for ' + direct_message + '. Check my tweets! ' + get_time())
        print('\nUser notified via DM.')
    else:
        print('\nNo recipes found')
        api.send_direct_message(sender_id, 'Sorry! I could not find recipes for ' + direct_message + '. ' + get_time())

    save_last_recipe(direct_message)
    return


while True:
    try:
        print('-------------------------------')
        # My own sender_id = '1368266407125733376'
        dms = api.list_direct_messages()
        while dms[0].message_create['sender_id'] == '1368266407125733376':
            dms.pop(0)
        direct_message = str(dms[0].message_create['message_data']['text']).lower()
        print('DM Request: ', direct_message)
        sender_id = dms[0].message_create['sender_id']

        # Load last recipe
        last_recipe = load_last_recipe()

        direct_message = direct_message.split(' ')
        if 'find' == direct_message[0]:
            direct_message.pop(0)
            direct_message = ' '.join(direct_message).strip()

            if last_recipe != direct_message:
                send_recipe()
            else:
                print('Search aborted: Recipe already found')

        time.sleep(60)

    except tweepy.RateLimitError as e:
        logging.error("Twitter api rate limit reached".format(e))
        time.sleep(60)
        continue
