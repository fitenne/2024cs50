import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
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
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

        self.mines: set[tuple[int, int]] = set()
        self.safes: set[tuple[int, int]] = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        self.draw()
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        self.draw()
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
        
        assert self.count != 0
        assert cell not in self.mines
        
        self.count -= 1
        self.cells.remove(cell)
        self.mines.add(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell not in self.cells:
            return
                
        self.safes.add(cell)
        self.cells.discard(cell)

    def draw(self):
        if self.count == len(self.cells) and len(self.cells) != 0:
            self.mines.update(self.cells)
            self.cells.clear()
            self.count = 0
        if self.count == 0 and len(self.cells) != 0:
            self.safes.update(self.cells)
            self.cells.clear()

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge: list[Sentence] = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def join_sentence(self, sentence: Sentence):
        for m in self.mines:
            sentence.mark_mine(m)
        for s in self.safes:
            sentence.mark_safe(s)

        self.knowledge.append(sentence)

        for m in sentence.known_mines():
            self.mark_mine(m)
        for s in sentence.known_safes():
            self.mark_safe(s)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        if cell in self.moves_made:
            return
        
        # cells either in self.mines or self.safes only added by mark_xxxx(cell)
        # thus every sentences knows that at the time of add

        # cells in knowledge[?].mines/safes could from a deduction or a mark_mines/safes
        
        # 1)
        self.moves_made.add(cell)
        # 2)
        if cell not in self.safes:
            self.mark_safe(cell)
        # 3)
        self.join_sentence(Sentence(cells=[
            (i, j) 
                for i in range(cell[0]-1, cell[0]+2) 
                    for j in range(cell[1]-1, cell[1]+2) 
                        if not(i == cell[0] and j == cell[1])
                             and (i, j) not in self.safes
                             and i >= 0 and i < self.height and j >= 0 and j < self.width
        ], count=count))

        while True:
            done = True

            # other sentences may draw new conclution
            for s in self.knowledge:
                for safe in s.known_safes():
                    if safe not in self.safes:
                        done = False
                        self.mark_safe(safe)
                for mine in s.known_mines():
                    if mine not in self.mines:
                        done = False
                        self.mark_mine(mine)

            for s in self.knowledge:
                for t in self.knowledge:
                    if s != t \
                      and len(s.cells) > 0 and len(t.cells) > 0 and len(t.cells) > len(s.cells) \
                      and s.cells.issubset(t.cells):
                        done = False
                        self.join_sentence(Sentence(cells=[
                            *(t.cells - s.cells)
                        ], count=t.count - s.count))

            if done:
                break



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) in self.safes and (i, j) not in self.moves_made:
                    return (i, j)
        
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        for i in range(self.width):
            for j in range(self.height):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    return (i, j)

        return None