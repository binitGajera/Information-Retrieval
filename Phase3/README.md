# Part 3 of the Project

In this phase, we will be focusing on building an index for the documents in the collection. We will use one of the most famous approaches for that known as, [inverted file index](https://en.wikipedia.org/wiki/Inverted_index).

## Approach

For this part, we would be needing the term weights that we calculated in tha Part 2 of the project, so we will use the same BM25 weights here. First, we have created a [term-document matrix](https://en.wikipedia.org/wiki/Document-term_matrix) i.e. TDM, this matrix will be storing the frequency of terms in our collection of documents.

To make the lookup and traversal easy and organized we have created a seperate postings file as well which stores the document *id* and *normalized weight of the word in that document*. In the end we return the following information overall stored in a dictionary of Python:

* The word
* The number of documents that contain that word 
* The location of the first record for that word in the postings file
