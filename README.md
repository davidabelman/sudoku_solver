Python Su Doku Solver
=====================

Note this appears to work on most Su Doku's, but not the 'Super Fiendish' ones published occasionally by The Times. Maybe you can improve! A brief blog post explaining can be found at https://davidabelman.wordpress.com/2015/03/03/su-doku-challenge/.

Running overview
-----------
Running is simple. Input Su Doku must be saved as a CSV in the same folder as the script. Output CSV will also be saved here.

In the terminal, type:
>> python sudoku.py

Optional argument is the name of the CSV file, though if this is not provided you will be prompted to provide it later.

Nine boards are supplied within this repo (from The Times).

How it works
-----------
- A Board object is created
- A board configuration can be loaded into the Board object: this loads a CSV file into initial_array variable
- For each of the 81 spaces on the Su Doku board, we instantiate a Cell object, and these are added to the Board's cell_array variable.
- Each of these Cell objects have 3 variables describing their position in the board (row, column block), as well as a 'final' variable (equal to None unless the cell has been filled in, at which point it becomes the final value) and an 'options' variable, which is an array of the remaining options for this cell.
- The board has methods to create temporary arrays of 9 cells (either rows, columns or blocks). These are used when trying to fill in the board.
- The board has a 'simple_solver' function, which repeatedly tries two methods of solving the board. Both of these use logic and don't require guessing. At every stage, we check to see if the board is complete - if so, the board will print results to screen and file. If we reach an impasse where the board is valid but no headway can be made with our two methods of solving, the function returns False (the board is kept in its latest state).
- The board has a 'split_and_guess' method, which duplicates the board into multiple copies. Each copy has a different guess for a specific cell (supplied as an argument to 'split_and_guess'). Once the board is split into these various copies, each of these will try and be solved using the 'simple_solver' method, until once again, they reach an impasse. At this point, if the board is invalid, we reject the latest guess, or if the board is still valid but we need to guess again, we recursively call 'split_and_guess' on this latest board configuration.
- The board has a high level 'solve_board' function, which attempts to solve using 'simple_solver', but if this is not successful, calls the 'split_and_guess' method, which should eventually find the solution.
- Once the solution is found, a 'clean_up' method is called. This displays how long the board took to solve, which methods were used to solve it (these are stored on a cell by cell basis within a cell variable), and prints the completed board to screen and CSV, and exits.

*Note that I have found two 'Super-Fiendish' puzzles which this script fails to solve. I have not debugged to work out why!*