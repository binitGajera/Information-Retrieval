import html2text                   #to convert html to text format
import time
from math import log               #to compute log in IDF function
import math
import sys
from pprint import pprint
import operator
import collections

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

#Calculate the denominator of cosine similarity
def cos_den(doc):
    calc = sum(val ** 2 for val in weight_dict[doc].values())
    return math.sqrt(calc)

#Calculate the dot product of the passed documents
def dot_product(doc1, doc2):
    k = weight_dict[doc1].keys() & weight_dict[doc2].keys()
    res = sum(weight_dict[doc1][key] * weight_dict[doc2][key] for key in k)
    return res

#Get the total number of clusters that are set as current
def get_current_clusters():
    return len([i for i, e in enumerate(current_clusters.values()) if e != -1])

#Get highest similarity scores from the current clusters
def high_sim_score():
    flag = -1
    maximum = (flag, 0, 0)
    for d1 in sim_matrix.keys():
        for d2 in sim_matrix[d1].keys():
            if d1 != d2: #ignoring similarity with itself
                if current_clusters[d1] != -1 and current_clusters[d2] != -1: #checking if cluster is present or not
                    score = sim_matrix[d1][d2]
                    if score > flag and score != 1:
                        flag = score
                        maximum = (flag, d1, d2)
    return maximum

#Check whether the passed element is cluster or a document
def check_whether_document(ele):
    if isinstance(ele, str):
        return [(ele)]
    else:
        return cluster_info[ele]

#Get the document that is closest to the centroid
def high_sim_centroid(d1, cluster):
    flag = -1
    maximum = (flag, 0, 0)
    for d2 in cluster_info[cluster]:
        if d1 != d2: #ignoring similarity with itself
            #import ipdb; ipdb.set_trace()
            if d2 in sim_matrix[d1].keys():
                score = sim_matrix[d1][d2]
            else:
                score = sim_matrix[d2][d1]
            if score > flag and score != 1:
                flag = score
                maximum = (flag, d1, d2)
    return maximum

#Perform the Group Average Link calculation
def group_link(new_cluster, other_cluster):
    nc_num = current_clusters[new_cluster]
    oc_num = current_clusters[other_cluster]
    if isinstance(other_cluster, str):
        ocluster = [(other_cluster)]
    else:
        ocluster = cluster_info[other_cluster]
    before_avg = 0
    for y in ocluster:
        for x in cluster_info[new_cluster]:
            if x in sim_matrix[y].keys():
                before_avg += sim_matrix[y][x]
            else:
                before_avg += sim_matrix[x][y]
    avg = before_avg / (nc_num + oc_num)
    return avg

def median(mylist):
    #Ref: http://stackoverflow.com/questions/10482339/how-to-find-median
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[int(length / 2)]

start = time.time()
# Phase 1
# =============================================================================
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
# =============================================================================

# Phase 2
# =============================================================================
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
    weight_dict.update({str(docs)+".html" : {}})
    for doc_word, doc_freq in preprocessed_data[docs].items():
        idf = IDF(doc_word, preprocessed_data)
        #score is the term weight we get by using the formula of BM25 mentioned in the reeport 
        score = idf * ( (tf[docs][doc_word] * (k1+1) ) / (tf[docs][doc_word] + ( k1 * ( 1 - b + ( b * ( doc_length[docs]/avgdl ) ) ) ) ) )
        #storing the calculated score in the required dictionary
        weight_dict[str(docs)+".html"].update({doc_word: score})
# =============================================================================

# Phase 3
# =============================================================================
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
# =============================================================================

# Phase 4
# =============================================================================
# query = tokenize(sys.argv[1])           #fetching the query terms from the command line arguments
# if len(query)%2==0:
#     query_format = zip(query[::2], query[1::2])         #building a tuple of (weight, query-term)
#     query_final = {}
#     for weight, qterm in query_format:          #Iterating through the tuple for preprocessing
#         if len(qterm) == 1 or qterm.lower() in stop_tokens:
#             pass                            #do nothing if those conditions are met because they are not needed
#         else:
#             final_qterm = qterm.lower()   
#         if len(final_qterm) > 0:    
#             query_final[final_qterm] = eval(weight)
# 
#     similar_scores = {key: 0 for key in doc_length.keys()}      #dictionay for calculating the similarity scores
#     for term, wt in query_final.items():
#         if term in tdm_dict.keys():
#             for doc in tdm_dict[term].keys():
#                 similar_scores[doc]  += tdm_dict[term][doc] * wt #dot product for obtaining the similarity score
#                 
#     final_sim_scores = {k+'.html':v for k,v in similar_scores.items() if v != 0} #using only non-zero score obtained
#     if len(final_sim_scores) > 0:
#         sorted_scores = sorted(final_sim_scores.items(), key=operator.itemgetter(1), reverse=True)      #sorting as per similarity score
#         pprint(sorted_scores[:10])      #printing only the top-10 scoring documents
#     else:
#         print("No results found")
# else:
#     print('please give arguments of the format "weight query-term"')
# =============================================================================

# Phase 5
# =============================================================================
file_list = []
for k in weight_dict.keys():
    file_list.append(k)

sim_matrix = collections.defaultdict(dict)
current_clusters = {}
cluster_info = {}

for i in range(0, len(file_list)):
    doc1 = file_list[i]
    denominator_doc1 = cos_den(doc1)
    for j in range(i, len(file_list)): #only for upper triangle
        doc2 = file_list[j]
        denominator_doc2 = cos_den(doc2)
        den = denominator_doc1 * denominator_doc2
        sim_matrix[doc1][doc2] = dot_product(doc1, doc2) / (den if den>0 else 1.0)
    current_clusters[doc1] = 1
    cluster_info[doc1] = doc1

A = [] #for storing sequence of merges

new_cluster = len(file_list) + 1 #cluster number
output = ""
while get_current_clusters() > 1: # If more than one cluster exists
    score, c1, c2 = high_sim_score() # most similar pair of clusters based on the similarity score
    if score>0.4:
        output +=  "Clustering '%s' + '%s' to get '%s' \n" %(c1, c2, new_cluster)
        A.append((c1, c2)) #storing the merge sequence
        cluster_info[new_cluster] = check_whether_document(c1) + check_whether_document(c2)
        current_clusters[new_cluster] = len(cluster_info[new_cluster])
        for or_cluster, current in current_clusters.items(): #only for current clusters
            if current != -1:
                sim_matrix[new_cluster][or_cluster] = group_link(new_cluster, or_cluster)
        new_cluster += 1
    current_clusters[c1], current_clusters[c2] = -1, -1

temp_output = output.split("\n")
cluster_file = open("cluster.txt", "w+", encoding="utf-8")
cluster_file.write('\n'.join(temp_output[:100]))
cluster_file.close()
print("Clustering Finished\nOutput stored in cluster.txt")

final_cluster = new_cluster - 1
cc_documents = cluster_info[final_cluster] #get documents present in the last cluster

m_list = [ (cos_den(file_list[document]), file_list[document]) for document in range(0, len(file_list)) ]
centroid = median(m_list)[1]
print("Centroid: " + centroid)
# =============================================================================

end = time.time()
print("Total running time: " + str(end-start))