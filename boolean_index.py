"""this module generate inverted index for each query box, generate the article shelve, offer conjunctive query """

import shelve
import json
from preprocessing import PreProcessing
import time
from nltk import word_tokenize

# instantiate pp to access normalize and flatten, and to create the test corpus
prep = PreProcessing()


def timing(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        func(*args, **kwargs)
        t2 = time.time()
        print("Time it took to build this index: " + str((t2 - t1)) + "\n")
    return wrapper


@timing
def main_query_inverted_index(shelvename1, shelvename2, corpus_name='2018_movies.json'):
    """
    create a title+free text inverted index, and put it into 2 shelve files (because one cannot hold)
    :param shelvename1: String
    :param shelvename2: String
    :param corpus_name: String a json file
    """
    with open(corpus_name) as f:
        corpus = json.load(f)

    docIDs = sorted(corpus.keys(), key=lambda d: int(d))

    for i, docID in enumerate(docIDs):
        # split the info in each doc into two shelves
        if i < 1500:
            inverted_shelve = shelve.open(shelvename1, writeback=False)
        else:
            inverted_shelve = shelve.open(shelvename2, writeback=False)

        title = corpus[docID]['Title'][0]
        text = corpus[docID]['Text']

        tokens = word_tokenize(title + ' ' + text)
        # the title phrase is seen as a separate token
        tokens.append(title.strip())

        # all the distinct terms in one doc
        terms = set(prep.normalize(token) for token in tokens
                    if prep.normalize(token) is not None and prep.normalize(token) is not '')

        # put the terms into the shelves
        for term in terms:
            if term not in inverted_shelve:
                inverted_shelve[term] = [docID]
            else:
                # assign the existing postings list to temp
                temp = inverted_shelve[term]
                # append the new docID to the postings list
                temp.append(docID)
                inverted_shelve[term] = temp
        inverted_shelve.close()
    print('film inverted index has been created!')


@timing
def fields_inverted_index(shelvename, field, corpus_name='2018_movies.json'):
    """
    create a shelve containing the inverted index of given field, from the json file
    :param shelvename:
    :param field:
    :param corpus_name:
    """
    with open(corpus_name) as f:
        corpus = json.load(f)

    inverted_shelve = shelve.open(shelvename, writeback=False)

    docIDs = sorted(corpus.keys(), key=lambda d: int(d))

    for docID in docIDs:
        field_value = corpus[docID][field]

        # tokenize the field value
        field_token = prep.flatten(field_value)
        tokens = word_tokenize(' '.join(field_token))
        # include the field name phrase into tokens
        tokens.extend(field_token)

        terms = set(prep.normalize(token) for token in tokens
                    if prep.normalize(token) is not None and prep.normalize(token) is not '')

        for term in terms:
            if term not in inverted_shelve:
                inverted_shelve[term] = [docID]
            else:
                temp = inverted_shelve[term]
                temp.append(docID)
                inverted_shelve[term] = temp
    inverted_shelve.close()
    print(field + ' inverted index has been created!')


@timing
def article_shelve(filename='2018_movies.json', shelvename='movie_page'):
    """Get all the doc data(displayed after clicking on a film title in the result page) and store it in a shelve."""
    with open(filename, 'rb') as f:
        corpus = json.load(f)

    ar_shelve = shelve.open(shelvename, writeback=False)

    for id in corpus.keys():
        starring_list = prep.flatten(corpus[id]['Starring'])
        ar_shelve[id] = {'Title': corpus[id]['Title'], 'Starring': ', '.join(starring_list),
                         'Director': corpus[id]['Director'], 'Location': corpus[id]['Location'],
                         'Text': corpus[id]['Text']}
    print('article shelve has been created!')


def intersection(posting_lists):
    """
    :param posting_lists: a list of multiple postings lists to be intersected, the postings are sorted
    :return: a list containing intersected docIDs
    """
    # return empty
    if not posting_lists:
        return []
    # base case: return the only postings list in the list
    elif len(posting_lists) == 1:
        return posting_lists[0]

    result = []
    i, j = 0, 0

    while i < len(posting_lists[0]) and j < len(posting_lists[1]):
        # if the ith docID in the 1st posting list is bigger
        # than the jth docID in the 2nd postings list, advance j
        if int(posting_lists[0][i]) > int(posting_lists[1][j]):
            j += 1
        elif int(posting_lists[0][i]) < int(posting_lists[1][j]):
            i += 1
        else:
            result.append(posting_lists[0][i])
            i += 1
            j += 1
    # delete the first two lists that has been intersected
    del posting_lists[:2]
    posting_lists.insert(0, result)

    return intersection(posting_lists)  # intersect recursively


def conjunctive_query(tokens, shelve_name):
    """
    :param tokens: tokenized query
    :param shelve_name: the shelve that contained inverted index of certain field
    :return: possibly a list of matching docIDs, a list of stopwords, and a list of unknown words
    """
    stopwords = []
    unknown = []
    terms = []

    for token in tokens:
        # normalize the input query and get lists of valid terms, unknown and stopwords
        normalized_token = prep.normalize(token)
        if normalized_token is None:
            stopwords.append(str(token))
        else:
            if normalized_token not in list(shelve_name.keys()):
                unknown.append(str(token))
            else:
                terms.append(normalized_token)
    if unknown:
        # if there is at least one unknown word, return an empty list
        return [], stopwords, unknown

    posting_lists = [shelve_name[term] for term in terms]
    # compare the shortest postings list first
    posting_lists = sorted(posting_lists, key=lambda d: len(d))
    # sort the posting list, so we can intersect the shortest lists first
    result = intersection(posting_lists)

    return result, stopwords, unknown


if __name__ == '__main__':
    print('waiting...')
    # generate the test_corpus.py
    prep.test_corpus()

    for field in ['Director', 'Starring', 'Location']:
        fields_inverted_index(shelvename=field + '_inverted_index', field=field)

    main_query_inverted_index(shelvename1='Text_inverted_index_1', shelvename2='Text_inverted_index_2')

    article_shelve()
    print("done!")



