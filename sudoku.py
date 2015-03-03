import sys
import time
import copy

class Board:

	def __init__(self):
		self.board_loaded = False
		self.initial_array = []
		self.cell_array = []
		self.filename = None
		self.time_start = None
		self.time_end = None
		self.board_complete = False

	def solve_board(self):
		"""
		Solves whichever board is currently loaded
		"""
		if not self.board_loaded:
			print "Error: no board loaded"
			return False

		# Start the timer
		self.time_start = time.time()

		# Attempt with the simple solver first (no guessing)
		finished = self.simple_solver()

		# If not finished, the simple logic didn't work, we will need to make a guess
		if not finished:
			# Find a cell with lowest number of options for us to guess
			index_of_cell_to_guess = self.locate_minimal_options_cell()
			# Call a recursive function, creates copies of the object with each guess
			# This function quits the program when a solution is found, else does nothing
			self.split_and_guess(index_of_cell_to_guess)

		# If we have reached here, the puzzle has not been solved and will exit
		print "It has not been possible to solve this SuDoku!"
		self.time_end = time.time()
		total_time_taken = self.time_end - self.time_start
		print "Time taken: {:.2f} seconds".format(total_time_taken)
		print "Exiting."
		sys.exit()
		
	def simple_solver(self):
		"""
		Attempts to solve with 2 simple elimination techniques (no guessing).
		Loops through until no changes are made using either method. 
		Returns False when done as much as possible, or terminates when board complete.
		"""
		# Keeps track of if the board has seen any changes (if no progress for long time, we will need to guess a square)
		no_change_counter = 0

		# Keep looping until finished or until no progress made
		while True:

			# Try striking options out
			while no_change_counter==0:
				if self.strike_options_all():
					
					# Change in board, so reset counter
					no_change_counter = 0  

					# Check if solved and wrap up if so
					if self.check_board_solved():
						self.clean_up()

				else:
					# No progress made
					no_change_counter +=1

			# Try process of elimination
			if self.select_only_remaining_option_all():

				# Change in board, so reset counter
				no_change_counter = 0  

				# Check if solved and wrap up if so
				if self.check_board_solved():
					self.clean_up()

			else:
				# No progress made
				no_change_counter +=1
			
			# If no change in either, return False
			if no_change_counter >= 2:
				return False

	def split_and_guess(self, index_of_cell_to_guess):
		"""
		Takes current board and chooses a cell to guess. 
		Splits the board into N versions, each with a different guess at this cell.
		Recursively calls itself until solution found.
		"""		
		# Repeat for each potential option		
		for option in self.cell_array[index_of_cell_to_guess].options:

			# Create copy of the board and insert the trial value
			duplicate_B = copy.deepcopy(self)
			duplicate_B.cell_array[index_of_cell_to_guess].finalise_cell(option)
			
			# Mark this as a guess
			duplicate_B.cell_array[index_of_cell_to_guess].filled = 'Guess'
			
			if debug:
				print "Added to board by guessing:"
				duplicate_B.print_board_to_screen()
				print
			
			# Run the simple solver again to see if we can complete			
			finished = duplicate_B.simple_solver()
			
			if not finished:
				# Couldn't complete simply - try guessing another cell, recursively
				index_of_cell_to_guess = duplicate_B.locate_minimal_options_cell()
				duplicate_B.split_and_guess(index_of_cell_to_guess)
		
	def locate_minimal_options_cell(self):
		"""
		Loops through all cells in object, finds index of one with minimal number of options remaining
		Returns the index of this cell.
		"""
		minimal_number_of_options = 10  # Should always be less than this
		minimal_index = None  # Index of the minimal option cell

		# Loop through cells
		for index in range(len(self.cell_array)):
			cell = self.cell_array[index]
			if cell.final:
				# Ignore cell if already filled
				continue
			# Assess how many options left - we are looking for cells with few options
			number_of_options = len(cell.options)
			if number_of_options < minimal_number_of_options:
				# If fewest seen so far, keep track of this
				minimal_number_of_options = number_of_options
				minimal_index = index
		return minimal_index

	def csv_to_array(self, filename):
		"""
		Given filename, converts 9x9 squares into Python array
		"""
		try:
			f = open(filename, 'r')
		except:
			print "{} is not a valid filename - please try again.".format(filename)
			sys.exit()
		self.filename = filename
		data = f.readlines()
		lines = [x.replace('\n','').split(',') for x in data]
		output = []
		for line in lines:
			for cell in line:
				if cell == '':
					output.append(None)
				else:
					output.append(int(cell))
		return output

	def load_board(self, filename):
		"""
		Loads board from csv file, deletes all previous workings
		"""
		self.initial_array = self.csv_to_array(filename)
		count = 0
		for entry in self.initial_array:
			row_number = count/9  # Integer division, will be 0-8
			col_number = count%9
			block_number = self.lookup_block_number(row_number, col_number)
			cell = Cell(entry, row_number, col_number, block_number)
			self.cell_array.append(cell)
			count += 1
		self.board_loaded = True

	def lookup_block_number(self, row_number, col_number):
		"""
		Given a row number and a col number, look up a block number, return it
		"""
		if row_number <= 2 and col_number <= 2:
			return 0
		if row_number <= 2 and col_number <= 5:
			return 1
		if row_number <= 2 and col_number <= 8:
			return 2
		if row_number <= 5 and col_number <= 2:
			return 3
		if row_number <= 5 and col_number <= 5:
			return 4
		if row_number <= 5 and col_number <= 8:
			return 5
		if row_number <= 8 and col_number <= 2:
			return 6
		if row_number <= 8 and col_number <= 5:
			return 7
		if row_number <= 8 and col_number <= 8:
			return 8

	def get_row(self, row_number):
		"""
		Returns list of cells in a certain row
		"""
		return self.get_9_cells(row_number, 'row')

	def get_col(self, col_number):
		"""
		Returns list of cells in a certain col
		"""
		return self.get_9_cells(col_number, 'col')

	def get_block(self, block_number):
		"""
		Returns list of cells in a certain block
		"""
		return self.get_9_cells(block_number, 'block')

	def get_9_cells(self, index, cell_collection_type):
		"""
		Helper function, cell_collection_type must be one of row, col, block
		"""
		out = []
		for cell in self.cell_array:
			if cell.get_index(cell_collection_type) == index:
				out.append(cell)
		return out

	def print_board_to_screen(self):
		"""
		Print current board to screen (note Terminal may need to be zoomed out to see properly)
		"""
		for index in range(len(self.cell_array)):
			if index%3==100:
				print self.cell_array[index].string_rep()
			else:
				print self.cell_array[index].string_rep(),
			if index%9==8:
				print "\n"

	def strike_options_all(self):
		"""
		Iterate through all cells, striking off any options not available because of other cells
		
		Return True if some cell on the board was finalised along the way (i.e. filled in)
		"""
		# Keep track to see if any material change on the board
		some_cell_finalised = False

		# Go through all cells and try to strike things off
		for cell in self.cell_array:
			# Considering just an individual cell
			_ = self.strike_options(cell)
			if _==True:
				some_cell_finalised = True	# Keeping track of change on the board

		return some_cell_finalised  # True/False depending if change on the board

	def strike_options(self, cell):
		"""
		Given a single cell, if it has a final value in it, remove final value from other relevant cells' options
		Return True if a cell was finalised along the way
		"""
		# Keep track to see if any material change on the board
		some_cell_finalised = False

		# If cell doesn't have a final value, we can't strike any options from other cells
		if not cell.final:
			return False

		# However, if cell does have a final value, get its row, col and block coordinates
		value_to_strike = cell.final
		strike_row, strike_col, strike_block = cell.row, cell.col, cell.block

		# Strike options from other cells in row, column and block in turn
		for (index, fn) in [( strike_row , self.get_row ),
							( strike_col , self.get_col ),
							( strike_block , self.get_block ) ]:

			strike_array = fn(index)  # An array of cells (either col, row or block)
			for other_cell in strike_array:
				# Attempt to remove option (i.e. if it exists)
				# Return True/False depending if option was removed
				option_removed = other_cell.remove_option(value_to_strike)  
				
				# If the option was removed, check to see if cell has only one option remaining
				if option_removed:
					if len(other_cell.options)==1:
						# Yes, just one option left...
						proposed_value = other_cell.options[0]
						# Check for any conflicts before assigning cell
						conflict = self.check_for_conflicts(other_cell, proposed_value)	
						if not conflict:
							other_cell.finalise_cell(proposed_value)
							other_cell.filled = 'Strike'
							some_cell_finalised = True

							if debug:
								print "Added to board by strike-out:"
								self.print_board_to_screen()
								print

		return some_cell_finalised  # True/False depending if change on the board

	def select_only_remaining_option_all(self):
		"""
		Iterate through each row and column and block, checking for 'singular' options
		Return True if some cell is finalised along the way.
		"""
		# Keep track to see if any material change on the board
		some_cell_finalised = False

		# For all 9 rows, columns and blocks, look for any singular remaining options
		for fn in (self.get_row, self.get_col, self.get_block):
			for index in range(9):
				array = fn(index)
				_ = self.select_only_remaining_option(array)
				# If material change on the board, keep track of it
				if _ == True:
					some_cell_finalised = True

		return some_cell_finalised # True/False depending if change on the board

	def select_only_remaining_option(self, array):
		"""
		Given an array (either row, col or block), finalises an option in a cell that appears only once in the options lists.
		E.g. 3 cells, may have options [5,7], [5,7], [5,7,8] --> third one must be 8
		Return True if a cell was finalised along the way
		"""
		# Keep track of if something is finalised
		some_cell_finalised = False

		# Preparation
		already_finalised = []
		option_tracker = {}

		# Loop through all cells in the array keeping track of options
		for cell in array:
			# Keep track of options already out of the reckoning, to exclude later
			if cell.final:
				# I.e. this cell already has this number as its finalised value
				already_finalised.append(cell.final)
				continue

			# Add any options to the option tracker, along with reference to the cell
			for option in cell.options:
				# Don't include any values already finalised in the array
				if option in already_finalised:
					cell.options.remove(option) # Remove it as an option generally
					continue
				# If it's the first time we've come across this option create new list of length 1
				if option not in option_tracker:
					option_tracker[option] = [cell]
				# If we've already come across it, append the cell to the list of cells with this option
				else:
					option_tracker[option].append(cell)

		# Now check through the option tracker to find values with only one viable cell in their list
		for option in option_tracker:
			if len(option_tracker[option])==1:
				# This is the only place this option can go within the array
				cell = option_tracker[option][0]

				# Let's finalise the cell, after making sure it's kosher
				conflict = self.check_for_conflicts(cell, option)	
				if not conflict:
					cell.finalise_cell(option)
					cell.filled = 'Elimination'
					some_cell_finalised = True

					if debug:
						print "Added to board by process of elimination:"
						self.print_board_to_screen()
						print

					# Now we have eliminated a cell, let's recalculate options
					self.strike_options_all()

		return some_cell_finalised

	def check_for_conflicts(self, cell, proposed_value):
		"""
		Given a cell and potential value, check to make sure there are no clashes
		"""
		row, col, block = cell.row, cell.col, cell.block
		
		# Consider other cells in row, col, block in turn:
		for (index, fn) in [( row , self.get_row ),
							( col , self.get_col ),
							( block , self.get_block ) ]:

			array_to_check = fn(index)  # An array of cells (either col, row or block)
			for other_cell in array_to_check:
				if other_cell.final == proposed_value:
					# Another cell has our proposed value already! Return True, since conflict.
					return True

		# No conflict found, return False
		return False


	def check_board_solved(self):
		"""
		Checks if whole board filled in (return True).
		If any cells are not filled with final value, returns False.
		"""
		# Loop through cells
		for cell in self.cell_array:
			if not cell.final:
				# A non-final cell found, return False
				return False
		self.board_complete = True
		return True

	def export_board_to_csv(self, filename):
		"""
		Export current board to CSV
		"""		
		f = open(filename, 'w')
		count = 0
		for cell in self.cell_array:
			f.write(str(cell.final))
			if count%9 == 8:
				f.write('\n')
			else:
				f.write(',')
			count+=1

	def print_final_board_to_screen_neat(self):
		"""
		Print numbers to screen (without index positions, options etc. as in self.print_board_to_screen)
		"""
		index = 0
		print
		for cell in self.cell_array:
			print cell.final,
			
			if index%3==2:
				print ' ',  # Column gaps
			
			if index%27==26:
				print  # Row gaps
			
			if index%9==8:
				print   # Line breaks
			
			index+=1

	def clean_up(self):
		"""
		Stops the timer, writes the board to CSV file, exits
		"""
		if not self.board_complete:
			print "Board is not complete, will not stop timer / write to CSV"
			return False
		
		print "Board complete!"
		
		# Time taken
		self.time_end = time.time()
		total_time_taken = self.time_end - self.time_start
		print "Time taken: {:.2f} seconds".format(total_time_taken)

		# Write to CSV
		new_filename = "{}_complete.csv".format(self.filename[:-4])
		print "Writing to CSV file ({}).".format(new_filename)
		self.export_board_to_csv(new_filename)		

		# Print to screen neatly
		print "Printing to screen for your records:"
		self.print_final_board_to_screen_neat()

		# Print how cells were filled in
		filled_in = {'Elimination':0, 'Strike':0, 'Guess':0, 'Already supplied':0}
		for cell in self.cell_array:
			filled_in[cell.filled] += 1
		print "Entries were found by:"
		for tup in filled_in.iteritems():
			print "{}: {}".format(tup[0], tup[1])
		
		# Exit
		sys.exit(0)


