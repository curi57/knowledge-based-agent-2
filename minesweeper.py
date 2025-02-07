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
        acquired_sentence = self.__build_acquired_sentence_from_existent_knowledge(neighboring, count) 
        
        print(f"acquired_sentence: {acquired_sentence}")
        
        self.knowledge.append(acquired_sentence)
  
        revealed = False                                                                                          
        cp = acquired_sentence.cells.copy()

        # Here we're trying to propagate knowledge from the conclusions about a exclusive sentence
        if self.__all_safes(acquired_sentence):  
            for cell in cp:  
                self.mark_safe(cell)
            revealed = True 
        elif self.__all_mines(acquired_sentence):
            for cell in cp:
                self.mark_mine(cell)
            revealed = True 
        
        # It is possible to have a empty Sentence "here"
        if not revealed:        
            
            print("----------------------------------------------------------") 
            print("Try to create new knowledge:")
            print("----------------------------------------------------------")
            
            self.__create_new_knowledge(acquired_sentence)

            
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

    def __propagate_if_new(self, new_sentence: Sentence) -> bool:

        is_new = not self.knowledge.__contains__(new_sentence)
        cp_cells = new_sentence.cells.copy()
        if is_new:
            if self.__all_safes(new_sentence):
                    
                for cell in cp_cells:        
                    # New sentence is not yet in the Knowledge Base, no need for copied cells, since this method does not change anything in the new sentence
                    self.mark_safe(cell)
                    new_sentence.cells.remove(cell)
                    new_sentence.safes.add(cell)

            elif self.__all_mines(new_sentence):

                    for cell in cp_cells:
                        self.mark_mine(cell)
                        new_sentence.cells.remove(cell)
                        new_sentence.mines.add(cell)
                        new_sentence.count -= 1

        return is_new

    
    def __create_new_knowledge(self, new_sentence: Sentence): 
        
        for sentence_x in self.knowledge: 

            # Evita comparar novas sentenças com conjuntos que já foram totalmente revelados (vazios)
            #if len(sentence.cells) == 0:                                                                      
            #    continue

            # -> It is guarantee that sentence have some unknown cells

            new_knowledge = []
            for sentence_y in self.knowledge:
                    
                print("\n")
                print(f"sentence_x: {sentence_x}\n")
                print(f"sentence_y: {sentence_y}\n")                                                 
                print("\n\n")

                intersection = sentence_x.cells.intersection(sentence_y.cells)
                if len(intersection):

                    print(f"intersection: {intersection}")

                    safe_cells_x = len(sentence_x.cells) - sentence_x.count
                    # The minimum number of mines in the intersecion concluded by looking at the set A
                    min_mines_intersection_x = len(intersection) - safe_cells_x
                    
                    safe_cells_y = len(sentence_y.cells) - sentence_y.count 
                    # The minimum number of mines in the intersecion concluded by looking at the set B
                    min_mines_intersection_y = len(intersection) - safe_cells_y
                    
                    # Either not of the intersection min number are Zero (improve english)
                    if min_mines_intersection_x or min_mines_intersection_y:
                        new_sentence = Sentence(intersection, max(min_mines_intersection_x, min_mines_intersection_y))
                        new_sentence_x = Sentence(sentence_x.cells.difference(new_sentence.cells), sentence_x.count - new_sentence.count)
                        new_sentence_y = Sentence(sentence_y.cells.difference(new_sentence.cells), sentence_y.count - new_sentence.count)
                    
                        # What's the chance to be duplicated?
                        if self.__propagate_if_new(new_sentence):
                            new_knowledge.append(new_sentence)
                        
                        if self.__propagate_if_new(new_sentence_x):
                            new_knowledge.append(new_sentence_x)
                        
                        if self.__propagate_if_new(new_sentence_y):
                            new_knowledge.append(new_sentence_y)
 
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

  
        
# Create new knowledge
# After updating the Superset there is not elements left inside the cells property if they're all safes or all mines

# It means unknown will contain the value of 0 and all the cells from the original sentence will be inside the mines or safes structure

# I this case all_safes will return False because unknown is 0 (False)

