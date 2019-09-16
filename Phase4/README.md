# Part 4 of the Project

Here, we would create a retreival engine that returns the top documents/document id that match a given specific query given by the user. It would be working like a search engine, if a query is given that has no relevalence to any document in the collection, then nothing would be returned, otherwise top 10 documents will be returned.

## Approach

To achieve this task, I have used the term-document matrix that we generated in the Part 3 of this project. Also, it is to be noted that as we pre-processed the complete data, I also have pre-processed the query itself with the same pre-processing method as we did for our dataset. So that if a query contains the word *the*, our engine would ignore it, since it is a part of the *stoplist.txt* file.

I also have query weights here, which means that a user can give weight to a query term as per their convenience and how important that query is to the user. We have calculated the similarity score, which would be the end result, by taking the dot product between the query vector and the row corresponding to the document in the term-document matrix. 

For each term in the query, the documents in which it appeared is obtained and then the query term weight is multiplied with the corresponding term weight from the term-document matrix. The result of the multiplication is then summed up to achieve the dot product and then stored document-wise in a different vector. This different vector will have document ids as keys and the complete operation will be performed for every document in which the query term is present.

To run the program, we would execute the following line in the terminal:
```
python retrieve.py "0.8 international 1.0 affairs"
```

The output here is a ranked list of documents with respect to the query that has been provided in the form of arguments when running the python program file. The first ten top-scoring documents are shown, where the first value of the tuple is the filename and the second element of the tuple is the similarity score of that corresponding document with the query provided.
