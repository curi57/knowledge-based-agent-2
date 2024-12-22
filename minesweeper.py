from _typeshed import Self
import itertools
import random
from typing import List



"""
Called when the Minesweeper board tells us, for a given
safe cell, how many neighboring cells have mines in them.
                                                               
This function should:
    1) mark the cell as a move that has been made
    2) mark the cell as safe
    3) add a new sentence to the AI's knowledge base
       based on the value of `cell` and `count`
    4) mark any additional cells as safe or as mines
       if it can be concluded based on the AI's knowledge base
    5) add any new sentences to the AI's knowledge base
       if they can be inferred from existing knowledge
"""

class Minesweeper():
    
    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()

        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):  
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):  
        return self.mines_found == self.mines


class Sentence():

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count 
        self.safes = set()
        self.mines = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        return self.mines    
        
    def known_safes(self):
        return self.safes        
        
    def mark_mine(self, cell):
        if self.cells.__contains__(cell):
            self.mines.add(cell)

    def mark_safe(self, cell):    
        if self.cells.__contains__(cell):
            self.safes.add(cell)

    def unknown(self) -> set:
        return self.cells - self.cells.intersection(self.safes.union(self.mines))


# this class contains all the knowledge about the envinroment
class MinesweeperAI():

    def __init__(self, height=8, width=8):

        self.height = height
        self.width = width

        self.moves_made = set()

        self.mines = set()
        self.safes = set()

        self.knowledge: List[Sentence] = []

    def mark_mine(self, cell):  
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):  
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def extract_knowledge(self, input_sentence_knowledge: Sentence, sentence: Sentence):
        
        if self.is_proper_subset(input_sentence_knowledge, sentence): 
            print("ispropersubset")
            
            unknown = sentence.unknown()
            #cell_nearby_mines = count
            cell_nearby_mines = input_sentence_knowledge.count
                                                                                                                                      
            # what if they are both count zero 
            # what if input_sentence_knowledge count is zero 
            # what if the sentence is count zero
            # what if new_sentence.count is bigger than sentence.count?
                # - diff will be negative
            mines_diff = min(sentence.count - cell_nearby_mines, 0)
                                                                                                                                      
            new_knowledge = Sentence(unknown - unknown.intersection(input_sentence_knowledge.unknown()), sentence.count - mines_diff)
            new_knowledge.mines = new_knowledge.cells.intersection(self.mines)
            new_knowledge.safes = new_knowledge.cells.intersection(self.safes)
            self.knowledge.append(new_knowledge)

        elif self.is_proper_subset(sentence, input_sentence_knowledge):
            print("ispropersuperset")


    def add_knowledge(self, cell, count):
      
        self.moves_made.add(cell)
        self.mark_safe(cell) 

        neighboring = self.get_neighboring(cell) 
        input_sentence_knowledge = Sentence(neighboring, count)
        input_sentence_knowledge.mines = input_sentence_knowledge.cells.intersection(self.mines)
        input_sentence_knowledge.safes = input_sentence_knowledge.cells.intersection(self.safes)
        self.knowledge.append(input_sentence_knowledge)                
         
        for sentence in self.knowledge:
            self.extract_knowledge(input_sentence_knowledge, sentence)
            
    def is_proper_subset(self, a: Sentence, b: Sentence):
        return a.unknown().issubset(b.unknown()) and not a.__eq__(b) #review it

    def get_neighboring(self, cell: tuple):

        neighboring = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):                                                         
                if (i, j) == cell:
                    continue
                                                                 
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighboor = (i, j)
                    neighboring.add(neighboor)  

        return neighboring

 
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if self.moves_made.__contains__(safe):
                continue
            self.moves_made.add(safe)
            return safe

        return None

    def make_random_move(self):  
        choices = []
        for i in range(self.height):
            for j in range(self.width):
                move_candidate = (i, j)
                if self.moves_made.__contains__(move_candidate) or self.mines.__contains__(move_candidate):
                    continue

                choices.append(move_candidate)
        
        random_choice = random.choice(choices)

        print(random_choice)

        return random_choice

  
        
        


