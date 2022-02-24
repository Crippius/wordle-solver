# Version 1.0, Random
# This program chooses a random word from a list of possible solutions, if the word is not correct it takes all the clues given,
# reduces the list of possible words and retries (randomly)
#
# Time to run 100 tries: about 15 seconds
# Results: 90% Win-rate after six tries
# In average it takes 4.85 tries to find the solution
# Approx. plot
#
#                       #
#                  #    #
#                  #    #
#                  #    # 
#                  #    #   #
#                  #    #   #
#             #    #    #   #   #
#             #    #    #   #   #
#        #    #    #    #   #   #
# ---------------------------------
#   1    2    3    4    5   6   7+
#
# x-axis: number of tries before winning

import os
from time import sleep
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

       

def main():

    words_list = [] # Insert in list every word in file
    with open("wordle_word_list.txt", "r") as words_file:
        word = words_file.readline()
        while word:
           words_list.append(word[:-1])
           word = words_file.readline()
        words_list.pop(-1)
        words_file.close()
        
    with open("wordle_possible_answers.txt", "r") as answers_file: # Getting number of possible answers
        len_anwers = sum(1 for _ in answers_file)

    won = 0
    gen = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    times = 100
    original = words_list
    text = ""
    mean = 0
    with alive_bar(times) as load_bar: # Using loading bar
        for _ in range(times):
            text = ""
            used_words = []
            words_list = original # Resetting list

            with open("wordle_possible_answers.txt", "r") as answers_file: # Get a random answer
                answers_file.seek(randint(0, len_anwers*6))
                answers_file.readline()
                solution = answers_file.readline()[:-1]
                
            for i in range(6): # Play the game for six rounds, if the program doesn't find the word in these six rounds it loses
                    
                word = words_list[randint(0, len(words_list)-1)] # Uses random (possible) word
                used_words.append(word)

                if word == solution: # If the word is correct, it won
                    # YOU WON!!!
                    score = i+1
                    gen[score] += 1
                    won += 1
                    text += "🟩🟩🟩🟩🟩\n" # Completed!
                    for j in range(6-score): # Filling last rows with ...
                        text += "...\n"
                    break

                clues = find_clues(word, solution) # If it is not, give clues
                for let, type, pos in clues: # Visualizing feedback
                    if type == 0:
                        text += "⬛"
                    elif type == 1:
                        text += "🟨"
                    else:
                        text += "🟩"
                text += "\n"
                words_list = update_list(words_list, clues) # Updating list of words

            if word != solution:
                # YOU LOST :'''(
                score = 7
                gen[7] += 1
                text = text[:-1] + " ❌❌❌" # <- You lost big time!!!
            
            mean += score
            os.system('cls')     
            print("\n".join([ # Print info about current round
                f"Score: {score}",
                f"Words used: {used_words}",
                f"Running average: {round(mean/(_+1), 2)}",
                f"Running win-rate: {round(100*won/(_+1), 2)}%"
                " ",
                text]))
            
            sleep(0.1)
            load_bar() # Updating loading bar

    print(f"Win-rate: {round(100*(won/times), 2)}") # Showing results
    print(f"Results: {gen}")
    print(f"Average number of tries: {round(mean/times, 2)}")


    bar(gen.keys(), gen.values())
    show() # Plotting reslults
    

    
if __name__ == "__main__":
    main()


