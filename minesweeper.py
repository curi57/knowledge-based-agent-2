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
     
        print(f"{cell} - {count}")
       
        self.moves_made.add(cell) 
        self.mark_safe(cell) # marca a célula descoberta como 'safe' em toda a base de conhecimento = ['Conhecimento Adquirido']
        
        # acquired_knowledge representa todas as células que são vizinhas da célula clicada, exceto a mesma
        acquired_knowledge = Sentence(self.get_neighboring(cell), count)
        self.knowledge.append(acquired_knowledge)

        # aqui a atualização de conhecimento poderá ser feita com base em inferências explícitas, como o número de minas ser igual a ZERO para todas as células vizinhas
        needs_update = self.__update_knowledge_base(acquired_knowledge)
        if needs_update:
            # esta função simplesmente atualiza o novo conhecimento adquirido com informações de células com minas e seguras já descobertas na base de conhecimento 
            for safe in self.safes:
                self.mark_safe(safe)
            for mine in self.mines:
                self.mark_mine(mine)

        print(self)
              
        self.__create_knowledge(acquired_knowledge)


    def __update_knowledge_base(self, sentence: Sentence) -> bool:                                                                                     
        
        # nota: é possível ter uma sentença com zero/ zero?
            # - é possível que uma sentença que represente um conhecimento prévio que tenha sido atualizado até que ambas as propriedades possuam valor ZERO
        if len(sentence.cells) == 0:
            print(f"sentence.cells == 0 must have {sentence.count} value (zero)")
            return True
       
        all_safes = sentence.count == 0 and len(sentence.cells) > 0
        all_mines = sentence.count > 0 and sentence.count == len(sentence.cells)

        if all_safes or all_mines:
            if all_safes:
                cp_cells = sentence.cells.copy()
                for cell in cp_cells:
                    self.mark_safe(cell)                                                                                                                                   
            elif all_mines:
                cp_cells = sentence.cells.copy()
                for cell in cp_cells:
                    self.mark_mine(cell)                                                                                                                              
            
            return False 

        return True 
         
    def __create_knowledge(self, new_sentence: Sentence):
        
        #new_knowledge = None 
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

                mines_diff = max(superset.count - subset.count, 0)
                new_knowledge = Sentence(superset.cells.difference(subset.cells), mines_diff) 
                #superset = Sentence(superset.cells.difference(subset.cells), mines_diff)  
                
                print(f"new_knowledge before update: {superset}")
                
                # nota: não é necessário atualizar safes e minas para este novo conhecimento pois o mesmo é um subset de uma relação de conhecimentos previamente atualizados
                # aqui precisamos apenas tentar inferir novas minas ou novos 'safes'
                needs_update = self.__update_knowledge_base(new_knowledge)
                if needs_update:
                    for previous_sentence in self.knowledge:
                        # verificar também se elementos mais 'antigos' da base de conhecimento podem oferecer algum tipo de inferência para o modelo de aprendizado
                        self.__update_knowledge_base(previous_sentence) 

                # anti loop-infinito
                #if not self.knowledge.__contains__(new_knowledge):
                #self.__create_knowledge(superset)       

     
    def is_proper_subset(self, a: Sentence, b: Sentence):
        return a != b and (len(a.cells) > 0 and len(b.cells) > 0) and a.cells.issubset(b.cells) # eliminar conjuntos vazios
    
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

  
        
        


