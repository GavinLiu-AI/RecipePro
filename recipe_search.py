import tweepy
import time
import logging
from datetime import datetime
import pickle
import os
import wget
import requests

API_KEY = 'Os4mmoHxVlTDexaoBI6pPltYb'
API_SECRET = 'PCgtTiGWubdnp1fHyDpPyP3PdopULxsc3i34KMELABPkslYHy3'
ACCESS_TOKEN = '1368266407125733376-BIH1qjjXngmnOZwmjQZzfVJLoCizMI'
ACCESS_SECRET = '2OBxdizhvn5mY0WG3UwlFDWNbQt2G9PUhXKdkUznrRtIM'

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
user = api.me()
FILE_DIR = os.path.dirname(os.path.abspath(__file__))


# Save recipe map as image to recipe
def save_map(recipe_map):
    # with open(FILE_DIR + '/recipe-map/recipes.pkl', 'wb') as f:
    with open(FILE_DIR + '\\recipe-map\\recipes.pkl', 'wb') as f:
        print('Recipe map saved')
        print(recipe_map)
        pickle.dump(recipe_map, f)


# Load recipe map
def load_map():
    # with open(FILE_DIR + '/recipe-map/recipes.pkl', 'rb') as f:
    with open(FILE_DIR + '\\recipe-map\\recipes.pkl', 'rb') as f:
        data = pickle.load(f)
        print('Recipe map loaded')
        return data


def save_last_recipe(recipe):
    # with open(FILE_DIR + '/recipe-map/last_recipe.pkl', 'wb') as f:
    with open(FILE_DIR + '\\recipe-map\\last_recipe.pkl', 'wb') as f:
        print('\nLast recipe saved')
        print(recipe)
        pickle.dump(recipe, f)


def load_last_recipe():
    # with open(FILE_DIR + '/recipe-map/last_recipe.pkl', 'rb') as f:
    with open(FILE_DIR + '\\recipe-map\\last_recipe.pkl', 'rb') as f:
        data = pickle.load(f)
        print('\nLast recipe loaded')
        print(data)
        return data


def save_last_upload(recipe):
    # with open(FILE_DIR + '/recipe-map/last_upload.pkl', 'wb') as f:
    with open(FILE_DIR + '\\recipe-map\\last_upload.pkl', 'wb') as f:
        print('\nLast upload saved')
        print(recipe)
        pickle.dump(recipe, f)


def load_last_upload():
    # with open(FILE_DIR + '/recipe-map/last_upload.pkl', 'rb') as f:
    with open(FILE_DIR + '\\recipe-map\\last_upload.pkl', 'rb') as f:
        data = pickle.load(f)
        print('\nLast upload loaded')
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
                # res = api.media_upload(FILE_DIR + '/images/' + str(recipe))
                res = api.media_upload(FILE_DIR + '\\images\\' + str(recipe))
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
        time.sleep(5)

    save_last_recipe(direct_message)
    return


def upload_recipe():
    print('Uploading!')

    image_names = []
    medias = mention.extended_entities['media']
    for image in medias:
        image_names.append(image['media_url'])

    recipe_map = load_map()

    # Download to images folder
    for image in image_names:
        if image not in recipe_map.keys():
            # wget.download(image, FILE_DIR + '/images/')
            wget.download(image, FILE_DIR + '\\test\\')
            print('\nDownloaded image: ', image)

            # Save to recipe map
            recipe_map[image] = upload_label
            print('\nSaved ', image, ': ', upload_label, ' to recipe map')

            api.send_direct_message(mention.author.id_str, 'Recipe for ' + str(upload_label) + ' uploaded. ' + get_time())
            time.sleep(5)
        else:
            print('Download skipped: Image ', image, ' already exists.')

    save_map(recipe_map)
    save_last_upload(upload_label)
    return


while True:
    try:
        print('-------------------------------')
        # My own sender_id = '1368266407125733376'
        dms = api.list_direct_messages()
        time.sleep(5)
        while dms[0].message_create['sender_id'] == '1368266407125733376':
            dms.pop(0)
        direct_message = str(dms[0].message_create['message_data']['text']).lower()
        print('DM Request: ', direct_message)
        sender_id = dms[0].message_create['sender_id']

        # Load last recipe
        last_recipe = load_last_recipe()

        # Upload
        mention = api.mentions_timeline(count=3)[0]
        mention_text = mention.text.split(' ')
        upload_label = []
        for word in mention_text:
            if not ('@' in word or 'http' in word):
                upload_label.append(word.lower())

        direct_message = direct_message.split(' ')
        if 'find' == direct_message[0]:
            direct_message.pop(0)
            direct_message = ' '.join(direct_message).strip()

            if last_recipe != direct_message:
                send_recipe()
            else:
                print('Search aborted: Recipe already found')
        if 'upload' == upload_label[0]:
            upload_label.pop(0)
            upload_label = ' '.join(upload_label)

            if upload_label != load_last_upload():
                upload_recipe()
            else:
                print('Upload aborted: Recipe already uploaded')

        time.sleep(60)

    except tweepy.RateLimitError as e:
        logging.error("Twitter api rate limit reached".format(e))
        time.sleep(60)
        continue
