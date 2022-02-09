# Program that finds the word with the highest entropy in the list and writes it in a file
# Since initially there are 12972 words and 243 possible combinations for every word
# it takes a lot of time to find the entropy of every word (1.5 seconds per word)
# 1.5 * 12972 / 3600 = 5.5 hours to complete
# 12972^2 * 3^5 = 4*10^10 checks done

from math import log2
from solver_v1 import is_in, is_placed_correctly

all_permutations = [] # ex. [🟨, 🟩, ⬛, 🟨, 🟩]

def initial_permutations(n=5, lst=[]): # Appending to list every possible permutation
    if n == 0:
        all_permutations.append(lst)
    else:
        initial_permutations(n-1, [0]+lst)
        initial_permutations(n-1, [1]+lst)
        initial_permutations(n-1, [2]+lst)

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

def main():
    global all_permutations
    words_list = [] # Inserting every word in list
    with open("wordle_word_list.txt", "r") as words_file:
        word = words_file.readline()
        while word:
           words_list.append(word[:-1])
           word = words_file.readline()
        words_list.pop(-1)
        words_file.close()

    initial_permutations()
    # Commented last part to avoid 5.5 hour program that resets 'entropy_list.txt', DO NOT UNCOMMENT

    # with open("entropy_list.txt", "w") as entropy_file:
    #     for word in words_list: # Finding entropy for every word and writing it into 'entropy_list.txt'
    #         entropy_file.write(f"{word} {find_general_entropy(word, words_list)}\n")



if __name__ == "__main__":
    main()