import json
import requests
from math import log2
from time import sleep
from alive_progress import alive_bar
from solver_v1 import is_in, is_placed_correctly

all_permutations = [] # ex. [🟨, 🟩, ⬛, 🟨, 🟩]

def initial_permutations(n=5, lst=[]): # Appending to list every possible permutation
    if n == 0:
        all_permutations.append(lst)
    else:
        initial_permutations(n-1, [0]+lst)
        initial_permutations(n-1, [1]+lst)

def find_general_entropy(word, words_list): # Finds entropy for word given every possible permutation
    global all_permutations
    length = len(words_list)
    entropy = 0

    for perm in all_permutations:
        possibilities = 0
        for other_word in words_list:
            check = 1
            for info in range(0, len(perm)): # Checking how many words can be found given every permutation
                if perm[info] == 0:
                    if is_in(other_word, word[info]):
                        check = 0
                        break
                elif perm[info] == 1:
                    if not (is_in(other_word, word[info]) and not is_placed_correctly(other_word, word[info], info)):
                        check = 0
                        break
                else:
                    if not is_placed_correctly(other_word, word[info], info):
                        check = 0
                        break
            if check:
                possibilities += 1

        p = possibilities/length

        if p != 0:
            entropy -= p * log2(p) # entropy = - sum(p(x)*log2(p(x)))
    
    return entropy

def get_prob(term, lang): # Use google ngram's site to find frequency of a particular word

    corpus = {"english":0, "italian":33} # For every language there is a different corpus

    param = {"content":term, "corpus":corpus[lang], "smoothing":0} # Parameters for the search

    reset = 1
    while True:
        r = requests.get(url="https://books.google.com/ngrams/graph", params=param) # Getting request
        
        if r.text == "Please try again later.": # If server is overloaded, ,wait a little
            reset += 1
            print('Could not get response.')
            sleep(2*reset)
            continue
        
        break

    r = str(r.text) # Find data
    r = r[r.find("ngrams.data")+15:]
    r = r[:r.find("}")+1]
    
    if r[:2] == "];": # No data found
        return 0

    freq = float(eval(r)["timeseries"][-1])*100 # Got data, get last datapoint
    
    return freq



def main():
    
    initial_permutations()

    sub = {"english":"eng", "italian":"ita"}
    
    languages = ["english", "italian"] # ["english", "italian"] 

    for lang in languages:
        words_list = [] # Inserting every word in list
        with open(f"word_list_{sub[lang]}.txt", "r") as words_file:
            word = words_file.readline()
            while word:
                words_list.append(word[:-1])
                word = words_file.readline()
            words_file.close()

        data = {} # Attention!!! Do not uncomment this code, if ran it takes > 12 hours per language to complete
                  # because of heavy calculations (and overworking google's ngram)
    
        with alive_bar(len(words_list)) as bar: # Getting the probability and the entropy of every word
            for word in words_list:
                data[word] = {}
                data[word]["probability"] = get_prob(word, lang)
                data[word]["entropy"] = find_general_entropy(word, words_list)
                print(word, data[word]["probability"], data[word]["entropy"])
                bar()
          
        with open(f"word_file_{sub[lang]}.json", "w") as fp: # Dumping it into json file
            json.dump(data, fp)



if __name__ == "__main__":
    main()