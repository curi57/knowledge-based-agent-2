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

        unknown = len(acquired_sentence.cells) 
        no_mines = not acquired_sentence.count
        all_safes = unknown and no_mines 
        all_mines = not no_mines and (acquired_sentence.count == unknown)
        propagated = False                                                                                          
        self.knowledge.append(acquired_sentence)
        acquired_sentence_cells_cp = acquired_sentence.cells.copy()
        if all_safes:  
            for cell in acquired_sentence_cells_cp:

                # Sentence is still not part of the knowledge base 
                #acquired_sentence.cells.remove(cell)
                #acquired_sentence.safes.add(cell)
                self.mark_safe(cell)
            propagated = True 
        elif all_mines:
            for cell in acquired_sentence_cells_cp:

                # Sentence is still not part of the knowledge base 
                #acquired_sentence.cells.remove(cell)
                #acquired_sentence.mines.add(cell)
                #acquired_sentence.count = acquired_sentence.count - 1

                self.mark_mine(cell)
            propagated = True 
        
        if not propagated:        
            print("----------------------------------------------------------") 
            print("Try to inference and propagate new knowledge:")
            print("----------------------------------------------------------")
            self.__try_create_new_knowledge(acquired_sentence)

            
        print(f"[DEBUG] Knowledge before propagation completion:")
        self.knowledge_repr()
        print(f"[DEBUG]")
 
        # Finalizar propagação do conhecimento em todas as sentenças da base de conhecimento
        for sentence in self.knowledge:   
            
            unknown = len(sentence.cells) 
            no_mines = not sentence.count
            all_safes = unknown and no_mines 
            all_mines = not no_mines and (sentence.count == unknown)
 
            sentence_cells_cp = sentence.cells.copy()
            if all_safes:  
                for cell in sentence_cells_cp:
                    self.mark_safe(cell)
            elif all_mines:
                for cell in sentence_cells_cp:
                    self.mark_mine(cell)
             
        print(f"Knowledge after propagation completion:")
        self.knowledge_repr()

        print(f"self.mines: {self.mines}")
        print(f"self.safes: {self.safes}")   


    def __try_create_new_knowledge(self, new_sentence: Sentence):  
      
        for sentence in self.knowledge:        
            print("\n")
            print(f"iteration sentence: {sentence}\n")
            print(f"new sentence: {new_sentence}\n") 

            print("\n\n")
            
            # Ou a sentença ou a nova sentença será o Superset (ou não haverá relação entre os conjuntos)
    
            # 1. Caso a sentença seja o superset ela será atualizada na diferença com o subset (nova sentença). Para garantir
            # que a nova sentença seja inserida na base de conhecimento sem duplicata, devemos realizar todas as iterações para apenas no final adicionar a estrutura

            # 2. Caso a nova sentença seja o superset, a sentença (subset) continua inalterada e podemos seguir a mesma diretriz para o caso acima, deixando para adicionar a nova senteça que terá sido modificada ou terá modificado durantes as iterações e provavelmente chegará ao final do método com menos elementos e com propriedades diferentes
            superset = self.is_proper_subset(new_sentence, sentence)            
            if superset is not None: 
                print(f"superset: {superset}")
                
                unknown = len(superset.cells) 
                no_mines = not superset.count
                all_safes = unknown and no_mines 
                all_mines = not no_mines and (superset.count == unknown)  
                deducted_and_propagated = False 

                superset_cells_cp = superset.cells.copy();
                if all_safes:  
                    for cell in superset_cells_cp:
                        self.mark_safe(cell)
                    deducted_and_propagated = True 
                elif all_mines:
                    for cell in superset_cells_cp:
                        self.mark_mine(cell)
                    deducted_and_propagated = True

                keep_comparing = not deducted_and_propagated
                if keep_comparing:
                    self.__try_create_new_knowledge(superset)  
            else:
                print(f"No relation for new_sentence: {new_sentence}")

        
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

        print(f"sentence.known_mines: {sentence.known_mines()}")
        print(f"sentence.known_safes: {sentence.known_safes()}")
                                                                                                                             
        return sentence
   

    # (1) Conjuntos não vazios e que já fazem parte da base de conhecimento podem se tornar conjuntos vazios 
    # na iteração para atualização após uma nova jogada 
    # (2) Tanto a sentença que está sendo iterada quando a nova sentença são testadas antes da iteração acontecer
    def is_proper_subset(self, a: Sentence, b: Sentence) -> Sentence | None:  
        if not a.__eq__(b):
            if a.cells.issubset(b.cells):
                
                print(f"subset: {a}") 

                mines_diff = max(b.count - a.count, 0)
                b.cells.difference_update(a.cells)
                b.count = mines_diff

                return b
            elif b.cells.issubset(a.cells):
 
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
