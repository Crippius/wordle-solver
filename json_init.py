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

def get_freq(term): # Use datamuse api to find frequency x (x/1.000.000)

    response = None
    while True:
        try: # Get response
            response = requests.get('https://api.datamuse.com/words?sp='+term+'&md=f&max=1').json()
        except:
            print('Could not get response.')
            sleep(0.5)
            continue
        break

    freq = 0.0 if len(response)==0 else float(response[0]['tags'][0][2:]) # Getting frequency from dict
    
    return freq



def main():

    words_list = [] # Inserting every word in list
    with open("wordle_word_list.txt", "r") as words_file:
        word = words_file.readline()
        while word:
           words_list.append(word[:-1])
           word = words_file.readline()
        words_list.pop(-1)
        words_file.close()

    data = {} # Attention!!! Do not uncomment this code, if ran it takes > 7 hours to complete
    # with alive_bar(len(words_list)) as bar:
    #     for word in words_list:
    #         data[word] = {}
    #         data[word]["probability"] = get_freq(word)
    #         data[word]["entropy"] = find_general_entropy(word, words_list)
    #         bar()
    #     json.dump(data, fp)



if __name__ == "__main__":
    main()