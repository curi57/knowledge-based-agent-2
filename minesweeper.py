#import itertools
import random
from types import UnionType
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
        if cell in self.cells:
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):    
        if cell in self.cells:
            self.safes.add(cell)
            self.cells.remove(cell)


class MinesweeperAI():

    def __init__(self, height=8, width=8):

        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge: List[Sentence] = []

    def __str__(self):
        return f"mines: {str(self.mines)}"

    def mark_mine(self, cell):  
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):  
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
  
    def add_knowledge(self, cell, count):                                                                                                                                             
        
        # debug
        print(f"{cell} - {count}\n\n")

        for i in self.knowledge:
            print(f"knowledge -> {i}, \n")
            for j in i.known_safes():
                print(f"safes: {j}")

            print("\n")

            for j in i.known_mines():
                print(f"mines: {j}")
        # debug

        neighboring = self.get_neighboring(cell)  
        acquired_sentence = self.__build_acquired_sentence_from_existent_knowledge(neighboring, count) 
        self.knowledge.append(acquired_sentence)
 
        self.moves_made.add(cell) 
        self.mark_safe(cell)         
        
        self.propagate_knowledge(acquired_sentence)
        
        has_min_knowledge = len(self.knowledge) > 1
        if has_min_knowledge:
            self.__exploit(acquired_sentence)
    

    def __exploit(self, new_sentence: Sentence):  
        
        new_inferences = [] 
        for sentence in self.knowledge:
            
            print(f"sentence [iteration]: {sentence}\n\n")

            subset = None
            superset = None        
            if self.is_proper_subset(new_sentence, sentence): 
                subset = new_sentence
                superset = sentence 
            elif self.is_proper_subset(sentence, new_sentence): 
                superset = new_sentence
                subset = sentence 
            
            if subset is not None and superset is not None:
                print("\n\n")
                print(f"superset: {superset}")
                print(f"subset: {subset}") 
                
                mines_diff = max(superset.count - subset.count, 0)
                superset.cells.intersection_update(subset.cells)
                superset.count = mines_diff

                #if self.knowledge.__contains__(inference_sentence):
                #    continue
                
                self.propagate_knowledge(superset)
                #self.propagate_knowledge(subset)
                
                self.__exploit(superset)
        
            if subset is not None:
                new_inferences.append(subset)

        self.knowledge.extend(new_inferences)
   

    def propagate_knowledge(self, sentence: Sentence):
          
        if sentence.count == 0 and len(sentence.cells) > 0:
            for cell in sentence.cells.copy():
                self.mark_safe(cell)
        elif sentence.count == len(sentence.cells):
            for cell in sentence.cells.copy():
                self.mark_mine(cell)

 
    def __build_acquired_sentence_from_existent_knowledge(self, neighboring: set, count: int) -> Sentence:
        
        unknown = set()
        safes = set()
        mines = set()
        for cell in neighboring:
            if self.safes.__contains__(cell):
                safes.add(cell)
            elif self.mines.__contains__(cell):
                mines.add(cell)
            else:
                unknown.add(cell)
        
        sentence = Sentence(unknown, count - len(mines))
        sentence.safes = safes
        sentence.mines = mines 
                                                                                                                                                                            
        return sentence
   
    def is_proper_subset(self, a: Sentence, b: Sentence):
        return a != b and not self.is_empty_set(a.cells) and not self.is_empty_set(b.cells) and a.cells.issubset(b.cells) # eliminar conjuntos vazios

    def is_empty_set(self, s: set):
        return len(s) == 0
    
    # nota: aplicar operação com matriz
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

  
        
        


# updates a single sentence
#def update_sentence(self, sentence: Sentence):
#    if sentence.count == 0 and len(sentence.cells) > 0:
#        for cell in sentence.cells:
#            sentence.safes.add(cell)
#            sentence.safes.remove(cell)
#    elif sentence.count == len(sentence.cells):
#        for cell in sentence.cells:
#            sentence.mines.add(cell)
#            sentence.cells.remove(cell)
#            sentence.count = sentence.count -1
