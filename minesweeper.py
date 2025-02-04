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

        # debug
        print(f"{cell} - {count}\n")  
        # debug
    
        # Este atributo serve apenas para controle de movimentos do jogo 
        self.moves_made.add(cell)         
        # Marcando a célula revelada como segura e propagando 
        self.mark_safe(cell) 

        neighboring = self.get_neighboring(cell)  

        # Aqui a sentença pode ser esvaziada após cruzamento de dados com a base de conhecimento que mantém as células já
        # reveladas e os seus valores 
        acquired_sentence = self.__build_acquired_sentence_from_existent_knowledge(neighboring, count) 
        
        print(f"acquired_sentence: {acquired_sentence}")
        # Adding the sentence to the Knowledge Base 
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

    
    def __make_deduction_from_iteration_result(self):

        for sentence_x in self.knowledge:  
               
            print(f"sentence.known_mines: {sentence_x.known_mines()}")
            print(f"sentence.known_safes: {sentence_x.known_safes()}")

            if len(sentence_x.cells) > 0:
            
                unknowns = len(sentence_x.cells) # Quantity
                mines = sentence_x.count 
                all_safes = unknowns > 0 and mines == 0 
                all_mines = mines > 0 and mines == unknowns
                propagate = all_safes or all_mines
                                                  
                if propagate:
                    sentence_x_cells_cp = sentence_x.cells.copy()
                    if all_safes:  
                        for cell in sentence_x_cells_cp:
                            self.mark_safe(cell)
                    elif all_mines:
                        for cell in sentence_x_cells_cp:
                            self.mark_mine(cell)

                    return self.__make_deduction_from_iteration_result()


                for sentence_y in self.knowledge:
                    
                    size_x = len(sentence_x.cells)
                    size_y = len(sentence_y.cells)

                    if not size_x == size_y:
                        continue 
                    
                    intersection = sentence_x.cells.intersection(sentence_y.cells)
                    simmetric_diff = sentence_x.cells.symmetric_difference(sentence_y.cells)
                    
                    if len(intersection) == len(simmetric_diff) and len(intersecion) == sentence_x.count:

                        new_count = size_x - size_y
                        if new_count < 0:
                            continue

                        print(f"new_count: {new_count}")

                        mine_sentence_candidate = Sentence(sentence_y.cells.difference(sentence_x.cells), size_x - size_y)
                        safe_sentence_candidate = Sentence(sentence_x.cells.difference(sentence_y.cells), max(0, size_y - size_x))

                        #self.mark_safe(safe_diff)
                        #self.mark_mine(mine_diff)
            

    def __all_safes(self, sentence: Sentence):
        unknowns = len(sentence.cells) 
        mines = sentence.count   
         
        return (unknowns > 0 and mines == 0)

    def __all_mines(self, sentence: Sentence):
        unknowns = len(sentence.cells) 
        mines = sentence.count   
        
        return (mines > 0 and mines == unknowns)


    # After updating the Superset there is not elements left inside the cells property if they're all safes or all mines
    
    # It means unknown will contain the value of 0 and all the cells from the original sentence will be inside the mines or safes structure
    
    # I this case all_safes will return False because unknown is 0 (False)
    
    # all_mines will propably return False either because not(no_mines) will return False (no_mines is True and not(no_mines) is False) resulting the 
    # proposition to be False
                                                                                                                                                       
    # In both cases deducted_and_propagated will return False and therefore the recursion will be called for a empty sentence, 
    # wasting time and computational resources. Also, no propagation will be done resulting in wrong outputs.
                                                                                                                                                       
    # The question is: How come the propagation for safe cells is happening? (clue: last block of code before terminating the add_knowledge function)
    def __create_new_knowledge(self, new_sentence: Sentence):  
        
        new_knowledge = []
        for sentence in self.knowledge:       
            
            # Evita comparar novas sentenças com conjuntos que já foram totalmente revelados (vazios)
            if len(sentence.cells) == 0:                                                                      
                continue
            

            # -> It is guarantee that sentence have some unknown cells

            print("\n")
            print(f"iteration sentence: {sentence}\n")
            print(f"new sentence: {new_sentence}\n") 

            print("\n\n")
 
            new_knowledge_sentence = self.is_proper_subset(new_sentence, sentence) # [New]
            #if superset is not None:
            
            # [English]
            # Nesta versão do algoritmo o conjunto original é mantido inalterado na base de conhecimento e a diferença entre o superconjunto e
            # o subconjunto é criado como uma nova sentença, caso contrário não seria possível definir se as células que estão representando
            # a diferença são minas ou seguras, portanto, também não seria possível transferi-las para a estrutura correspondente (known_safes ou known_mines)
            if new_knowledge_sentence is not None and not self.knowledge.__contains__(new_knowledge_sentence):
                new_knowledge.append(new_knowledge_sentence)
                #self.knowledge.append(new_knowledge_sentence)
                
                #print(f"superset: {superset}")
                print(f"new_knowledge_sentence: {new_knowledge_sentence}")

                  
                # The new knowledge is not updated (self.mark_mine and self.mark_safe does not have effect on sentences that are part of the KB)
                revealed = self.__try_reveal(new_knowledge_sentence)
                
                if not revealed:
                    
                    # Revisar este retorno (com retorno e sem retorno não faz diferença, deveria fazer?)
                    self.__create_new_knowledge(new_knowledge_sentence)
            else:
                print(f"No relation for new_sentence: {new_sentence}")

        self.knowledge.extend(new_knowledge)
        
    def __try_reveal(self, new_sentence: Sentence) -> bool:
        
        revealed = False
        if new_sentence.count == 0:
            
            # Do it make sense to verify if number of cells in the sentence are not zero?
            for cell in new_sentence.cells:
                
                # New sentence is not yet in the Knowledge Base, no need for copied cells, since this method does not change anything in the new sentence
                self.mark_safe(cell)

                new_sentence.cells.remove(cell)
                new_sentence.safes.add(cell)

            revealed = True 
        elif new_sentence.count == len(new_sentence.cells):

            new_sentence.cells = new_sentence.cells.copy()

            for cell in new_sentence.cells:
                self.mark_mine(cell)
                new_sentence.cells.remove(cell)
                new_sentence.mines.add(cell)
                new_sentence.count -= 1
            revealed = True

        return revealed

         
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
  
    def is_proper_subset_V2(self, a: Sentence, b: Sentence) -> Sentence | None:  
        
        new_sentence = None
        if not a.__eq__(b):
                                                                               
            if a.cells.issubset(b.cells):
                
                # A is the subset 
                print(f"subset: {a}") 
                                                                               
                mines_diff = max(b.count - a.count, 0)
                new_sentence = Sentence(b.cells.difference(a.cells), mines_diff)
                                                                                 
                return b
            elif b.cells.issubset(a.cells):
                    
                # B is the subset 
                print(f"subset: {b}") 
                                                                               
                mines_diff = max(a.count - b.count, 0)
                new_sentence = Sentence(a.cells.difference(b.cells), mines_diff)

        return new_sentence 

 
    def is_proper_subset(self, a: Sentence, b: Sentence) -> Sentence | None:  
        if not a.__eq__(b):

            if a.cells.issubset(b.cells):
                
                # A is the subset 
                print(f"subset: {a}") 

                mines_diff = max(b.count - a.count, 0)
                b.cells.difference_update(a.cells)
                b.count = mines_diff

                return b
            elif b.cells.issubset(a.cells):
                
                # B is the subset
                print(f"subset: {b}")

                mines_diff = max(a.count - b.count, 0)
                a.cells.difference_update(b.cells)
                a.count = mines_diff

                return a
        
        return None 
        #return a != b and a.cells.issubset(b.cells) 

    def is_valid_sentence(self, s: Sentence):
        if len(s.cells) > 0:
            return True 

        if s.count != 0:
            raise Exception("Empty sentence must have a count value of zero")

        return False
            
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

  
        
        
#else:
#    print("\n")
#    print(f"Combination sentence [1]: {multiple_sentence_combination}")
#    # i still don't know if it could be better to keep building the combination sentence even if there superset/subset relation have been found 
#    if (len(multiple_sentence_combination.cells.intersection(sentence.cells)) == 0 and len(sentence.cells.intersection(new_sentence.cells))):
#        multiple_sentence_combination.cells = multiple_sentence_combination.cells.union(sentence.cells)
#        multiple_sentence_combination.count = multiple_sentence_combination.count + sentence.count
#                                                                                                                                                 
#        print(f"Combination sentence [2]: {multiple_sentence_combination}")
#                                                                                                                                                 
#        if self.is_proper_subset(multiple_sentence_combination, new_sentence): 
#            subset_from_combination = new_sentence # já faz parte da base de conhecimento 
#            combination_superset = multiple_sentence_combination
#            
#            mines_diff = max(combination_superset.count - subset_from_combination.count, 0)
#            combination_superset.cells.difference_update(subset_from_combination.cells)
#            combination_superset.count = mines_diff
#                                                                                                                                                 
#            if self.knowledge.__contains__(combination_superset):
#                continue 
#                                                                                                                                                 
#            new_inferences.append(multiple_sentence_combination)
#                                                                                                                                                 
#            propagated = self.propagate_knowledge(combination_superset) 
#            if not propagated:
#                self.__make_deduction(combination_superset)
#                                                                                                                                                 
#            
#        if self.is_proper_subset(new_sentence, multiple_sentence_combination): 
#            superset_from_sentence = new_sentence # já faz parte da base de conhecimento
#            combination_subset = multiple_sentence_combination # mesmo caso acima, porém ao contrário
#                                                                                                                                                 
#            mines_diff = max(superset_from_sentence.count - combination_subset.count, 0)
#            superset_from_sentence.cells.difference_update(combination_subset.cells)
#            superset_from_sentence.count = mines_diff
#                                                                                                                                                 
#            if self.knowledge.__contains__(superset_from_sentence):
#                continue
#                                                                                                                                                 
#            keep_comparing = not self.propagate_knowledge(superset_from_sentence) 
#            if keep_comparing:
#                self.__make_deduction(superset_from_sentence)
#                                                                                                                                                 
#            keep_comparing = not self.propagate_knowledge(combination_subset) 
#            if keep_comparing:
#                self.__make_deduction(combination_subset)
#                                                                                                                                                 
#        elif not len(multiple_sentence_difference.cells.intersection(sentence.cells)):
#            multiple_sentence_difference.cells.union(sentence.cells)
#            multiple_sentence_difference.count = multiple_sentence_difference.count + sentence.count
