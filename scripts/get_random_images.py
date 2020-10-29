from random import shuffle
from bbox import AnnotationContainer
import os
import shutil
import argparse

ALIAS_NAME = 'random_image'

def get_random_images_from_container(container_path, labels=[], prune=False, max_labels=float('inf'), min_labels=0, path='', number=100, min_area = 0, max_area = float('inf'), image_prefix = None):
    cont = AnnotationContainer.from_file(container_path)
    new_cont = AnnotationContainer(dataset_source_provider=cont.dataset_source_provider)
    if labels and len(labels) > 0:
        cont = cont.with_selected_labels(labels, prune_empty_entries=prune, in_place=True)

    entry_keys = list(cont.entries.keys())
    shuffle(entry_keys)

    key = None
    i = 0
    not_found_counter = 0
    found_counter = 0
    successfully_shown = set()
    for k in entry_keys:
            e = cont.entries[k]
            if not e.get_image_full_path().exists():
                print('Entry:', k, 'is not found.')
                not_found_counter += 1
                continue


            labels = [inst.label for inst in e]
            image_area = e.image_size.width * e.image_size.height
            areas = [(inst.area()/image_area) for inst in e]
            not_enough_labels = False
            for l in labels:
                if max_labels is not None and labels.count(l) > max_labels or labels.count(l) < min_labels:
                    print('Entry:', k, 'Does not have enough labels.', labels.count(l))
                    not_enough_labels = True
                    break
                else:
                    print('Labels', labels.count(l))

            if not_enough_labels:
                not_found_counter += 1
                continue

            is_over_min = all(a > min_area for a in areas)
            is_under_max = all(a < max_area for a in areas)

            if not is_over_min or not is_under_max:
                not_found_counter += 1
                continue

            path = e.get_image_full_path()
            print("Found", path, path)
            image_name = image_prefix + e.image_name if image_prefix is not None else e.image_name
            e.image_name = image_name
            new_path = os.path.join(path, image_name)
            shutil.copy(path, new_path)
            new_cont.add_entry(e)
            if number is not None and number <= found_counter:
                print(f'Max number ({number}) of images shown')
                break

            found_counter += 1

    if not_found_counter > 0:
            print('\tNB:\t\tTried to copy', not_found_counter, 'missing images.')

    new_cont.to_file(os.path.join(path, 'container_random.bbox'))
    new_cont.to_file(os.path.join(path, 'container_random.json'))
    new_cont.summary()

    return new_cont

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show entries from annotation container.')

    parser.add_argument('container', metavar='FILE', type=str, help='Container')
    parser.add_argument('-l', '--labels', type=str, nargs='*', help='Only show these labels')
    parser.add_argument('-p', '--path', type=str, default=None, help='Path to copy dir')
    parser.add_argument('-n', '--number', type=int, default=None, help='Number of images to copy to path')
    parser.add_argument('-pr', '--prune', action='store_true', help='Prune empty entries')
    parser.add_argument('-max', '--max_labels', type=int, default=None, help='Max amount of labels in image')
    parser.add_argument('-min', '--min_labels', type=int, default=None, help='Min amount of labels in image')
    parser.add_argument('-mina', '--min_area', type=int, default=None, help='Min size of area %')
    parser.add_argument('-maxa', '--max_area', type=int, default=None, help='Max size of area %')

    args = parser.parse_args()

    container_path = args.container

    get_random_images_from_container(container_path, args.labels, args.prune, args.max_labels, args.min_labels, args.path, args.number, args.min_area, args.max_area)
