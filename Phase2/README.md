# Part 2 of the Project

In this phase we will calculate term weights of the tokens that occur in each document for the whole collection.

## Term Weighting

Before we calculate the term weights, it is important to simply normalize the frequency of the types so that we get an appropriate results. To normalize we will simply divide each word type's frequency by the total number of tokens in the document collection.

After all the preprocessing is done, we can calculate the term weights. There are several ways to do this calculation on of the most common approach is the [TF-IDF](http://www.tfidf.com/) approach. But we would not be doing that instead we would implement the [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25) method which is modern and very useful for different applications other than term weighting as well.
