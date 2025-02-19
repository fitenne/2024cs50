import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword: Crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var, _ in self.domains.items():
            var: Variable = var
            self.domains[var] = set(filter(lambda w: len(w) == var.length, self.domains[var]))

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        if self.crossword.overlaps[x, y] == None:
            return False

        dx, dy = self.crossword.overlaps[x, y]

        filtered = set(
            filter(
                lambda xcan: any(
                    map(lambda ycan: xcan[dx] == ycan[dy], self.domains[y])
                ),
                self.domains[x],
            )
        )

        revised = len(filtered) != len(self.domains[x])
        self.domains[x] = filtered
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = [
                k
                for k, v in self.crossword.overlaps.items()
                if v != None
            ]

        while len(arcs) != 0:
            u, v = arcs.pop()
            if self.revise(u, v):
                if len(self.domains[u]) == 0:
                    return False
                for m, n in self.crossword.overlaps.keys():
                    if m == u and n != v:
                        arcs.append((n, m))

        return True

    def assignment_complete(self, assignment: dict):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return assignment.keys() == self.crossword.variables

    def consistent(self, assignment: dict):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        if len(set(assignment.values())) != len(assignment.keys()):
            return False

        self.enforce_node_consistency()
        self.ac3()

        if any([
            v not in self.domains[k]
            for k, v in assignment.items()
        ]):
            return False

        for i in range(len(assignment)):
            for j in range(i + 1, len(assignment)):
                if (i, j) in self.crossword.overlaps.keys():
                    di, dj = self.crossword.overlaps[i, j]
                    if assignment[i][di] != assignment[j][dj]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        sorted(
            self.domains[var],
            key=lambda s: sum([
                1
                for k in self.crossword.overlaps.keys()
                if k != None and var == k[0] and k[1] not in assignment and s in self.domains[k[1]]
            ])
        )
        return list(self.domains[var])

    def select_unassigned_variable(self, assignment: dict):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # sort is stable
        return sorted(
            sorted(
                self.crossword.variables.difference(assignment.keys()),
                key=lambda var: len(self.domains[var])
            ),
            key=lambda var: sum([
                1
                for k in self.crossword.overlaps.keys()
                if k != None and k[0] == var
            ]),
            reverse=True
        )[0]

    def backtrack(self, assignment: dict):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            if self.consistent(assignment):
                return assignment
            return None
        
        var = self.select_unassigned_variable(assignment)
        for i in self.order_domain_values(var, assignment):
            assignment[var] = i
            res =  self.backtrack(assignment)
            if res != None:
                return res
            assignment.pop(var)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
