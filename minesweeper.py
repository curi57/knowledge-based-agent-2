import random
from typing import List


class Minesweeper():
    
    def __init__(self, height=4, width=4, mines=4):
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

        print(self.mines)
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

    def won(sel):  
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
        # If all cells in the sentence are mines, return them
        if len(self.cells) == self.count:
            return self.cells.copy()
        # Otherwise, no definitive conclusion
        return set()
  
    def known_safes(self):
        if self.count == 0:
            return self.cells.copy()
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
        
        print("---------------------------------------------------------------------------------------")

        print(f"{cell} - {count}\n")  
    
        self.moves_made.add(cell)         
        self.mark_safe(cell)

        self.__use_inference()

        neighboring = self.get_neighboring(cell)

        unknowns = set()
        safes = set()
        mines = set()
        for cell in neighboring:
            if self.safes.__contains__(cell):
                safes.add(cell)
            elif self.mines.__contains__(cell):
                mines.add(cell)
            else:
                unknowns.add(cell) 
                                                          
        acquired_sentence = Sentence(unknowns, count - len(mines))
        acquired_sentence.safes = safes
        acquired_sentence.mines = mines
  
        self.knowledge.append(acquired_sentence)
        
        print(f"Complete Sentence: {Sentence(neighboring, count)}")
        print(f"Reduced Sentence [acquired_sentence]: {acquired_sentence}")
 
        print(f"[DEBUG] Knowledge BEFORE __create_new_knowledge and __use_inference:")
        print("--------------------------------------------------------------------------------------")
        for sentence in self.knowledge:
            print(f"sentence: {sentence}")
        print("--------------------------------------------------------------------------------------")

        self.__create_new_knowledge() 
         
        print(f"[DEBUG] Knowledge AFTER __create_new_knowledge and __use_inference:")
        print("--------------------------------------------------------------------------------------")
        for sentence in self.knowledge:
            print(f"sentence: {sentence}")

        print("--------------------------------------------------------------------------------------")  
        for sentence in self.knowledge:
            print(f"sentence.known_mines: {sentence.known_mines()}")
            print(f"sentence.known_safes: {sentence.known_safes()}")
 

    def __use_inference(self):
        
        count = 0
        while count < len(self.knowledge):

            sentence = self.knowledge.__getitem__(count)

            print(f"Sentence [Make Deduction]: {sentence}")

            unknowns = len(sentence.cells) 
            mines = sentence.count 
            all_safes = unknowns > 0 and mines == 0 
            all_mines = mines > 0 and mines == unknowns
            propagate = all_safes or all_mines
                                              
            if propagate:
                count = 0
                sentence_cells_cp = sentence.cells.copy()
                if all_safes:  
                    for cell in sentence_cells_cp:
                        self.mark_safe(cell)
                elif all_mines:
                    for cell in sentence_cells_cp:
                        self.mark_mine(cell)
            else:
                count += 1


    def __try_save(self, sentence: Sentence) -> bool:
        
        if not self.knowledge.__contains__(sentence) and len(sentence.cells) > 0:
            self.knowledge.append(sentence)
            return True
        
        return False
        

    def __create_new_knowledge(self): 
        
        self.__use_inference()       
        for sentence_x in self.knowledge: 
            
            # Avoid to compare new sentences to completely revealed sets
            if len(sentence_x.cells) == 0:                                                                      
                continue
            
            for sentence_y in self.knowledge:
                
                kb_updated = False 

                # Avoid to compare new sentences to completely revealed sets
                if len(sentence_y.cells) == 0 or sentence_y.__eq__(sentence_x):                                                                      
                    continue
 
                print("\n")
                print(f"sentence_x: {sentence_x}\n")
                print(f"sentence_y: {sentence_y}\n")                                                 
                print("\n\n")

                if sentence_y.cells.issubset(sentence_x.cells):
                    
                    new_sentence = Sentence(sentence_x.cells.difference(sentence_y.cells), max(0, sentence_x.count - sentence_y.count))
                    print(f"new_sentence [Subset]: {new_sentence}")
                    kb_updated = self.__try_save(new_sentence)
                    if kb_updated:
                        self.knowledge.remove(sentence_x)
                      
                elif sentence_x.cells.issubset(sentence_y.cells):

                    new_sentence = Sentence(sentence_y.cells.difference(sentence_x.cells), max(0, sentence_y.count - sentence_x.count))
                    print(f"new_sentence [Subset]: {new_sentence}")
                    
                    kb_updated = self.__try_save(new_sentence)
                    if kb_updated:
                        self.knowledge.remove(sentence_y)  
                else:

                    intersection = sentence_x.cells.intersection(sentence_y.cells)
                    if len(intersection) and not sentence_x.__eq__(sentence_y):
 
                        # Represent the number of safe cells: cannot be Negative
                        #safe_cells_x = min(len(sentence_x.cells) - sentence_x.count, len(intersection))
                        no_mines_x = len(sentence_x.cells) - sentence_x.count
                        
                        # The minimum number of mines in the intersecion (concluded by looking at the set A)
                        # Safe cells are retrieved by subtracting the count value from the length of the set. 
                        min_mines_intersection_x = len(intersection) - no_mines_x # Observation: A negative number means a minimum
                        # of safes elements in Intersection

                        max_mines_intersection_x = min(sentence_x.count, len(intersection))
                        
                        no_mines_y = len(sentence_y.cells) - sentence_y.count

                        # The minimum number of mines in the intersecion concluded by looking at the set B
                        min_mines_intersection_y = len(intersection) - no_mines_y # A negative number means Safes (in Intersection)

                        # The max number of mines is the count value when count is smaller then the size of the Intersection 
                        # Ex. A set with a count of 3 and a Intersection with a length of 2 couldn't have a max number of mines of 3
                        # (more mines of elements in the Intersection Set)
                        max_mines_intersection_y = min(sentence_y.count, len(intersection))
 
                        new_count = None 
                        if max_mines_intersection_x == min_mines_intersection_y:
                            new_count = max_mines_intersection_x
                        if max_mines_intersection_y == min_mines_intersection_x:
                            new_count = max_mines_intersection_y
            
                        if new_count is not None:
                            new_sentence = Sentence(intersection, new_count)       
                            print(f"new_sentence [Intersection]: {new_sentence}")
                              
                            virtual_sentence_x = Sentence(
                                    sentence_x.cells.difference(new_sentence.cells), 
                                    max(0, sentence_x.count - new_sentence.count))
                            print(f"virtual_sentence_x: {virtual_sentence_x}")
                            
                            virtual_sentence_y = Sentence(
                                    sentence_y.cells.difference(new_sentence.cells), 
                                    max(0, sentence_y.count - new_sentence.count))
                            print(f"virtual_sentence_x: {virtual_sentence_y}")
 
                            kb_updated = self.__try_save(virtual_sentence_x)
                            kb_updated = self.__try_save(virtual_sentence_y) or kb_updated
            
                if kb_updated:                           
                    self.__use_inference()
                             
            
    # Apply Matrix Operation
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

  
        





















































