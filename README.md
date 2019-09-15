# Information-Retrieval
This project performs web scraping for tokenization, clustering and different other tasks for information retrieval. There are different phases to the project which perform different tasks that are used in the last phase to achieve clustering of documents based on the relevalence.

## Dataset

The dataset of the web files is stored in the *files* folder where there are approximately 500 web files used for scraping and finding relevant details and classes based on it. The dataset is completely random so some might have different topics in common while some might have no information in common.

The .html file can be interpreted as any normal news, blog or any other informative web page from where users can read information and developers like us can use for different tasks. One of the task that is not in this project is the page rank algorithm that can also be implemented if there are large number of web pages available to us, but clustering and finding relevalent information between all this pages can be considered as one part of the algorithm.

## Code

The code is written in Python and no NLP libraries have been used to achieve results. There are many libraries out there now a days that would have achieved the same or even better results than this in shorter period of time and fewer lines of code but I, personally prefer to code this project with as less number of libraries as possible to understand the concept more clearly and implement it thoroughly.

Few of the libraries used are:

* html2text - To convert the html files to text files and make it more understandable to Python
* collections - To calculate a [Similarity Matrix](http://www.biocomp.unibo.it/casadio/LMBIOTEC/Similarity_matrix)
* math - To calculate the [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) score