class Cell:

	def __init__(self, entry, row, col, block):		
		"""
		A cell within the SuDoku board. 'self.final' is a written (known/guessed) entry.
		"""
		self.final = entry # Will either be None or an entry

		# If self.final == None, we need 1-9 in the options
		if self.final==None:
			self.options = range(1,10) # i.e. [1,2,3,4,5,6,7,8,9]
		else:
			self.options = None # i.e. the cell is already filled in

		# Indicies of the cell on the board
		self.row = row
		self.col = col
		self.block = block

		# How was cell filled in
		self.filled = 'Already supplied'

	def string_rep(self):
		"""
		Return 1 line string representation of the cell
		Example 1: |      |8-2-6|1234589  |
		Example 2: |  *6* |4-2-3|         |
		Key:       |final |index|options..|
		"""
		# Top line = option string
		option_string = ''
		if self.options == None:
			option_string = ' '*9
		else:
			for o in self.options:
				option_string += str(o)
			# Fill out remaining space
			remaining_space = 9 - len(option_string)
			option_string += remaining_space * ' '
		
		# Position string
		position_string = '{}-{}-{}'.format(self.row, self.col, self.block)
		
		# Final entry
		if self.final:
			final_string = ' *{}* '.format(self.final)
		else:
			final_string = '     '

		# Create the string to print
		string_to_print = """{}|{}|{}|""".format(final_string, position_string, option_string)
		return string_to_print

	def get_index(self, key):
		"""
		Getter for an index type, allowing key to be a string argument
		"""
		if key not in ('row', 'col', 'block'):
			raise ValueError, "Error - key must be 'row', 'col', or 'block'."
		if key=='row':
			return self.row
		if key=='col':
			return self.col
		if key=='block':
			return self.block

	def remove_option(self, option_to_strike):
		"""
		Remove an option from cell.options (if it exists)
		If this results in a removed option, return True
		"""
		# We will return this value
		option_removed = False

		# Cell already has a final value, no need to do anything
		if not self.options:
			return False

		# But if cell has option to strike in its options, let's strike it off
		if option_to_strike in self.options:
			self.options.remove(option_to_strike)
			option_removed = True

		return option_removed

	def finalise_cell(self, value):
		"""
		Finalise cell with a certain value.
		Note that we should check for conflicts *before* calling this function.
		"""
		self.final = value
		self.options = []

	def __repr__(self):
		return "{} (row {}, col {}, block {})".format(self.final, self.row, self.col, self.block)


# Main script
if __name__=='__main__':

	# Setup
	debug = False
	B = Board()
	print(chr(27) + "[2J") # Clears terminal screen

	# Get input - from command line or input
	if len(sys.argv)==2:
		filename = sys.argv[1]
	else:
		filename = raw_input('Type filename of input board (should be csv file) >> ')
		if filename=='':
			print "No boardname entered, using board1.csv as a default."
			filename='board1.csv'

	# Load board
	B.load_board(filename)
	
	# Solve board
	B.solve_board()

