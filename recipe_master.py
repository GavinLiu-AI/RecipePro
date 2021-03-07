import pickle
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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


# Get current images in the directory
def get_dir_images(extension):
    image_dir = 'images'

    # Get all image names without extension
    image_list = []
    for filename in os.listdir(image_dir):
        if not extension:
            filename = os.path.splitext(filename)[0]
        image_list.append(filename)
    return image_list


# Add new recipes
def create_mode():
    print('-------------------------------')
    print('Creating new recipes\n')

    image_list = get_dir_images(extension=True)

    fig = plt.figure(figsize=(10, 10))
    fig.set_tight_layout(True)
    plt.axis('off')

    recipe_map = load_map()
    for image in image_list:
        # image_name = os.path.splitext(image)[0]
        if image not in recipe_map:
            # Image name without extension
            plt.ion()
            recipe_img = mpimg.imread('images/' + image)
            plt.imshow(recipe_img, aspect='auto')
            plt.waitforbuttonpress()

            # Enter one line
            recipe_map[image] = str(input('\nRecipe for ' + image + ': ')).lower()
            plt.clf()

    save_map(recipe_map)
    return


def edit_mode(key, value):
    recipe_map = load_map()

    if key in recipe_map.keys():
        old_value = recipe_map[key]
        recipe_map[key] = value
        save_map(recipe_map)
        print('Updated: Recipe for ', key, ' changed from ', old_value, ' to ', value)
    else:
        print('Key not found in recipe map')


# Update recipes based on current images
def remove_recipes():
    print('-------------------------------')
    print('Removing old recipes\n')
    recipe_map = load_map()
    image_list = get_dir_images(extension=False)

    remove_list = []
    for key in list(recipe_map.keys()):
        if key not in image_list:
            remove_list.append(key)

    # Skip if nothing to remove
    if not remove_list:
        print('SKIPPED: Nothing to remove')
        return

    # Confirm to remove recipes
    print('About to remove: ', remove_list)
    confirm = str(input('Confirm? (y/n): ')).lower()
    if confirm == 'y':
        for key in remove_list:
            recipe_map.pop(key)
        save_map(recipe_map)
        print('UPDATED: removed old recipes\n\n')
    else:
        print('Aborted')
    return


def clear_recipe():
    # Confirm to remove recipes
    print('About to clear ALL recipes')
    confirm = str(input('Confirm? (y/n): ')).lower()

    if confirm == 'y':
        recipe_map = dict()
        save_map(recipe_map)
    return


def search_recipe(search):
    recipe_map = load_map()

    result = [key for key, value in recipe_map.items() if search in value]
    recipe = [value for _, value in recipe_map.items() if search in value]

    print('\nFound: ')
    for r in recipe:
        print(r)

    return result


def run(create, remove, clear):
    if clear:
        clear_recipe()
    if remove:
        remove_recipes()
    if create:
        try:
            create_mode()
            print('Added new recipes successfully\n\n')
        except:
            print('ERROR: Create failed')
    return


if __name__ == '__main__':
    run(create=True, remove=False, clear=False)
    # edit_mode('IMG_8685.JPEG', 'christmas steak marinade beef')
    # search_recipe('cookies')
