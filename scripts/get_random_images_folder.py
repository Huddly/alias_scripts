from get_random_images import get_random_images_from_container
import argparse
from bbox import AnnotationContainer

ALIAS_NAME = 'random_image_folder'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show entries from annotation container.')

    parser.add_argument('path', metavar='FILE', type=str, help='Container')

    args = parser.parse_args()

    container_paths = Path(args.path).glob('**/*.bbox')

    random_cont = new AnnotationContainer()
    for c_path in container_paths:
      name = c_path.split('/')[-1]
      new_cont = get_random_images_from_container(c_path, number = args.number, image_prefix=name)
      random_cont.merge(new_cont)

    random_cont.to_file(os.path.join(path, 'total_random.bbox'))
