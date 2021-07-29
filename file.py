import os


def get_file():
    target = ''
    path = './menu'

    for file in sorted(os.listdir(path), reverse=True):
        size = os.path.getsize('{}/{}'.format(path, file))
        if file.endswith('.pdf') and size > 1000:
            # print("file={}, size={}".format(file, size))
            target = file
            break

    return '{}/{}'.format(path, target)


if __name__ == '__main__':
    print(get_file())
