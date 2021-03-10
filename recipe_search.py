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
        # print(recipe_map)
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


def send_recipe(direct_message, sender_id):
    print('\nSearching for: ', direct_message)

    result = search_recipe(direct_message)

    if result:
        num_result = str(len(result))
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
            time.sleep(3)

        api.send_direct_message(sender_id,
                                'I found ' + num_result + ' recipes for ' + direct_message + '. Check my tweets! ' + get_time())
        print('\nUser notified via DM.')
    else:
        print('\nNo recipes found')
        api.send_direct_message(sender_id, 'Sorry! I could not find recipes for ' + direct_message + '. ' + get_time())
        time.sleep(5)

    save_last_recipe(direct_message)
    return


def upload_recipe(mention, upload_text):
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
            recipe_map[image.split('/')[-1]] = upload_text
            print('\nSaved ', image, ': ', upload_text, ' to recipe map')
        else:
            print('Download skipped: Image ', image, ' already exists.')

    save_map(recipe_map)
    api.send_direct_message(mention.author.id_str, 'Recipe for ' + str(upload_text) + ' uploaded. ' + get_time())
    time.sleep(3)
    return


def run():
    while True:
        try:
            # Search recipe
            print('-------------------------------')
            # My own sender_id = '1368266407125733376'
            dms = api.list_direct_messages(count=100)
            time.sleep(5)
            while dms:
                if dms[0].message_create['sender_id'] == '1368266407125733376':
                    dms.pop(0)
                else:
                    break
            if dms:
                direct_message = str(dms[0].message_create['message_data']['text']).lower()
                print('DM Request: ', direct_message)
                sender_id = dms[0].message_create['sender_id']

                last_recipe = load_last_recipe()

                direct_message = direct_message.split(' ')
                if 'find' == direct_message[0]:
                    direct_message.pop(0)
                    direct_message = ' '.join(direct_message).strip()

                    if last_recipe != direct_message:
                        send_recipe(direct_message, sender_id)
                    else:
                        print('Search aborted: Recipe already found.')
            else:
                print('Search aborted: No search requested recently.')

            # Upload
            mentions = api.mentions_timeline(count=20)
            upload_texts = []
            upload_mentions = []
            # Get 5 latest upload
            for mention in mentions:
                if len(upload_texts) == 10:
                    break

                mention_text = mention.text.split(' ')
                upload_label = []
                for word in mention_text:
                    if not ('@' in word or 'http' in word):
                        upload_label.append(word.lower())
                if 'upload' == upload_label[0]:
                    upload_label.pop(0)
                    upload_label = ' '.join(upload_label)
                    upload_texts.append(upload_label)
                    upload_mentions.append(mention)

            last_upload = load_last_upload()  # Should be a list of 5 uploads
            new_upload = []
            for index, upload_text in enumerate(upload_texts):
                if upload_text not in last_upload:
                    upload_recipe(upload_mentions[index], upload_text)
                    new_upload.insert(0, upload_text)
                else:
                    print('Upload aborted: Recipes already uploaded')
                    break

            if new_upload:
                new_upload.reverse()
                new_upload.extend(last_upload)
                save_last_upload(new_upload[0:5])
            else:
                save_last_upload(last_upload)
            time.sleep(30)

        except tweepy.RateLimitError as e:
            logging.error("Twitter api rate limit reached".format(e))
            time.sleep(30)
            continue


if __name__ == '__main__':
    run()
