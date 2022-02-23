# Wordle Solver
This repository contains a fun project in which I brushed up my Python skills while jumping on the "Wordle" bandwagon and learning some new libraries.

## Files
In this repo you can find the following files:

* Three versions of solvers, based on three different methods: - Random, - Entropy, - Probability
* A helper script, that can be used when stuck during the completion of the word of the day
* A json initialiser, used to find the entropy and probabilty of every word, and its product
* The list of all possible words AND answers in the game
* Some multimedia files in the 'materials' folder

## How to use the helper
Insert every clue you've got on the board, by inputting the letter in the appropiate box with its position and type of clue, then press the 'Insert letter' button.
When all clues have been pushed click the 'Submit' button, a new window will show the best possible approaches.
A 'Remove clue' button can be used to pop the last element from the list of clues.

### Key bindings
* 1 -> 5: select X position 
* shift + 1: select gray type
* shift + 2: select yellow type
* shift + 3: select  green type
* space: insert clue
* back: remove clue
* enter: submit clues
* up/down: move up and down in the type selection
  
## Upcoming possible updates
### Near future
* QoL changes
* Adding italian compatibility to helper for [Pietroppeter](https://github.com/pietroppeter)'s version of Wordle "[Parle](https://pietroppeter.github.io/wordle-it/)"
* Create a simple wordle player
* Make the solvers more interactable
### Not too near future
* Solver that considers two steps ahead
* Solver trained with machine learning (after Tensorflow course?)
* Probably a better wordle player
