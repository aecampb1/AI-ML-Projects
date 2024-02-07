import itertools
import random


class Minesweeper:
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


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            # check if cell in set of cells though to be a mine
            self.cells.remove(cell)


class MinesweeperAI:
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

        # Keep track of accounted mines
        self.accounted_mines = set()

        # List of sentences about the game known to be true
        self.knowledge = []

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
        if cell in self.moves_made:
            self.moves_made.remove(cell)

        if hasattr(self, "safes") and hasattr(self, "knowledge"):
            self.safes.add(cell)

            for sentence in self.knowledge:
                sentence.mark_safe(cell)

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

        # 2) Mark cell as safe
        self.mark_safe(cell)

        # 3) Adjust count based on known mines in the neighborhood
        for mine in self.mines:
            if mine in self.get_neighbors(cell) and mine not in self.accounted_mines:
                count -= 1

        # 1) Mark cell as move made
        self.moves_made.add(cell)

        # 4) Add a new sentence to the knowledge base
        new_sentence_cells = self.get_neighbors(cell)
        new_sentence_cells.difference_update(self.safes)
        new_sentence_cells.difference_update(self.moves_made)
        new_sentence_cells.difference_update(self.mines)
        new_sentence = Sentence(new_sentence_cells, count)
        self.knowledge.append(new_sentence)

        # 5) Inference base on subset
        for sentence in self.knowledge:
            if new_sentence.cells.issubset(sentence.cells):
                # A subset of B, update B counts
                difference_cells = sentence.cells.difference(new_sentence.cells)
                if sentence.count - new_sentence.count == 0:
                    for cell in difference_cells:
                        self.mark_safe(cell)
                elif sentence.count - new_sentence.count == len(difference_cells):
                    for cell in difference_cells:
                        self.mark_mine(cell)
            elif new_sentence.cells.issuperset(sentence.cells):
                # Superset of B, update B counts
                difference_cells = new_sentence.cells.difference(sentence.cells)
                if new_sentence.count == 0:
                    for cell in difference_cells:
                        self.mark_safe(cell)
                elif new_sentence.count - sentence.count == len(difference_cells):
                    for cell in difference_cells:
                        self.mark_mine(cell)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = [cell for cell in self.safes if cell not in self.moves_made]

        if safe_moves:
            # choose a safe move
            chosen_move = safe_moves[0]
            return chosen_move
        else:
            return None

    def play(self):
        # Makes safe move nad updates self.moves_made
        safe_move = self.make_safe_move()

        if safe_move:
            # Add the chosen safe move to self.moves_made
            self.moves_made.add(safe_move)
            # Remove the chosen move from the set of safe cells
            self.safes.remove(safe_move)
            return safe_move
        else:
            # IF no safe moves are available, makea random move
            random_move = self.make_random_move()
            if random_move:
                # Add the chosen random move to self.moves_made
                self.moves_made.add(random_move)
                return random_move
            else:
                return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = list(itertools.product(range(self.height), range(self.width)))
        possible_moves = [
            cell
            for cell in all_cells
            if cell not in self.moves_made and cell not in self.mines
        ]
        if possible_moves:
            return random.choice(possible_moves)
        return None

    def get_neighbors(self, cell):
        # returns neighbors available
        i, j = cell
        neighbors = set(
            itertools.product(
                range(max(0, i - 1), min(self.height, i + 2)),
                range(max(0, j - 1), min(self.width, j + 2)),
            )
        )
        neighbors.remove(cell)
        return neighbors
