#import itertools
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

        #self.__update()

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
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):    
        if self.cells.__contains__(cell):
            self.safes.add(cell)
            self.cells.remove(cell)

    def update(self, safes: set, mines: set):
        unknowns = len(self.cells)
                                                                 
        if self.count == 0 and unknowns > 0:
            self.safes |= self.cells
            self.cells.clear()      
        elif self.count > 0 and self.count == unknowns:
            self.mines |= self.cells
            self.cells.clear()
            self.count = 0
        else:
            for safe in safes:
                self.mark_safe(safe)                             
            for mine in mines:
                self.mark_mine(mine)


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
       
    def extract_knowledge(self, new_sentence: Sentence):
       
        new_knowledge = None 
        for sentence in self.knowledge:
            subset = None
            superset = None        
            if self.is_proper_subset(new_sentence, sentence): 
                subset = new_sentence
                superset = sentence 
            elif self.is_proper_subset(sentence, new_sentence): 
                superset = new_sentence
                subset = sentence 
            
            if subset is not None and superset is not None: 
 
                print(f"superset: {superset}")
                print(f"subset: {subset}") 

                new_knowledge_cells = superset.cells - superset.cells.intersection(subset.cells) 
                mines_diff = min(superset.count - subset.count, 0)                                                                          
                new_knowledge = Sentence(new_knowledge_cells, superset.count - mines_diff)
                #new_knowledge.update(self.safes, self.mines) # esta função deve fornecer informação suficiente para quê outras partes do conhecimento possam se atualizar
                self.update_knowledge_base(new_knowledge)

                # also check for updates on previous knowledge (after update knowledge base from new knowledge)
                #self.update_knowledge_base(sentence) -> WHY?!

                # avoid an infinite loop
                if not self.knowledge.__contains__(new_knowledge):
                    self.extract_knowledge(new_knowledge)       

        # why add knowledge after iteration? how it does impact the final result from the knowledge intersections?
        if new_knowledge is not None: 
            self.knowledge.append(new_knowledge)

    
    # add knowledge acquired from the game
    def add_acquired_knowledge(self, cell):
        self.moves_made.add(cell)
        self.mark_safe(cell) 

    def update_knowledge_base(self, sentence: Sentence):
        
        #if len(sentence.cells) == 0:
        #    return False
        
        unknowns = len(sentence.cells)
        if sentence.count == 0 and unknowns > 0:
            sentence.safes |= sentence.cells
            sentence.cells.clear()      
        elif sentence.count > 0 and sentence.count == unknowns:
            sentence.mines |= sentence.cells
            sentence.cells.clear()
            sentence.count = 0
        else:
            for safe in self.safes:
                sentence.mark_safe(safe)                             
            for mine in self.mines:
                sentence.mark_mine(mine)

    # remove code repetition 
    def add_knowledge(self, cell, count):
        
        print(f"{cell} - {count}")

        self.add_acquired_knowledge(cell) 
        
        acquired_knowledge = Sentence(self.get_neighboring(cell), count)
        acquired_knowledge.update(self.safes, self.mines)
        
        self.extract_knowledge(acquired_knowledge)
           

    def is_proper_subset(self, a: Sentence, b: Sentence):
        return a != b and len(a.cells) > 0 and a.cells.issubset(b.cells) # eliminating empty sets
    
    # apply matrix operation
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

  
        
        


