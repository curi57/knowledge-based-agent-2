import random
from typing import List



# o quê fazer depois de criar uma nova sentença (inferência) a partir da sentença combinada?
# a sentença combinada foi criada e populada na iteração, portanto, não existe na base de conhecimento
# se essa sentença for capaz de propagar inferências absolutas sobre o jogo, não será necessário adiciona-la a base de conhecimento
# porém, se a inferência for parcial, ela pode ser usada na próxima recursão?
# então teríamos uma branch criada para a inferência (combinada) e uma iteração que continua com a nova sentença sendo testada com outros conjuntos (ok?)
# se a inferência parcial chamar a recursão, teremos um outro contexto de memória, onde a sentença combinada é reiniciada

# como adicionamos esta nova inferência combinada a base de conhecimento?
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

    def knowledge_repr(self):
        print("--------------------------------------------------------------------------------------")
        for sentence in self.knowledge:
            print(f"sentence: {sentence}")
        print("--------------------------------------------------------------------------------------")


    def add_knowledge(self, cell, count):                                                                                                                                             
        
        print("---------------------------------------------------------------------------------------")

        print(f"{cell} - {count}\n")  
    
        self.moves_made.add(cell)         
        self.mark_safe(cell) 

        neighboring = self.get_neighboring(cell)

        # This method filter the cells from the new sentence based on the known mines and known safes 
        acquired_sentence = self.__build_acquired_sentence_from_existent_knowledge(neighboring, count)  
        self.knowledge.append(acquired_sentence)
        print(f"acquired_sentence: {acquired_sentence}")
        if len(acquired_sentence.cells): 
            if self.__all_safes(acquired_sentence): 
                cp_cells = acquired_sentence.cells.copy()
                for cell in cp_cells:  
                    self.mark_safe(cell)
            elif self.__all_mines(acquired_sentence):
                cp_cells = acquired_sentence.cells.copy()
                for cell in cp_cells:
                    self.mark_mine(cell)

              
        print("----------------------------------------------------------") 
        print("Try to create new knowledge:")
        print("----------------------------------------------------------")
       
        self.__create_new_knowledge()

        print(f"[DEBUG] Knowledge BEFORE propagation completion:")
        self.knowledge_repr()
        print(f"[DEBUG]")
 
        self.__make_deduction_from_iteration_result() 
       
        print(f"Knowledge after propagation completion:")
        self.knowledge_repr()

        print(f"self.mines [Total]: {self.mines}")
        print(f"self.safes [Total]: {self.safes}")  


    def __build_acquired_sentence_from_existent_knowledge(self, neighboring: set, count: int) -> Sentence:              
        
        # What happens if the sentence is a conclusion?
        unknowns = set()
        safes = set()
        mines = set()
        for cell in neighboring:
            if self.safes.__contains__(cell):
                safes.add(cell)
            elif self.mines.__contains__(cell):
                mines.add(cell)
            else:
                unknowns.add(cell) # What if it is a conclusion?
       
        sentence = Sentence(unknowns, count - len(mines))
        sentence.safes = safes
        sentence.mines = mines
                                                                                                                  
        return sentence
 
 
    def __make_deduction_from_iteration_result(self):
          
        for sentence in self.knowledge:  
            
            print(f"sentence.known_mines: {sentence.known_mines()}")
            print(f"sentence.known_safes: {sentence.known_safes()}")

            if len(sentence.cells) > 0:
            
                unknowns = len(sentence.cells) # Quantity
                mines = sentence.count 
                all_safes = unknowns > 0 and mines == 0 
                all_mines = mines > 0 and mines == unknowns
                propagate = all_safes or all_mines
                                                  
                if propagate:
                    sentence_cells_cp = sentence.cells.copy()
                    if all_safes:  
                        for cell in sentence_cells_cp:
                            self.mark_safe(cell)
                    elif all_mines:
                        for cell in sentence_cells_cp:
                            self.mark_mine(cell)

                    return self.__make_deduction_from_iteration_result() 


    def __all_safes(self, sentence: Sentence):
        unknowns = len(sentence.cells) 
        mines = sentence.count   
         
        return (unknowns > 0 and mines == 0)

    def __all_mines(self, sentence: Sentence):
        unknowns = len(sentence.cells) 
        mines = sentence.count   
        
        return (mines > 0 and mines == unknowns)

    def __try_propagate(self, new_sentences: List[Sentence]):
        
        for sentence in new_sentences:
            cp_cells = sentence.cells.copy()

            # The method contains verify if sentence is already in KB (because of the inner for loop, wich creates each relation 2 times) and the length verification is for to avoid to add zero sets coming from a subset/superset relation
            if not self.knowledge.__contains__(sentence) and len(sentence.cells) > 0:
                
                self.knowledge.append(sentence)
                
                if self.__all_safes(sentence):        
                    for cell in cp_cells:        
                        self.mark_safe(cell)
                          
                elif self.__all_mines(sentence):
                    for cell in cp_cells:
                        self.mark_mine(cell)
                        

    def __create_new_knowledge(self): 
        
        new_knowledge = []
        for sentence_x in self.knowledge: 

            # Evita comparar novas sentenças com conjuntos que já foram totalmente revelados (vazios)
            if len(sentence_x.cells) == 0:                                                                      
                continue

            for sentence_y in self.knowledge:
                    
                print("\n")
                print(f"sentence_x: {sentence_x}\n")
                print(f"sentence_y: {sentence_y}\n")                                                 
                print("\n\n")

                intersection = sentence_x.cells.intersection(sentence_y.cells)
                if len(intersection) and not sentence_x.__eq__(sentence_y):

                    print(f"intersection: {intersection}")

                    safe_cells_x = min(len(sentence_x.cells) - sentence_x.count, len(intersection))
                    # The minimum number of mines in the intersecion concluded by looking at the set A
                    min_mines_intersection_x = len(intersection) - safe_cells_x
                    
                    safe_cells_y = min(len(sentence_y.cells) - sentence_y.count, len(intersection))
                    # The minimum number of mines in the intersecion concluded by looking at the set B
                    min_mines_intersection_y = len(intersection) - safe_cells_y
                    
                    print(f"min_mines_intersection_x: {min_mines_intersection_x}")
                    print(f"min_mines_intersection_y: {min_mines_intersection_y}")
                    if min_mines_intersection_x or min_mines_intersection_y:
                        
                        new_sentence = Sentence(intersection, max(min_mines_intersection_x, min_mines_intersection_y))       
                        new_sentence_x = Sentence(sentence_x.cells.difference(new_sentence.cells), max(0, sentence_x.count - new_sentence.count))
                        new_sentence_y = Sentence(sentence_y.cells.difference(new_sentence.cells), max(0, sentence_y.count - new_sentence.count))
                        
                        self.__try_propagate([new_sentence, new_sentence_x, new_sentence_y])
                             
        self.knowledge.extend(new_knowledge) 
                     
    # Aplicar operação com matriz
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

  
        





















































