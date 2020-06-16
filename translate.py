import http.client
import hashlib
import urllib
import random
import time
import json

import multiprocessing

appid = '20200403000411315'  # 填写你的appid
secretKey = '7HjoylhCni3lBsLmeWIr'  # 填写你的密钥

httpClient = None
myurl = '/api/trans/vip/translate'


def _translate(sent, from_lan, to_lan):
    salt = random.randint(32768, 65536)
    sign = appid + sent + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(sent) + '&from=' + from_lan + '&to=' + \
          to_lan + '&salt=' + str(salt) + '&sign=' + sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', url)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)['trans_result'][0]['dst']
        if httpClient:
            httpClient.close()
        return result
    except Exception as e:
        print(e)


def translate_and_back(sent, language):
    res1 = None
    while res1 == None:
        res1 = _translate(sent, 'zh', language)
    res2 = None
    while not res2:
        res2 = _translate(res1, language, 'zh')
    return res2


'''
200个query的结果：1069.5117816925049
226.7929081916809
'''
if __name__ == "__main__":
    d = {}
    input_path = '../data/20190508/processing/train.txt'
    output_path = '../data/20190508/processing/translate/train_translate.txt'
    with open(input_path, encoding='utf-8') as inp_file:
        for line in inp_file:
            query, question, label = line.strip().split('\t')
            if query not in d:
                d[query] = [(question, label)]
            else:
                d[query].append((question, label))

    pool = multiprocessing.Pool(processes=4)
    result = []

    count = 0
    time0 = time.time()

    for query in d:
        result.append(pool.apply_async(translate_and_back, (query, 'jp')))
        # translate_and_back(query, 'jp')
        for question, label in d[query]:
            # bt = translate_and_back(question, 'jp')
            result.append(pool.apply_async(translate_and_back, (question, 'jp')))
            # translate_and_back(question, 'jp')

        count += 1

    pool.close()
    pool.join()
    with open(output_path, mode='w', encoding='utf-8') as out:
        for res in result:
            out.write(res.get())
            out.write('\n')
    print(time.time()-time0)

