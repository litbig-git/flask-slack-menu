import requests


# Google Custom Search https://byeonghun-lee.github.io/2017/06/29/googleCustomSearch/
def get_img_urls(word, num=3) -> list:
    url = 'https://customsearch.googleapis.com/customsearch/v1'
    api_key = 'AIzaSyBd-izRgvtuXg_Kc4pYbAiXQN_94BzBW2o'
    engine_id = '0170d06dac8d18b01'
    search_word = word
    params = {
        'key': api_key,
        'cx': engine_id,
        'q': search_word,
        'num': num
    }
    response = requests.get(url=url, params=params)
    if 'error' in response.json() and response.json().get('error')['code'] == 429:
        print('Google Custom Search free tier is exceed!')
        return None

    items = response.json()['items']
    ret = list()
    for item in items:
        try:
            url = item['pagemap']['cse_thumbnail'][0]['src']
        except:
            continue
        finally:
            print(url)
            ret.append(url)

    return ret


def get_img_url(word, num=3) -> str:
    urls = get_img_urls(word, num)
    if urls:
        return urls[0]


if __name__ == '__main__':
    print(get_img_url('계란'))
