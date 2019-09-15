import html2text                   #to convert html to text format
import time

hyper = html2text.HTML2Text()
hyper.ignore_links = True          #ignoring the urls to external documents

from os import listdir
from os.path import isfile, join

#from collections import Counter

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

onlyfiles = [f for f in listdir("../files") if isfile(join("../files", f))]
start = time.time()

for i in onlyfiles:
    with open("../files/"+i, "r", encoding="ISO-8859-1") as o_file:     #opening a html file, so keeping the encoding as ISO-8859-1
        file_data = o_file.read()
    
    html_text = hyper.handle(file_data)                      #converting the htmls to text files
    tokenizer = tokenize(html_text)             #calling the method
    f_name = i.split('.')
    f_text = open("txt_files/"+f_name[0]+".txt", "w+", encoding="utf-8")        #storing the text files, keeping the encoding as utf-8
    for lm in range(0, len(tokenizer)):
        f_text.write(tokenizer[lm] + "\n")          #writing the tokens to a text files
    f_text.close()

end = time.time()
print("Total time for conversion of html to txt:", (end-start), "seconds")

start_second = time.time()
tokenfiles = [f for f in listdir("txt_files") if isfile(join("txt_files", f))]

read_tokens=""
for file in tokenfiles:
    with open("txt_files/" + file, "r", encoding="utf-8") as in_file:       #Reading the tokens which were stored previuosly
        read_tokens += in_file.read()

retokenize = tokenize(read_tokens)
word_map=create_map(retokenize)       #create frequency distribution for all tokens stored in 'retokenize'
#word_map = Counter(retokenize)
sort_map_token = sorted(word_map.items(), key=lambda kv: kv[0])        #sorting using the alphabets
sort_map_freq = sorted(word_map.items(), key=lambda kv: kv[1], reverse=True)       #sorting using the frequency
end_second = time.time()
print("Total time for final tokenization of all files with frequency: ", (end_second-start_second), "seconds")

final_file_token = open("all_tokens_token.txt", "w+", encoding="utf-8")
for i in range(len(sort_map_token)):    
    final_file_token.write(sort_map_token[i][0] + " - " + str(sort_map_token[i][1]) + "\n")    #storing all tokens in a file sorted alphabetically
final_file_token.close()

final_file_freq = open("all_tokens_freq.txt", "w+", encoding="utf-8")
for i in range(len(sort_map_freq)):    
    final_file_freq.write(sort_map_freq[i][0] + " - " + str(sort_map_freq[i][1]) + "\n")       #storing all tokens in a file sorted by frequency
final_file_freq.close()

fifty_file_token = open("fifty_tokens_token.txt", "w+", encoding="utf-8")      #storing the first fifty and last fifty tokens alphabetically
fifty_file_token.write("----------------First 50 lines----------------\n")
for i in range(0, 50):    
    fifty_file_token.write(sort_map_token[i][0] + " - " + str(sort_map_token[i][1]) + "\n")
fifty_file_token.write("----------------Last 50 lines----------------\n")    
last_token = len(sort_map_token) - 50
for i in range(last_token, len(sort_map_token)):    
    fifty_file_token.write(sort_map_token[i][0] + " - " + str(sort_map_token[i][1]) + "\n")
fifty_file_token.close()

fifty_file_freq = open("fifty_tokens_freq.txt", "w+", encoding="utf-8")        #storing the first fifty and last fifty token by frequency sort
fifty_file_freq.write("----------------First 50 lines----------------\n")
for i in range(0, 50):    
    fifty_file_freq.write(sort_map_freq[i][0] + " - " + str(sort_map_freq[i][1]) + "\n")
fifty_file_freq.write("----------------Last 50 lines----------------\n")    
last_freq = len(sort_map_freq) - 50
for i in range(last_freq, len(sort_map_freq)):    
    fifty_file_freq.write(sort_map_freq[i][0] + " - " + str(sort_map_freq[i][1]) + "\n")
fifty_file_freq.close()