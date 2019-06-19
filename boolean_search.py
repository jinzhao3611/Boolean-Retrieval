from boolean_index import conjunctive_query
from nltk import sent_tokenize
import shelve


def dummy_search(query, shelve):
    """Return a list of movie ids that match the query."""
    token_list = query.split()
    ids, stopwords, unknown = conjunctive_query(token_list, shelve)
    return ids, stopwords, unknown


def dummy_movie_data(doc_id, shelvename='article_shelve'):
    """
    Return data fields for a movie.
    Your code should use the doc_id as the key to access the shelf entry for the movie doc_data.
    You can decide which fields to display, but include at least title and text.
    """
    article_shelve = shelve.open(shelvename, writeback=False)
    movie_data = article_shelve[doc_id]
    article_shelve.close()
    return movie_data


def dummy_movie_snippet(doc_id):
    """
    Return a snippet for the results page: (doc_id, "Movie title", "Place movie snippet here")
    Needs to include a title and a short description.
    Your snippet does not have to include any query terms, but you may want to think about implementing
    that feature. Consider the effect of normalization of index terms (e.g., stemming), which will affect
    the ease of matching query terms to words in the text.
    """
    movie_data = dummy_movie_data(doc_id, shelvename='article_shelve')
    title = movie_data['Title']
    # display the first two sentences of the free text for each movie on the results page
    description = ' '.join(sent_tokenize(movie_data['Text'])[:2])
    result = (doc_id, title, description)
    return result

