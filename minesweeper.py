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
        
        print("---------------------------------------------------------------------------------------")

        # debug
        print(f"{cell} - {count}\n")  
        # debug

        self.moves_made.add(cell) # este atributo serve apenas para controle de movimentos do jogo 
        self.mark_safe(cell) # propagação de conhecimento simples

        neighboring = self.get_neighboring(cell)  

        # Aqui a sentença pode ser esvaziada após cruzamento de dados com a base de conhecimento que mantém as células já
        # reveladas e os seus valores 
        acquired_sentence = self.__build_acquired_sentence_from_existent_knowledge(neighboring, count) 
        
        # Importante ter atenção com o que será executado neste bloco de código abaixo, que está condicionado a existência de algum
        # elemento dentro de 'acquired_sentence'. Se for algo que precisa ser executado precisa estar fora do bloco. Um bom exemplo
        # é a iteração em todos os elementos do conjunto de conhecimento para verificar se há alguma revelação sobre o estado do board
        # após as propagações de conhecimento que foram realizadas. Neste caso são 3:
        # 1 - self.mark_safe(cell)
        # 2 - propagação de conhecimento caso o novo conjunto revelado possua atributos que possibilitem determinar se todos os elementos
        # contidos nele são minas ou seguras 
        # 3 - propagações que são feitas na combinação de conjuntos e identificação de relações de superconjuntos e subconjuntos
        if (len(acquired_sentence.cells)):        
            propagated = self.propagate_knowledge(acquired_sentence, cell)

            if not propagated and len(self.knowledge) > 1:
                self.__make_deduction(acquired_sentence)
        
        for knowledge_set in self.knowledge:    
            set_len = len(knowledge_set.cells)
            set_count = knowledge_set.count 
            
            if not set_count and set_len:
                for cell in knowledge_set.cells.copy():
                    self.mark_safe(cell)
            if set_len and set_len == set_count:
                for cell in knowledge_set.cells.copy():
                    self.mark_mine(cell)

        print(f"know mines: {self.mines}")
        print(f"know safes: {self.safes}")   

        
    # 1.0 - Atualização da base (tentando afirmar valores (antes) incertos)  
    # 1.1 - Propagação de certezas (utiliza os elementos adjacentes)                                     
    def propagate_knowledge(self, sentence: Sentence, cell):                                         
                                                                                                    
        print("----------------------------------------------------------")    
        print("PROPAGATE KNOWLEDGE:")
        print(f"sentence: {sentence}")
        print("----------------------------------------------------------")
           
        # A sentença poderá ser vazia após o cruzamento dos dados de células da nova sentença com
        # a base de conhecimento que representa as células já reveladas (minas ou seguras)
        print(f"sentence.cells: {sentence.cells}")
        print(f"sentence.count: {sentence.count}")
             
        all_safes = sentence.count == 0 and len(sentence.cells) > 0
        all_mines = sentence.count == len(sentence.cells)
                                                                                      
        propagated = False
        if (all_safes or all_mines):
            propagated = True 

        if all_safes:
            for cell in sentence.cells.copy():
                self.mark_safe(cell)
        elif all_mines:
            for cell in sentence.cells.copy():
                self.mark_mine(cell)
                                                                                             
        return propagated
                                                                                                  
         
    def __make_deduction(self, new_sentence: Sentence):  
        
        # representa todas as sentenças com conjuntos que possuem relação de interseção com a nova sentença 
        # mas que não possuem relação de interseção entre si, formando assim, no melhor das hipóteses, um superconjunto da nova sentença
        multiple_sentence_combination = Sentence(set(), 0)
 
        # representa todas as sentenas com conjuntos que possuem relação de interseção com a nova sentença                                     
        # e com a combinação de múltiplas sentenças, formando assim, no melhor das hipóteses, um subconjunto da nova sentença
        multiple_sentence_difference = Sentence(set(), 0)
        
        new_inferences = []
        for sentence in self.knowledge:
            
            print("\n")
            print(f"new sentence: {new_sentence}\n\n") 
            print(f"iterarion sentence: {sentence}\n\n")

            if self.is_empty_set(sentence.cells, sentence.count):
                continue

            subset = None
            superset = None        
            if self.is_proper_subset(new_sentence, sentence): 
                subset = new_sentence
                superset = sentence 
            elif self.is_proper_subset(sentence, new_sentence): 
                superset = new_sentence
                subset = sentence 
            else:
                print("\n")
                print(f"Combination sentence [1]: {multiple_sentence_combination}")
                # i still don't know if it could be better to keep building the combination sentence even if there superset/subset relation have been found 
                if (len(multiple_sentence_combination.cells.intersection(sentence.cells)) == 0 and len(sentence.cells.intersection(new_sentence.cells))):
                    multiple_sentence_combination.cells = multiple_sentence_combination.cells.union(sentence.cells)
                    multiple_sentence_combination.count = multiple_sentence_combination.count + sentence.count

                    print(f"Combination sentence [2]: {multiple_sentence_combination}")
 
                    if self.is_proper_subset(multiple_sentence_combination, new_sentence): 
                        subset_from_combination = new_sentence # já faz parte da base de conhecimento 
                        combination_superset = multiple_sentence_combination
                        
                        mines_diff = max(combination_superset.count - subset_from_combination.count, 0)
                        combination_superset.cells.difference_update(subset_from_combination.cells)
                        combination_superset.count = mines_diff

                        if self.knowledge.__contains__(combination_superset):
                            continue 

                        new_inferences.append(multiple_sentence_combination)

                        propagated = self.propagate_knowledge(combination_superset) 
                        if not propagated:
                            self.__make_deduction(combination_superset)

                        
                    if self.is_proper_subset(new_sentence, multiple_sentence_combination): 
                        superset_from_sentence = new_sentence # já faz parte da base de conhecimento
                        combination_subset = multiple_sentence_combination # mesmo caso acima, porém ao contrário

                        mines_diff = max(superset_from_sentence.count - combination_subset.count, 0)
                        superset_from_sentence.cells.difference_update(combination_subset.cells)
                        superset_from_sentence.count = mines_diff

                        if self.knowledge.__contains__(superset_from_sentence):
                            continue

                        keep_comparing = not self.propagate_knowledge(superset_from_sentence) 
                        if keep_comparing:
                            self.__make_deduction(superset_from_sentence)

                        keep_comparing = not self.propagate_knowledge(combination_subset) 
                        if keep_comparing:
                            self.__make_deduction(combination_subset)

                    elif not len(multiple_sentence_difference.cells.intersection(sentence.cells)):
                        multiple_sentence_difference.cells.union(sentence.cells)
                        multiple_sentence_difference.count = multiple_sentence_difference.count + sentence.count

            if subset is not None and superset is not None:
                
                print("\n\n")
                print(f"superset: {superset}")
                print(f"subset: {subset}") 
                
                mines_diff = max(superset.count - subset.count, 0)
                superset.cells.difference_update(subset.cells)
                superset.count = mines_diff

                #new_inferences.append(superset) -> vai duplicar
  
                keep_comparing = self.propagate_knowledge(superset) 
                if keep_comparing:
                    self.__make_deduction(superset)
          
        self.knowledge.extend(new_inferences)
 
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
        return a != b and not self.is_empty_set(a.cells, a.count) and not self.is_empty_set(b.cells, b.count) and a.cells.issubset(b.cells) # eliminar conjuntos vazios

    def is_empty_set(self, s: set, count):
        if len(s) == 0:
            if count != 0:
                raise Exception("Empty set must have a count value of zero")
            return True
        
        return False
    
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

  
        
        













