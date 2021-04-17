import pygame
import os
import sys
from sudoku import Sudoku, SquareStack, Square, Cell

DIM = 9
CLUES = 32
OVERRIDE = False

# Colours
BLACK = (0, 0, 0)
GREY = (180, 180, 180)
WHITE = (255, 255, 255)
GREEN = (45, 217, 33)
ORANGE = (240, 182, 10)
RED = (209, 17, 17)

def sample():
    boards = []
    while len(boards) < 100:
        game = Sudoku()
        if game.board not in [gm.board for gm in boards]:
            boards.append(game)
    for gm in boards:
        gm.print()

pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

OPEN_SANS = os.path.join("assets", "fonts", "OpenSans-Regular.ttf")
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

BRDPADDING = 30
brdwidth = (0.5 * width)
brdheight = height - (BRDPADDING * 2)
cellsize = int(min(brdwidth / DIM, brdheight / DIM))
brdorigin = ((width / 2) - (brdwidth / 2), (height / 2) - (brdheight / 2))

game = Sudoku(override=OVERRIDE, dim=DIM, clues=CLUES)
game.print()

filled = set()
for i in range(len(game.board)):
    for j in range(len(game.board[i])):
        if game.board[i][j] is not None:
            filled.add(Square((i, j), game.board[i][j]))

won = False

aiPlaying = False
# Show instructions
instructions = True

cells = []
enterval = ""
selected = False

while True:
    for event in pygame.event.get(): # Check for quit
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill(GREY)

    if instructions:  # show instructions
        # Title
        title = largeFont.render("Play Sudoku", True, BLACK)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)
        # Rules
        rules = [
            "Each square can only contain the numbers 1-9.",
            "For every row, column, and quadrant a number can only appear once.",
            "Fill the board to win."
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, BLACK)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)
        # Play game button
        buttonText = mediumFont.render("Play Game", True, BLACK)
        buttonRect = pygame.Rect(((width / 4), (2 / 5 * height)), (width / 2, 50))
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, WHITE, buttonRect)
        screen.blit(buttonText, buttonTextRect)
        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click:
            if buttonRect.collidepoint(pygame.mouse.get_pos()):
                instructions = False

        pygame.display.flip()
        continue

    # Board

    for i in range(DIM):
        col = []
        for j in range(DIM):
            # Draw rectangle for cell
            rect = pygame.Rect(brdorigin[0] + i * cellsize, brdorigin[1] + j * cellsize, cellsize, cellsize)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, GREY, rect, 3)
            if game.value((i, j)) is not None:
                value = mediumFont.render(str(game.value((i, j))), True, BLACK)
                valueTextRect = value.get_rect()
                valueTextRect.center = rect.center
                screen.blit(value, valueTextRect)
            col.append(Cell(rect))
        if len(cells) != DIM:
            cells.append(col)
    for i in range(1, 3):
        divider = pygame.Rect(brdorigin[0] + (i * 3) * cellsize - 2, brdorigin[1], 4, cellsize * 9)
        pygame.draw.rect(screen, BLACK, divider)
    for j in range(1, 3):
        divider = pygame.Rect(brdorigin[0], brdorigin[1] + (j * 3) * cellsize - 2, cellsize * 9, 4)
        pygame.draw.rect(screen, BLACK, divider)

    outline = pygame.Rect(brdorigin[0], brdorigin[1], cellsize * DIM, cellsize * DIM)
    pygame.draw.rect(screen, BLACK, outline, 4, 5)
    for col in cells:
        for cell in col:
            if cell.state:
                pygame.draw.rect(screen, GREEN, cell.rect, 4)


    # AI solve button
    aiButton = pygame.Rect(
        (7.5 / 10) * width + BRDPADDING, (1 / 3) * height - 50, (width / 4.5) - BRDPADDING, 50
    )
    buttonText = mediumFont.render("AI Solve", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        aiButton.topleft[0], aiButton.topleft[1] + 70, (width / 4.5) - BRDPADDING, 50
    )
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    quitButton = pygame.Rect(
        resetButton.topleft[0], resetButton.topleft[1] + 70, (width / 4.5) - BRDPADDING, 50
    )
    buttonText = mediumFont.render("Quit", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = quitButton.center
    pygame.draw.rect(screen, WHITE, quitButton)
    screen.blit(buttonText, buttonRect)
    # Check for a win
    if not any(None in col for col in game.board):
        won = True
        for x in range(len(game.board)):
            for y in range(len(game.board[x])):
                if cells[x][y].state:
                    cells[x][y].toggleselect()
        text = "Won"
        text = mediumFont.render(text, True, WHITE)
        textRect = text.get_rect()
        textRect.center = (buttonRect.center[0], buttonRect.center[1] + 70)
        screen.blit(text, textRect)

    left = False

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            left = True
        elif event.type == pygame.KEYDOWN:
            if selected:
                if event.key == pygame.K_BACKSPACE:
                    enterval = ""
                else:
                    if len(enterval) == 0:
                        if str(event.unicode).isnumeric():
                            enterval += event.unicode
                for x in range(len(game.board)):
                    for y in range(len(game.board[x])):
                        if cells[x][y].state:
                            if len(enterval) > 0 and int(enterval) in game.possible_numbers((x, y)):
                                game.board[x][y] = int(enterval)
                            else:
                                game.board[x][y] = None
                                enterval = ""
    # Handle left mouse button click

    if left:
        mouse = pygame.mouse.get_pos()
        if resetButton.collidepoint(mouse):
            game = Sudoku(override=OVERRIDE, dim=DIM, clues=CLUES)
            won = False
            aiPlaying = False
            continue
        elif aiButton.collidepoint(mouse):
            game.solve()
        elif quitButton.collidepoint(mouse):
            pygame.quit()
        # When selecting a cell:
        elif not won:
            for x in range(len(game.board)):
                for y in range(len(game.board[x])):
                    if cells[x][y].rect.collidepoint(mouse) and game.original[x][y] is None:
                        # Deselect any other square that was selected
                        for i in range(len(game.board)):
                            for j in range(len(game.board[i])):
                                if (i, j) != (x, y):
                                    if cells[i][j].state:
                                        cells[i][j].toggleselect()
                        cells[x][y].toggleselect()
                        selected = cells[x][y].state
                        enterval = str(game.board[x][y]) if game.board[x][y] is not None else ""

    pygame.display.flip()