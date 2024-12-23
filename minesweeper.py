from _typeshed import Self
import itertools
import random
from typing import List


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

    # what if they are both count zero 
    # what if new_sentence count is zero 
    # what if the sentence is count zero
    # what if new_sentence.count is bigger than sentence.count?
        # - diff will be negative
    def extract_knowledge(self, new_sentence: Sentence, sentence: Sentence):
        
        subset = None
        superset = None
        
        if self.is_proper_subset(new_sentence, sentence): 
            subset = new_sentence
            superset = sentence 
        elif self.is_proper_subset(sentence, new_sentence): 
            superset = new_sentence
            subset = sentence 
        
        if subset is not None and superset is not None: 
            
            print("issubset or superset")

            unknown = superset.unknown()  
            mines_diff = min(superset.count - subset.count, 0)
                                                                                                                                      
            new_knowledge = Sentence(unknown - unknown.intersection(subset.unknown()), superset.count - mines_diff)
            new_knowledge.mines = new_knowledge.cells.intersection(self.mines)
            new_knowledge.safes = new_knowledge.cells.intersection(self.safes)
            
            new_knowledge_unknown = new_knowledge.unknown()
            if new_knowledge.count == len(new_knowledge_unknown):
                for cell in new_knowledge_unknown:
                    self.mark_mine(cell)
            elif new_knowledge.count == 0:
                for cell in new_knowledge_unknown:
                    self.mark_safe(cell)

            self.knowledge.append(new_knowledge)
            
            for sentence in self.knowledge:
                self.extract_knowledge(new_knowledge, sentence)            

    # remove code repetition 
    def add_knowledge(self, cell, count):
      
        self.moves_made.add(cell)
        self.mark_safe(cell) 

        neighboring = self.get_neighboring(cell) 
        input_sentence_knowledge = Sentence(neighboring, count)
        input_sentence_knowledge.mines = input_sentence_knowledge.cells.intersection(self.mines)
        input_sentence_knowledge.safes = input_sentence_knowledge.cells.intersection(self.safes)
        
        input_sentence_knowledge_unknown = input_sentence_knowledge.unknown()
        if input_sentence_knowledge.count == len(input_sentence_knowledge_unknown):
            for cell in input_sentence_knowledge_unknown:
                self.mark_mine(cell)
        elif input_sentence_knowledge.count == 0:
            for cell in input_sentence_knowledge_unknown:
                self.mark_safe(cell)

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

  
        
        


