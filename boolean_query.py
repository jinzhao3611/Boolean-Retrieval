"""This module provides an interface for the Boolean search engine

boolean_query.py
Dependencies: python 3.x, flask

To start the application:
   >python boolean_query.py
To terminate the application, use control-c
To use the application within a browser, use the url:
   http://127.0.0.1:5000/
"""

from flask import Flask, render_template, request
from boolean_search import dummy_search, dummy_movie_data, dummy_movie_snippet
from boolean_index import intersection
import shelve

# Create an instance of the flask application within the appropriate namespace (__name__).
app = Flask(__name__)


# Welcome page
@app.route("/")
def query():
    return render_template('query_page.html')


# This takes the form data produced by submitting a query page request and returns a page displaying
# results (SERP).
@app.route("/results/<int:page_num>", methods=['POST'])
def results(page_num):
    """Generate a result set for a query and present the 10 results starting with <page_num>."""

    # page_num = int(request.form['page_num'])
    film_shelve_1 = shelve.open('film_inverted_index_1', writeback=False)
    film_shelve_2 = shelve.open('film_inverted_index_2', writeback=False)
    director_shelve = shelve.open('director_inverted_index', writeback=False)
    starring_shelve = shelve.open('starring_inverted_index', writeback=False)
    location_shelve = shelve.open('location_inverted_index', writeback=False)
    fields = ['query', 'director', 'starring', 'location']
    shelve_dict = {'query': film_shelve_1, 'director': director_shelve, 'location': location_shelve,
                   'starring': starring_shelve}
    # shelves for queries over terms in different fields

    skipped = []
    unknown_terms = []
    ids_list = []
    queries = []
    # list containers for stopwords, unknown words, DocIDs, raw queries

    for field in fields:
        # populate the list containers defined before
        raw_query = request.form[field]
        queries.append(raw_query)
        if raw_query:
            ids, skippedwords, unk = dummy_search(raw_query, shelve_dict[field])
            ids_list.append(ids)
            skipped.extend(skippedwords)
            unknown_terms.extend(unk)
    ids_list[0].extend(dummy_search(request.form['query'], film_shelve_2)[0])
    movie_ids = intersection(ids_list)
    # If your search finds any query terms that are not in the index, add them to unknown_terms and
    # render the error_page.
    if unknown_terms:
        return render_template('error_page.html', unknown_terms=unknown_terms)
    else:
        # render the results page
        num_hits = len(movie_ids)  # Save the number of hits to display later
        movie_ids = movie_ids[((page_num - 1) * 10):(page_num * 10)]  # Limit of 10 results per page
        movie_results = list(map(dummy_movie_snippet, movie_ids))  # Get movie snippets: title, abstract, etc.
        return render_template('results_page.html', orig_query1=queries[0],
                               orig_query2=queries[1], orig_query3=queries[2], orig_query4=queries[3],
                               results=movie_results, srpn=page_num, len=len(movie_ids), skipped_words=skipped,
                               total_hits=num_hits)


# Process requests for movie_data pages
# This decorator uses a parameter in the url to indicate the doc_id of the film to be displayed
@app.route('/movie_data/<film_id>')
def movie_data(film_id):
    """Given the doc_id for a film, present the title and text (optionally structured fields as well)
    for the movie."""
    data = dummy_movie_data(film_id)  # Get all of the info for a single movie
    return render_template('doc_data_page.html', data=data)


# If this module is called in the main namespace, invoke app.run().
# This starts the local web service that will be listening for requests on port 5000.
if __name__ == "__main__":

    app.run(debug=True)
    # While you are debugging, set app.debug to True, so that the server app will reload
    # the code whenever you make a change.  Set parameter to false (default) when you are
    # done debugging.






