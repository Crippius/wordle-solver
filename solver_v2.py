# Version 2.0, Entropy
# This program makes weighted choices from the list of words, picking the one that has the most entropy: the one that has on average
# the highest chance to reduce the number of words in the list.
# EX: the word 'wonky' reduces significantly the number of words in the lists if one or more unusual letters like 'w', 'k', 'y' are found
# but if these letters are not in the final word, the number of words in the list are still high, and a round is 'wasted'.
# For this dataset the word with the highest entropy is 'tares', when no letter is in the word, you still receive a lot of information,
# since these letters are found in a lot of words, so a lot of words will be removed from the list.
# The program will always choose 'tares' first, then it will choose the next word with the highest entropy given all the remaining
# words and possible permutations, until the final word is found.
#
# Time to run 100 tries: about 2 minutes (It takes more time for a more 'though out' solution)
# Results: 95% Win-rate after six tries
# In average it takes 4.3 tries to find the solution
# Approx. plot
#
#                  #     
#                  #    
#                  #    
#                  #     
#                  #    #   
#                  #    #   
#             #    #    #      
#             #    #    #   #   
#             #    #    #   #   #
# ---------------------------------
#   1    2    3    4    5   6   7+
#
# x-axis: number of tries before winning

import os
import json
from math import log2
from random import randint
from matplotlib.pyplot import show, bar
from alive_progress import alive_bar
from solver_v1 import find_clues, update_list, is_placed_correctly, is_in

def find_entropy(permutations, word, words_list): # Finds entropy of a given word
    length = len(words_list)
    entropy = 0

    for perm in permutations: # Iterating every permutation possible
        possibilities = 0
        for other_word in words_list: # Checking the number of words that would have been found given the permutation
            check = 1
            for info in range(0, len(perm)):
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

all_permutations = [] # ex. [🟨, 🟩, ⬛, 🟨, 🟩]

def permutations(clues, n=5, lst=[]): # Recursive function to find all permutations
    global all_permutations
    
    if n==0: # Base case: no remaining steps, add it to list
        all_permutations.append(lst)
    
    else: # Default case: has more steps to do, try all possibilities
        
        check = 1 # Checking if a 🟩 is in this position
        for clue in clues:
            if clue[1] == 2 and clue[2] == 5-n:
                check = 0
        
        if check: # If we know that in a given position there's a certain letter, only 🟩 can be placed
            permutations(clues, n-1, lst+[0])
            permutations(clues, n-1, lst+[1])
        permutations(clues, n-1, lst+[2]) 

def solver_v2(solution, lang="english", other_info=False):

    global all_permutations

    sub = {"english":"eng", "italian":"ita"}
    
    words_list = [] # Inserting in list every possible word
    with open(f"word_file_{sub[lang]}.json", "r") as fp:
        words = json.load(fp)
        max = -1
        max_word = ""
        for word in words.keys():
            words_list.append(word)
            if words[word]["entropy"] > max: # And finding the most efficient word in the meantime
                max = words[word]["entropy"]
                max_word = word
    
    word = max_word
    text = ""
    used_words = [word]

    if word == solution: # If solution == tares
        # YOU WON!!!
        text += "🟩🟩🟩🟩🟩\n" # YOU DID IT!!!
        for i in range(5):
            text += "...\n" # Filling last rows...
    
    else:
        clues = sorted(find_clues(word, solution), key=lambda i:i[1], reverse=True)
        words_list = update_list(words_list, clues) # Updating list of words

        for i in range(1, 6):
            for let, type, pos in sorted(clues, key=lambda i:i[2]):
                if type == 0: # Providing feedback
                    text += "⬛"
                elif type == 1:
                    text += "🟨"
                else:
                    text += "🟩"
            text += "\n"


            max = -1 # Resetting variables
            all_permutations = []
            permutations(clues)

            if len(words_list) > 100: # Time optimisation: Consider only a local point of list
                sub = randint(100, len(words_list))
                compressed_list = words_list[sub-100:sub]
            else:
                compressed_list = words_list

            for other_word in compressed_list: # Find word with the highest entropy locally
                entropy = find_entropy(all_permutations, other_word, compressed_list)
                if max < entropy:
                    word = other_word
                    max = entropy
        
            used_words.append(word)

            if word == solution: # If the word is correct, it won
                # YOU WON!!!
                score = i+1
                text += "🟩🟩🟩🟩🟩\n" # YEEEAAHHH
                for j in range(6-score):
                    text += "...\n"
                break
            
            clues = sorted(find_clues(word, solution), key=lambda i:i[1], reverse=True) # If it is not, give new clues
            words_list = update_list(words_list, clues) # Updating list of words

        if word != solution:
            # YOU LOST :'''(
            score = 7
            text = text[:-1] + " ❌❌❌" # Oops
    
    if other_info:
        return score, text, used_words
    return score
    

if __name__ == "__main__":

    sub = {"english":"eng", "italian":"ita"}
    lang = "english"

    with open(f"possible_answers_{sub[lang]}.txt", "r") as answers_file: # Getting number of possible answers
        len_anwers = sum(1 for _ in answers_file)

    won = 0
    gen = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    times = 100
    mean = 0
    with alive_bar(times) as load_bar: # Using loading bar
        for _ in range(times):
            with open(f"possible_answers_{sub[lang]}.txt", "r") as answers_file: # Get a random answer
                    answers_file.seek(randint(0, len_anwers*6))
                    answers_file.readline()
                    solution = answers_file.readline()[:-1]
            score, text, used_words = solver_v2(solution, lang, True)
            
            if score != 7:
                won += 1
            gen[score] += 1

            mean += score
            os.system('cls')     
            print("\n".join([ # Print info about current round
                f"Score: {score}",
                f"Words used: {used_words}",
                f"Running average: {round(mean/(_+1), 2)}",
                f"Running win-rate: {round(100*won/(_+1), 2)}%"
                " ",
                text]))

            load_bar() # Updating loading bar

    print(f"Win-rate: {won/times}") # Showing results
    print(f"Results: {gen}")
    print(f"Average number of tries: {mean/times}")

    bar(gen.keys(), gen.values())
    show() # Plotting results