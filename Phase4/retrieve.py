import html2text                   #to convert html to text format
import time
from math import log               #to compute log in IDF function
import sys
from pprint import pprint
import operator

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

weight_dict = {}
#for loop to calculate the score value using the BM25 term weighting method
for docs in preprocessed_data:
    weight_dict.update({docs : {}})
    for doc_word, doc_freq in preprocessed_data[docs].items():
        idf = IDF(doc_word, preprocessed_data)
        #score is the term weight we get by using the formula of BM25 mentioned in the reeport 
        score = idf * ( (tf[docs][doc_word] * (k1+1) ) / (tf[docs][doc_word] + ( k1 * ( 1 - b + ( b * ( doc_length[docs]/avgdl ) ) ) ) ) )
        #storing the calculated score in the required dictionary
        weight_dict[docs].update({doc_word: score})

#creating the matrix of TDM using dictionary
tdm_dict = {}
for doc_id in weight_dict:
    for token, score in weight_dict[doc_id].items():
        tdm_dict.update({token: {}})

#updating the values in tdm
for all_token in tdm_dict:
    for doc_id in weight_dict:
        tdm_dict[all_token].update({doc_id : 0})
        if all_token in weight_dict[doc_id].keys():
            tdm_dict[all_token].update({doc_id: weight_dict[doc_id][all_token]})

#dictionary that will have information for the postings file
postings = []
for tokens in tdm_dict:
    for doc_id, score in tdm_dict[tokens].items():
        #storing only if the score of token is greater than zero
        if score>0:
            postings.append(str(doc_id) + ', ' + str(score))

#the dictionary file that will contain the token, frequency in the collection and position in postings file
final_dict = {}
#the first position of first token in the postings file would be 1
first_occ = 1
for tokens in tdm_dict:
    final_dict.update({tokens: 0})
    #for counting the frequency of a token in the entire collection
    occ=0
    for did, score in tdm_dict[tokens].items():
        if score>0:
            occ = occ + 1
    #updating the necessary values
    final_dict.update({tokens: str(occ)+','+str(first_occ)})
    first_occ = first_occ + occ
    
query = tokenize(sys.argv[1])           #fetching the query terms from the command line arguments
if len(query)%2==0:
    query_format = zip(query[::2], query[1::2])         #building a tuple of (weight, query-term)
    query_final = {}
    for weight, qterm in query_format:          #Iterating through the tuple for preprocessing
        if len(qterm) == 1 or qterm.lower() in stop_tokens:
            pass                            #do nothing if those conditions are met because they are not needed
        else:
            final_qterm = qterm.lower()   
        if len(final_qterm) > 0:    
            query_final[final_qterm] = eval(weight)

    similar_scores = {key: 0 for key in doc_length.keys()}      #dictionay for calculating the similarity scores
    for term, wt in query_final.items():
        if term in tdm_dict.keys():
            for doc in tdm_dict[term].keys():
                similar_scores[doc]  += tdm_dict[term][doc] * wt #dot product for obtaining the similarity score
                
    final_sim_scores = {k+'.html':v for k,v in similar_scores.items() if v != 0} #using only non-zero score obtained
    if len(final_sim_scores) > 0:
        sorted_scores = sorted(final_sim_scores.items(), key=operator.itemgetter(1), reverse=True)      #sorting as per similarity score
        pprint(sorted_scores[:10])      #printing only the top-10 scoring documents
    else:
        print("No results found")
else:
    print('please give arguments of the format "weight query-term"')

end = time.time()
print("Total running time: " + str(end-start))