import json
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from random import randint
from solver_v1 import is_placed_correctly, is_in, update_list

def player():

    languages = ["English", "Italian"] 

    root = Tk() # Creating main window
    root.iconbitmap("materials/duh.ico")
    root.title("Wordle Player")
    root.resizable(False, False)

    # TODO: create image for title
    image = ImageTk.PhotoImage(Image.open("C:/Users/cripp/Google Drive/programming/repos/wordle-solver/materials/wordle.png"))
    title = Label(root, image=image) # Adding title
    title.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
    
    lang = StringVar()
    lang.set("English")
    lang_list = OptionMenu(root, lang, *languages)
    lang_list.grid(row=1, column=1)
    lang_label = Label(root, text="Language:")
    lang_label.grid(row=1, column=0)

    def play():
        nonlocal lang

        sub = {"english":"eng", "italian":"ita"}

        with open(f"possible_answers_{sub[lang.get().lower()]}.txt", "r") as answers_file:
            len_anwers = sum(1 for _ in answers_file)
            answers_file.seek(randint(0, len_anwers*6))
            answers_file.readline()
            solution = answers_file.readline()[:-1]

        play_level = Toplevel()
        play_level.resizable(False, False)
        play_level.iconbitmap("materials/duh.ico")
        play_level.title("Crippius' Wordle")
        
        def character_limit(entry_text): # Used to get only one letter
            if len(entry_text.get()) > 0:
                entry_text.set(entry_text.get()[:5])

        def isalpha(letter): # Used to get only letters
            alpha = 'abcdefghijklmnopqrstuvwxyz'
            return letter in alpha
        validation = root.register(isalpha)

        word = StringVar() # Letter insertion widgets
        word_widget = Entry(play_level, textvariable = word, validate='all', validatecommand=(validation, '%S')) 
        word_widget.grid(row=1, column=0)
        word_widget.focus_set()
        word_label = Label(play_level, text="WORD:")
        word_label.grid(row=0, column=0) 
        word.trace("w", lambda *args: character_limit(word)),

        trames_of_clues = []
        times = 0
        def enter():
            nonlocal word
            nonlocal solution
            nonlocal times
            nonlocal trames_of_clues

            if len(word.get()) < 5:
                messagebox.showerror("ERROR", "Not enough letters")
                return
            
            with open(f"word_file_{sub[lang.get().lower()]}.json", "r") as fp:
                words = json.load(fp)
            
            if word.get() not in words:
                messagebox.showerror("ERROR", "Not a valid word")
                return
            
            word_place_count = {}
            clues = []
            for iter in range(2):
                for i in range(5):
                    if iter == 0:
                        if word.get()[i] not in word_place_count:
                            word_place_count[word.get()[i]] = 0

                        if is_placed_correctly(solution, word.get()[i], i):
                            Label(play_level, text=word.get()[i], width=4, height=2, relief="sunken", bg="green").grid(row=times, column=1+i)
                            word_place_count[word.get()[i]] += 1
                            clues.append((word.get()[i], 2, i))
                    
                    else:
                        if is_placed_correctly(solution, word.get()[i], i): # Skip, just considered it
                            continue

                        elif is_in(solution, word.get()[i]) and solution.count(word.get()[i]) > word_place_count[word.get()[i]]:
                            Label(play_level, text=word.get()[i], width=4, height=2, relief="sunken", bg="yellow").grid(row=times, column=1+i)
                            word_place_count[word.get()[i]] += 1
                            clues.append((word.get()[i], 1, i))

                        else:
                            Label(play_level, text=word.get()[i], width=4, height=2, relief="sunken", bg="gray").grid(row=times, column=1+i)
                            clues.append((word.get()[i], 0, i))

            trames_of_clues.append(clues)

            def result_screen(won):
                nonlocal trames_of_clues

                play_level.destroy()
                result = Toplevel(root)
                result.iconbitmap("materials/duh.ico")
                result.resizable(False, False)
                result.title("Results")

                if won:
                    Label(result, text="You won!!!", font=("Helvetica", 22), ).grid(row=0, column=0)
                else:
                    Label(result, text="You lost :(((", font=("Helvetica", 22), ).grid(row=0, column=0)
                
                def gtc():
                    nonlocal trames_of_clues
                    text = "Crippius' Wordle"
                    if len(trames_of_clues) <= 6:
                        text += f" {len(trames_of_clues)}/6\n"
                    else:
                        text += " X/6\n"
                        
                    colors = {0:"⬛", 1:"🟨", 2:"🟩"}
                    for clues in trames_of_clues:
                        for _, type, pos in sorted(clues, key=lambda i:i[2]):
                            text += colors[type]
                        text += "\n"
                            
                    root.clipboard_clear()
                    root.clipboard_append(text)

                    Label(result, text="Results copied to clipboard").grid(row=2, column=0)
                
                Button(result, text="Share with your friends!", command=gtc).grid(row=1, column=0)
                
            times += 1
            if word.get() == solution:
                result_screen(1)
                return
            if times == 6:
                result_screen(0)
                return

            word.set("")

        submit_btn = Button(play_level, text="Enter", command=enter)
        submit_btn.grid(row=3, column=0)

        def helper(): # Submit function
            nonlocal trames_of_clues
            nonlocal lang

            sub = {"english":"eng", "italian":"ita"}

            words_list = [] # Resetting list
            with open(f"word_file_{sub[lang.get().lower()]}.json", "r") as fp:
                data = json.load(fp)
                for word in data.keys():
                    words_list.append(word)

            original = words_list
            for clues in trames_of_clues:
                words_list = update_list(words_list, clues) # Update list

            prob_list = []
            entropy_list = []

            
            for word in words_list:
                prob_list.append(data[word]["probability"])
                entropy_list.append(data[word]["entropy"])
            
            prob_list = [elem for _, elem in sorted(zip(prob_list, words_list), reverse=True)]
            entropy_list = [elem for _, elem in sorted(zip(entropy_list, words_list), reverse=True)]
            
            if len(prob_list) == 0:
                messagebox.showerror(title="Error", message="No words found, please check if the\nclues inserted and language used are correct")
                return

            help_level = Toplevel()
            help_level.resizable(False, False)
            help_level.iconbitmap("materials/duh.ico")
            help_level.title("Results")

            label =  Label(help_level, text="RESULTS")
            label.grid(row=0, column=0)
            length = Label(help_level, text=f"{len(words_list)}/{len(original)} words")
            length.grid(row=0, column=1)

            if len(words_list) == 0: # Text based on number of words
                prob_text = "No words possible"
                entropy_text = "No words possible"
            elif len(words_list) == 1:
                prob_text = f"Most probable words:\n 1. {prob_list[0]}"
                entropy_text = f"Most efficient words:\n 1. {entropy_list[0]}"
            elif len(words_list) == 2:
                prob_text = f"Most probable words:\n 1. {prob_list[0]}\n 2. {prob_list[1]}"
                entropy_text = f"Most efficient words:\n 1. {entropy_list[0]}\n 2. {entropy_list[1]}"
            else:
                prob_text = f"Most probable words:\n 1. {prob_list[0]}\n 2. {prob_list[1]}\n 3. {prob_list[2]}"
                entropy_text = f"Most efficient words:\n 1. {entropy_list[0]}\n 2. {entropy_list[1]}\n 3. {entropy_list[2]}"

            best_prob = Label(help_level, text=prob_text) # Widget to show results
            best_prob.grid(row=1, column=0)

            best_entropy = Label(help_level, text=entropy_text)
            best_entropy.grid(row=1, column=1)

            other = Label(help_level, text="Other words sorted by:")
            other.grid(row=2, column=0, columnspan=2) 

            prob_label = Label(help_level, text="Probability")
            prob_label.grid(row=3, column=0) 

            prob_label = Label(help_level, text="Entropy")
            prob_label.grid(row=3, column=1) 

            prob_word = StringVar()
            entropy_word = StringVar()
            
            if len(words_list) == 0:
                pass
            elif len(words_list) > 3:
                prob_word.set(prob_list[3])
                entropy_word.set(entropy_list[3])
            else:
                prob_word.set(prob_list[0])
                entropy_word.set(entropy_list[0])

            if len(prob_list) != 0:
                prob_drop = OptionMenu(help_level, prob_word, *prob_list) # Widget with the remaining words in a list
                prob_drop.grid(row=4, column=0)
                entropy_drop = OptionMenu(help_level, entropy_word, *entropy_list)
                entropy_drop.grid(row=4, column=1)

        help_btn = Button(play_level, text="Need some help?", command=helper)
        help_btn.grid(row=4, column=0)

        for i in range(6):
            for j in range(5):
                Label(play_level, text="", width=4, height=2, borderwidth=2, relief="sunken", bg="white").grid(row=i, column=1+j)


    start = Button(root, text="Start playing!", width=10, height=3, font=("Helvetica", 22), command=play)
    start.grid(row=2, column=0, columnspan=2, pady=(20, 0))

    
    root.mainloop()



if __name__ == "__main__":
    player()