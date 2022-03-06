# Version 3.0, Frequency
# While trying to find the best word to minimize the choices is a good strategy, there comes a point where the best play is to choose
# the most probable between the remaining, to finally finish the game; this version of the solver in fact after a certain threshold
# stops choosing the 'most efficient' word and tries to find the 'most probable' one.
#
# Time to run 100 tries: about 1 minute and 30 seconds
# Results: 99% Win-rate after six tries
# In average it takes 3.9 tries to find the solution
# Approx. plot
#
#                       
#                  #    
#                  #    
#             #    #     
#             #    #    #   
#             #    #    #   
#             #    #    #      
#             #    #    #      
#        #    #    #    #   #   
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

def update_list(word_list, clues): # Remove from list every string that doesn't follow new clues
    new_list = []
    for word in word_list:
        check = 1  # If word doesn't follow every rule, then check = 0
        for clue in clues: 
            if clue[1] == 0: # (Check 'find_clues' function to see how clues are structured)
                if is_in(word, clue[0]): # ⬛
                    check = 0
                    break
            elif clue[1] == 1: # 🟨
                if is_placed_correctly(word, clue[0], clue[2]) or not is_in(word, clue[0]):
                    check = 0
                    break
            else: # 🟩
                if not is_placed_correctly(word, clue[0], clue[2]):
                    check = 0
                    break
        
        if check: # If check = 1, word could be an answer, and is insterted in list
            new_list.append(word)

    return new_list

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

def find_clues(word, solution): # Give the user clues given the word
    clues = []
    for i in range(len(word)):
        if is_placed_correctly(solution, word[i], i): # 🟩
            clues.append((word[i], 2, i)) 
        elif is_in(solution, word[i]): # 🟨
            clues.append((word[i], 1, i))
        else:
            clues.append((word[i], 0, -1)) # ⬛
    
    return clues # Structure of clue (letter, type of clue (🟩, 🟨, ⬛), position)

def is_placed_correctly(word, s, pos):
    return word[pos] == s

def is_in(word, s):
    return s in word



def solver_v3(solution, lang, other_info=False):

    global all_permutations
    
    sub = {"english":"eng", "italian":"ita"}

    with open(f"possible_answers_{sub[lang]}.txt", "r") as answers_file: # Getting number of possible answers
        len_anwers = sum(1 for _ in answers_file)

    words_list = [] # Inserting in list every possible word
    with open(f"word_file_{sub[lang]}.json", "r") as fp:
        data = json.load(fp) # (Using this dict for later)
        words = data
        max = -1
        max_word = ""
        for word in data.keys():
            words_list.append(word)
            if words[word]["entropy"] > max: # And finding the most efficient word in the meantime
                max = words[word]["entropy"]
                max_word = word
    
    word = max_word

    text = ""
    used_words = [word]

    if word == solution: # If solution == tares
        # YOU WON!!!
        text += "🟩🟩🟩🟩🟩\n" # Congrats!!!
        for j in range(5):
            text += "...\n" # Filling last rows...

    else:
        clues = find_clues(word, solution) 
        words_list = update_list(words_list, clues) # Updating list of words

        for i in range(1, 6):
            for let, type, pos in clues[-5:]:
                if type == 0: # Giving feedback with squares
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
                for other_word in words_list[sub-100:sub]: # Find word with the highest entropy locally
                    entropy = find_entropy(all_permutations, other_word, words_list[sub-100:sub])
                    if max < entropy:
                        word = other_word
                        max = entropy
            else:
                most_probable = ""
                max_prob = -1
                    
                for other_word in words_list:
                    if data[other_word]["probability"] > max_prob:
                        word = other_word
                        max_prob = data[word]["probability"]

            used_words.append(word)

            if word == solution: # If the word is correct, it won
                # YOU WON!!!
                score = i+1
                text += "🟩🟩🟩🟩🟩\n" # Nice!!!
                for j in range(6-score):
                    text += "...\n"

                break
            
            clues += find_clues(word, solution) # If it is not, give new clues
            words_list = update_list(words_list, clues) # Updating list of words

        if word != solution:
            # YOU LOST :'''(
            score = 7
            text = text[:-1] + " ❌❌❌"
    
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
            score, text, used_words = solver_v3(solution, lang, True)
            
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