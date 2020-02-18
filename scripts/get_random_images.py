from random import shuffle
from bbox import AnnotationContainer
import os 
import shutil
import argparse


ALIAS_NAME = 'contshow'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show entries from annotation container.')

    parser.add_argument('container', metavar='FILE', type=str, help='Container')
    parser.add_argument('-l', '--labels', type=str, nargs='*', help='Only show these labels')
    parser.add_argument('-p', '--path', type=str, default=None, help='Path to copy dir')
    parser.add_argument('-n', '--number', type=int, default=None, help='Number of images to copy to path')
    parser.add_argument('-pr', '--prune', action='store_true', help='Prune empty entries')
    parser.add_argument('-max', '--max_labels', type=int, default=None, help='Max amount of labels in image')
    parser.add_argument('-min', '--min_labels', type=int, default=None, help='Min amount of labels in image')
    args = parser.parse_args()

    container = args.container
    cont = AnnotationContainer.from_file(container)
    new_cont = AnnotationContainer(dataset_source_provider=cont.dataset_source_provider)
    if args.labels and len(args.labels) > 0:
        cont = cont.with_selected_labels(args.labels, prune_empty_entries=args.prune, in_place=True)
    
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
            not_enough_labels = False
            for l in args.labels:
                if args.max_labels is not None and labels.count(l) > args.max_labels or labels.count(l) < args.min_labels:
                    print('Entry:', k, 'Does not have enough labels.', labels.count(l))
                    not_enough_labels = True
                    break
                else:
                    print('Labels', labels.count(l))
            
            if not_enough_labels:
                not_found_counter += 1
                continue
            
            path = e.get_image_full_path()
            print("Found", path, args.path)
            new_path = os.path.join(args.path, e.image_name)
            shutil.copy(path, new_path)
            new_cont.add_entry(e)
            if args.number is not None and args.number <= found_counter:
                print(f'Max number ({args.number}) of images shown')
                break

            found_counter += 1

    if not_found_counter > 0:
            print('\tNB:\t\tTried to copy', not_found_counter, 'missing images.')
    
    new_cont.to_file(os.path.join(args.path, 'container_random.bbox'))
    new_cont.to_file(os.path.join(args.path, 'container_random.json'))
    new_cont.summary()

