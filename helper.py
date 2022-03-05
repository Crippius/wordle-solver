import json
from tkinter import *
from PIL import ImageTk, Image
from solver_v1 import update_list
from solver_v3 import all_permutations, permutations, find_entropy

def helper():

    root = Tk() # Creating main window
    root.iconbitmap("materials/duh.ico")
    root.title("Wordle Helper")
    root.resizable(False, False)

    clues = []

    languages = ["English", "Italian"] 

    image = ImageTk.PhotoImage(Image.open("materials/helper.png"))
    title = Label(root, image=image) # Adding title
    title.grid(row=0, column=0, columnspan=4, sticky=N+S+W+E)

    def character_limit(entry_text): # Used to get only one letter
        if len(entry_text.get()) > 0:
            entry_text.set(entry_text.get()[-1])

    def isalpha(letter): # Used to get only letters
        alpha = 'abcdefghijklmnopqrstuvwxyz'
        return letter in alpha
    validation = root.register(isalpha)

    letter = StringVar() # Letter insertion widgets
    letter.set(" ")
    letter_widget = Entry(root, textvariable = letter, validate='all', validatecommand=(validation, '%S'), width=3) 
    letter_widget.grid(row=3, column=0)
    letter_label = Label(root, text="LETTER:")
    letter_label.grid(row=2, column=0) 
    letter.trace("w", lambda *args: character_limit(letter))

    language = StringVar()
    language.set("English")
    language_list = OptionMenu(root, language, *languages)
    language_list.grid(row=1, column=0)

    type = IntVar() # Type insertion widgets
    type.set(0)
    isnotin_widget = Radiobutton(root, variable=type, value=0, text="Is not in word", bg="gray", height=2)
    isnotin_widget.grid(row=1, column=1, columnspan=2, sticky=N+S+W+E)
    isin_widget = Radiobutton(root, variable=type, value=1, text="Is in word", bg="yellow", height=2)
    isin_widget.grid(row=2, column=1, columnspan=2, sticky=N+S+W+E)
    iscorrect_widget = Radiobutton(root, variable=type, value=2, text="Is placed correctly", bg="green", height=2)
    iscorrect_widget.grid(row=3, column=1, columnspan=2, sticky=N+S+W+E)

    root.bind("<exclam>", lambda event: type.set(0))  # Keyboard binds for easier insertions
    root.bind("<quotedbl>", lambda event: type.set(1))
    root.bind("<sterling>", lambda event: type.set(2))

    root.bind("<Up>", lambda event: type.set((type.get()-1)%3))
    root.bind("<Down>", lambda event: type.set((type.get()+1)%3))

    pos = IntVar() # Position insertion widgets
    pos.set(0)
    one = Radiobutton(root, variable=pos, value=0, text="1st letter", height=2)
    one.grid(row=1, column=3, sticky=N+S+W+E)
    two = Radiobutton(root, variable=pos, value=1, text="2nd letter", height=2)
    two.grid(row=2, column=3, sticky=N+S+W+E)
    third = Radiobutton(root, variable=pos, value=2, text="3rd letter", height=2)
    third.grid(row=3, column=3, sticky=N+S+W+E)
    forth = Radiobutton(root, variable=pos, value=3, text="4th letter", height=2)
    forth.grid(row=4, column=3, sticky=N+S+W+E)
    forth = Radiobutton(root, variable=pos, value=4, text="5th letter", height=2)
    forth.grid(row=5, column=3, sticky=N+S+W+E)

    root.bind('1', lambda event: pos.set(0)) # Keyboard binds for easier insertions
    root.bind('2', lambda event: pos.set(1))
    root.bind('3', lambda event: pos.set(2))
    root.bind('4', lambda event: pos.set(3))
    root.bind('5', lambda event: pos.set(4))

    label_list = [] # Insertion function
    len_labels = 0
    def insert_clue():
        global pos
        global type
        global letter
        global len_labels
        global label_list

        clues.append((letter.get(), type.get(), pos.get()))
        placeholder = "" # Adding info to list of clues

        for i in range(5): # Showing feedback to user: position
            if i == pos.get():
                placeholder += "⬛"
            else:
                placeholder += "⬜"

        placeholder = f"({letter.get()}) {placeholder}" # letter feedback
        
        back = "gray" # type feedback
        if type.get() == 1:
            back = "yellow"
        elif type.get() == 2:
            back = "green"
        
        label = Label(root, text=placeholder, bg=back) # Displaying inserted letter
        label.grid(row=1+len_labels%5, column=4+len_labels//5)
        label_list.append(label)
        
        if len_labels == 0:
            Label(root, text="CLUES:").grid(row=0, column=4, columnspan=5)

        pos.set((pos.get()+1)%5)
        len_labels += 1

    insert = Button(root, text="Insert letter", command=insert_clue)
    insert.grid(row=5, column=0)

    root.bind("<space>", lambda event: insert_clue())

    def delete_clue(): # Deletion function, remove last clue
        global clues
        global label_list
        global len_labels

        if len_labels != 0:
            label_list[len_labels-1].grid_forget()
            clues.pop(-1)
            len_labels -= 1

    delete = Button(root, text="Remove clue", command=delete_clue)
    delete.grid(row=5, column=1)

    root.bind("<minus>", lambda event: delete_clue())

    def submit(): # Submit function
        global clues
        global words_list
        global language

        sub = {"english":"eng", "italian":"ita"}

        words_list = [] # Resetting list
        with open(f"word_file_{sub[language.set().lower()]}.json", "r") as words:
            words = json.load(fp)
            for word in words.keys():
                words_list.append(word)

        original = words_list
        words_list = update_list(words_list, clues) # Update list

        prob_list = []
        entropy_list = []
        with open("word_file_ita.json", "r") as fp:
            data = json.load(fp)

        if len(words_list) >= 100: # Getting probability and entropy from every word
            for word in words_list:
                prob_list.append(data[word]["probability"])
                entropy_list.append(data[word]["entropy"])
        else:
            permutations(clues)
            for word in words_list:
                prob_list.append(data[word]["probability"])
                entropy_list.append(find_entropy(all_permutations, word, words_list))
        
        prob_list = [elem for _, elem in sorted(zip(prob_list, words_list), reverse=True)]
        entropy_list = [elem for _, elem in sorted(zip(entropy_list, words_list), reverse=True)]

        results  = Toplevel()
        results.iconbitmap("materials/duh.ico")
        results.title("Results")

        label =  Label(results, text="RESULTS")
        label.grid(row=0, column=0)
        length = Label(results, text=f"{len(words_list)}/{len(original)} words")
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


        best_prob = Label(results, text=prob_text) # Widget to show results
        best_prob.grid(row=1, column=0)

        best_entropy = Label(results, text=entropy_text)
        best_entropy.grid(row=1, column=1)

        other = Label(results, text="Other words sorted by:")
        other.grid(row=2, column=0, columnspan=2) 

        prob_label = Label(results, text="Probability")
        prob_label.grid(row=3, column=0) 

        prob_label = Label(results, text="Entropy")
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

        prob_drop = OptionMenu(results, prob_word, *prob_list) # Widget with the remaining words in a list
        prob_drop.grid(row=4, column=0)
        entropy_drop = OptionMenu(results, entropy_word, *entropy_list)
        entropy_drop.grid(row=4, column=1)

    submit_btn = Button(root, text="Submit", command=submit)
    submit_btn.grid(row=5, column=2, padx=(0, 15))

    root.bind("<Return>", lambda event: submit())

    root.mainloop()



if __name__ == "__main__":
    helper()