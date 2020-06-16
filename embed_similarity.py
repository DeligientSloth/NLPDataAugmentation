import synonyms
from numpy import dot
from numpy.linalg import norm

def word2vector(word):
    try:
        vector = synonyms.v(word)
    except Exception as e:
        vector = None
    return vector

def cos_similarity(v1, v2):
    if v1 is None or v2 is None:
        return None
    return dot(v1, v2) / ((norm(v1)+1e-10) * (norm(v2)+1e-10))

def word_similarity(w1, w2):
    '''
    word similarity by embedding
    '''
    return cos_similarity(word2vector(w1), word2vector(w2))

if __name__ == '__main__':
    print(word_similarity('设置', '设立'))