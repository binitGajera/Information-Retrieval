import html2text                   #to convert html to text format
import time
from math import log               #to compute log in IDF function

hyper = html2text.HTML2Text()
hyper.ignore_links = True          #ignoring the urls to external documents

from os import listdir
from os.path import isfile, join

def IDF(query, data):              #calculates the idf value for a token in the specified document
    N = len(data)
    nq=0
    for document in data:
        if query in data[document].keys():          #checks whether thee query occurs in a document
            nq += 1                                 #increases the count by one if the query occurs in one document
    result = log(N/nq)
    return result                                   #returns the calculated IDF

def tokenize(tf):
    if tf is not None:
        words = tf.lower().split() #creating the tokens
        return words
    else:
        return None
        
def create_map(tokens):
    hash_map = {}

    if tokens is not None:
        for ele in tokens:
            # Remove Punctuation
            word = ele.replace(",","")    #removing the comma punctuation
            word = word.replace(".","")   #removing the full stop puntuation
            word = word.replace("\"", "") #ignoring the back-slash in tokens

            # Word Exist?
            if word in hash_map:
                hash_map[word] = hash_map[word] + 1   #counting the frequency of a token where 'word' is the token
            else:
                hash_map[word] = 1

        return hash_map
    else:
        return None

start = time.time()
onlyfiles = [f for f in listdir("../files") if isfile(join("../files", f))]
stop_list = open("stoplist.txt", "r")           #reading the stoplist.txt file provided
stop_tokens = tokenize(stop_list.read())        #tokenizing the same to obtain the stop words in a list

preprocessed_data = {}                          #intializing the main dictionary
for i in onlyfiles:
    with open("../files/"+i, "r", encoding="ISO-8859-1") as o_file:     #opening a html file, so keeping the encoding as ISO-8859-1
        file_data = o_file.read()
    
    html_text = hyper.handle(file_data)                      #converting the htmls to text files
    tokenizer = tokenize(html_text)             #calling the method
    word_map = create_map(tokenizer)
    f_name = i.split('.')
    preprocessed_data.update({f_name[0] : {}})  #adding the document name as key to later identify it uniquely
    for lm in word_map:                     #checking each token for the stop words and other reequested operation
        if len(lm)==1 or word_map[lm]==1 or lm in stop_tokens:
            pass                            #do nothing if those conditions are met because they are not needed
        else:
            preprocessed_data[f_name[0]].update({lm: word_map[lm]})

doc_length = {}    #the dictionary to maintain total tokens inside a document
avgdl=0
k1 = 1.2           #value of k1 for BM25
b = 0.75           #value of b for BM25
tf={}              #maintaing a seperate dictionary with normalized term frequencies

#for loop to calculate the total tokens inside a document and average lenght of a document in the collection
for documents in preprocessed_data:
    freq=0
    for temp_word, temp_freq in preprocessed_data[documents].items():
        freq+=temp_freq
        avgdl+=temp_freq
    doc_length.update({documents: freq})
avgdl = avgdl/len(preprocessed_data)

#for loop to normalize the term frequencies
for do in preprocessed_data:
    tf.update({do : {}})
    for w, f in preprocessed_data[do].items():
        tf[do].update({w : f/doc_length[do]})

#for loop to calculate the score value using the BM25 term weighting method
for docs in preprocessed_data:
    f_text = open("txt_files/"+docs+".txt", "w+", encoding="utf-8")
    for doc_word, doc_freq in preprocessed_data[docs].items():
        idf = IDF(doc_word, preprocessed_data)
        #score is the term weight we get by using the formula of BM25 mentioned in the reeport 
        score = idf * ( (tf[docs][doc_word] * (k1+1) ) / (tf[docs][doc_word] + ( k1 * ( 1 - b + ( b * ( doc_length[docs]/avgdl ) ) ) ) ) )
        f_text.write(str(doc_word) + " - " + str(round(score, 2)) + "\n")
    f_text.close()

end = time.time()
print("Total running time: " + str(end-start))