# all_mines will propably return False either because not(no_mines) will return False (no_mines is True and not(no_mines) is False) resulting the 
# proposition to be False
                                                                                                                                                   
# In both cases deducted_and_propagated will return False and therefore the recursion will be called for a empty sentence, 
# wasting time and computational resources. Also, no propagation will be done resulting in wrong outputs.
                                                                                                                                                   
# The question is: How come the propagation for safe cells is happening? (clue: last block of code before terminating the add_knowledge function)


#new_knowledge = []
#for sentence in self.knowledge:       
#    
#    # Evita comparar novas sentenças com conjuntos que já foram totalmente revelados (vazios)
#    if len(sentence.cells) == 0:                                                                      
#        continue
#    
                                                                                                                                                        
#    # -> It is guarantee that sentence have some unknown cells
                                                                                                                                                        
#    print("\n")
#    print(f"iteration sentence: {sentence}\n")
#    print(f"new sentence: {new_sentence}\n") 
                                                                                                                                                        
#    print("\n\n")
                                                                                                                                                        
#    new_knowledge_sentence = self.is_proper_subset(new_sentence, sentence) # [New]
#    #if superset is not None:
#    
#    # [English]
#    # Nesta versão do algoritmo o conjunto original é mantido inalterado na base de conhecimento e a diferença entre o superconjunto e
#    # o subconjunto é criado como uma nova sentença, caso contrário não seria possível definir se as células que estão representando
#    # a diferença são minas ou seguras, portanto, também não seria possível transferi-las para a estrutura correspondente (known_safes ou known_mines)
#    if new_knowledge_sentence is not None and not self.knowledge.__contains__(new_knowledge_sentence):
#        new_knowledge.append(new_knowledge_sentence)
#        #self.knowledge.append(new_knowledge_sentence)
#        
#        #print(f"superset: {superset}")
#        print(f"new_knowledge_sentence: {new_knowledge_sentence}")
                                                                                                                                                        
#          
#        # The new knowledge is not updated (self.mark_mine and self.mark_safe does not have effect on sentences that are part of the KB)
#        revealed = self.__try_reveal(new_knowledge_sentence)
#        
#        if not revealed:
#            
#            # Revisar este retorno (com retorno e sem retorno não faz diferença, deveria fazer?)
#            self.__create_new_knowledge(new_knowledge_sentence)
#    else:
#        print(f"No relation for new_sentence: {new_sentence}")
                                                                                                                                                        
#self.knowledge.extend(new_knowledge)

                                                                                                                                                       
#def is_proper_subset_V2(self, a: Sentence, b: Sentence) -> Sentence | None:  
#    
#    new_sentence = None
#    if not a.__eq__(b):
#                                                                           
#        if a.cells.issubset(b.cells):
#            
#            # A is the subset 
#            print(f"subset: {a}") 
#                                                                           
#            mines_diff = max(b.count - a.count, 0)
#            new_sentence = Sentence(b.cells.difference(a.cells), mines_diff)
#                                                                             
#            return b
#        elif b.cells.issubset(a.cells):
#                
#            # B is the subset 
#            print(f"subset: {b}") 
#                                                                           
#            mines_diff = max(a.count - b.count, 0)
#            new_sentence = Sentence(a.cells.difference(b.cells), mines_diff)
                                                                                                                                                       
#    return new_sentence 
                                                                                                                                                       
                                                                                                                                                       
#def is_proper_subset(self, a: Sentence, b: Sentence) -> Sentence | None:  
#    if not a.__eq__(b):
                                                                                                                                                       
#        if a.cells.issubset(b.cells):
#            
#            # A is the subset 
#            print(f"subset: {a}") 
                                                                                                                                                       
#            mines_diff = max(b.count - a.count, 0)
#            b.cells.difference_update(a.cells)
#            b.count = mines_diff
                                                                                                                                                       
#            return b
#        elif b.cells.issubset(a.cells):
#            
#            # B is the subset
#            print(f"subset: {b}")
                                                                                                                                                       
#            mines_diff = max(a.count - b.count, 0)
#            a.cells.difference_update(b.cells)
#            a.count = mines_diff
                                                                                                                                                       
#            return a
#    
#    return None 
    #return a != b and a.cells.issubset(b.cells) 
