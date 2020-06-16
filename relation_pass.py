# zh = '氩弧焊焊不结实怎么办'
#
# from googletrans import Translator
# translator = Translator(service_urls=['translate.google.cn'])
# en = translator.translate(zh, src='zh-CN').text
# print(en)
# zh = translator.translate(en, dest='zh-CN').text
# print(zh)
'''
1、句子关系传递
2、随机词替换（word embedding）
'''
def relation_pass(input_path, output_path):
    '''
    匹配和不匹配
    :return:
    '''
    d = {}
    count = 0
    with open(input_path, encoding='utf-8',) as input_file:
        for line in input_file:
            line = line.strip().replace('|', '').split('\t')
            query, question, label = line
            if query not in d:
                d[query] = []
            else:
                d[query].append((question, label))
    with open(output_path, mode='w', encoding='utf-8', ) as output_file:
        for query in d:
            set0 = [item[0] for item in d[query] if float(item[1]) == 0 or float(item[1]) == 1]
            set1 = [item[0] for item in d[query] if float(item[1]) == 2]

            for query in set1:
                for question in set0:
                    output_file.write(query + '\t' + question + '\t' + '0')
                    output_file.write('\n')
                    count += 1
    print(count)

relation_pass('./train.txt', './augment/train_augment.txt')

# #使用方法
# from googletrans import Translator
# translator = Translator(service_urls=['translate.google.cn'])
# source = 'QQ怎样把不是好友的人拉入黑名单？'
# text = translator.translate(source,src='zh-cn',dest='en').text
# print(text)
# text = translator.translate(text,dest='zh-cn',src='en').text
# print(text)