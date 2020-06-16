import jieba.posseg as pseg

import embed_similarity
import cilin_similarity

cilin_path = './cilin.txt'
stopwords = open('./stopwords.txt',encoding='utf8').read().split('\n')

def cut_sentence(s):
    cut = pseg.cut(s)
    cut = [(_.word, _.flag) for _ in cut]
    sent_cut = [_[0] for _ in cut]
    pos_cut = [_[1] for _ in cut]
    return sent_cut, pos_cut

def syn_similarity(word, syn_words, similarity):
    '''
    同义词排序，根据word embedding相关度排序
    与之前接口一致，返回word和score的列表
    需要传入相似度计算函数
    词林相似度计算以及word embedding相似度计算两种
    '''
    if not syn_words:
        return [], []
    syn_words = [_ for _ in syn_words if _!=word]

    word_scores = []
    for w2 in syn_words:
        score = similarity(word, w2)
        if score!=None:
            word_scores.append((score, w2))
    word_scores.sort(reverse=True)
    words = [_[1] for _ in word_scores]
    scores = [_[0] for _ in word_scores]
    return words, scores

word = '设置'
cilin = cilin_similarity.CilinSimilarity(cilin_path)

cilin_sim = cilin.sim2013
embed_sim = embed_similarity.word_similarity
#
# synwords = cilin.get_synwords(word)
#
# synwords, _ = syn_similarity(word, synwords, cilin_sim)
# print(synwords, _)
#
# synwords, _ = syn_similarity(word, synwords, embed_sim)
# print(synwords, _)


def replace_syn(sent_cut, pos_cut):
    '''
    分词以及词性信息
    '''
    word_idx = None
    syn_word = None
    best_score = 0

    #  替换名词或者动词
    # indices = np.random.choice(range(len(sent_cut)))
    indices = [idx for idx, _ in enumerate(pos_cut) if pos_cut[idx]=='n' or pos_cut[idx]=='v']

    for idx in indices:
        word = sent_cut[idx]
        if word in stopwords:
            continue
        #  查找近义词，不是word本身
        syn_words = cilin.get_synwords(word)
        if len(syn_words)==0:
            continue
        syn_words, scores = syn_similarity(word, syn_words, cilin_sim)
        #  cilin top syn words
        i = 0
        while i<len(scores) and scores[i] == scores[0]:
            i += 1
        top_syn_words = syn_words[:i]

        top_syn_words, scores = syn_similarity(word, top_syn_words, embed_sim)

        if len(top_syn_words) and scores[0] > best_score:
            word_idx = idx
            syn_word = top_syn_words[0]
            best_score = scores[0]

    if best_score < 0.5:
        return None, None
    repalce_word = sent_cut[word_idx]
    sent_cut[word_idx] = syn_word
    return ''.join(sent_cut), (repalce_word, syn_word)


# s = '挂壁空调怎么美观'
# sent_cut, pos_cut = cut_sentence(s)
# print(sent_cut, pos_cut)
# res = replace_syn(sent_cut, pos_cut)
# print(res)

#
#
def synonym_replacement_augment(inp_path, out_path):
    d = {}
    with open(inp_path, encoding='utf-8') as inp_file:
        for line in inp_file:
            query, question, label = line.strip().split('\t')
            if query not in d:
                d[query] = []
            else:
                d[query].append((question, label))

    count = 0
    with open(out_path, mode='w', encoding='utf-8') as out:
        for query in d:
            # sun replace后的query
            sent_cut, pos_cut = cut_sentence(query)
            _query, swap = replace_syn(sent_cut, pos_cut)

            if swap!=None:
                out.write(_query + '\t' + swap[0] + '->' + swap[1])
                out.write('\n')
            qq_list = []
            for question, label in d[query]:

                # sun replace后的question
                sent_cut, pos_cut = cut_sentence(question)
                _question, swap = replace_syn(sent_cut, pos_cut)

                if swap!=None:
                    out.write(_question + '\t' + swap[0] + '->' + swap[1])
                    out.write('\n')

            count += 1
            if count>=100:
                break
                # if query != _query:
                #     qq_list.append((_query, question, label))
                # if question != _question:
                #     qq_list.append((query, _question, label))

            # for query, question, label in qq_list:
            #     out_file.write('\t'.join([query, question, label]))
            #     out_file.write('\n')
#
#
# print(syn_candidate('斩首'))

synonym_replacement_augment('../data/50W/test.txt', '../data/50W/augment/test_syn_augment.txt')
# synonym_replacement_augment('train.txt', './augment/train_augment.txt')

