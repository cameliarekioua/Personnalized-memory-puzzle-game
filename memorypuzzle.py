import tkinter as tk
from tkinter import filedialog
import random, pygame, sys
from pygame.locals import *

FPS = 30  # frames per second, the general speed of the program
WINDOWWIDTH = 640  # size of window's width in pixels
WINDOWHEIGHT = 480  # size of windows' height in pixels
REVEALSPEED = 8  # speed boxes' sliding reveals and covers
BOXSIZE = 110  # size of box height & width in pixels
GAPSIZE = 10  # size of gap between boxes in pixels
BOARDWIDTH = 5  # number of columns of icons
BOARDHEIGHT = 4  # number of rows of icons
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE


def main():
    global FPSCLOCK, DISPLAYSURF, image_paths
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0
    mousey = 0
    pygame.display.set_caption('Memory Game')

    images = loadImages(image_paths)
    mainBoard = getRandomizedBoard(images)
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None
    DISPLAYSURF.fill(BGCOLOR)

    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                firstSelection = handleMouseClick(mainBoard, revealedBoxes, firstSelection)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes


def select_images():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_paths = filedialog.askopenfilenames(
        title="Select 10 images",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    return root.tk.splitlist(file_paths)


def loadImages(image_paths):
    images = []
    for path in image_paths:
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (BOXSIZE, BOXSIZE))
        images.append(image)
    return images


def getRandomizedBoard(images):
    random.shuffle(images)  # Shuffle the images
    numImagesUsed = BOARDWIDTH * BOARDHEIGHT // 2  # number of pairs needed
    images = images[:numImagesUsed] * 2  # double the images for pairs
    random.shuffle(images)  # shuffle again

    # Create the board structure with random images.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(images.pop())
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):
    left = XMARGIN + boxx * (BOXSIZE + GAPSIZE)
    top = YMARGIN + boxy * (BOXSIZE + GAPSIZE)
    return (left, top)


def drawIcon(image, boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    DISPLAYSURF.blit(image, (left, top))


def drawBoard(board, revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                drawIcon(board[boxx][boxy], boxx, boxy)


def handleMouseClick(board, revealed, firstSelection):
    mousex, mousey = pygame.mouse.get_pos()
    boxx, boxy = getBoxAtPixel(mousex, mousey)

    if boxx is not None and boxy is not None:
        if not revealed[boxx][boxy]:
            revealBoxesAnimation(board, [(boxx, boxy)])
            revealed[boxx][boxy] = True

            if firstSelection is None:
                firstSelection = (boxx, boxy)
            else:
                if board[boxx][boxy] == board[firstSelection[0]][firstSelection[1]]:
                    if hasWon(revealed):
                        gameWonAnimation(board)
                else:
                    pygame.time.wait(1000)
                    coverBoxesAnimation(board, [(boxx, boxy), firstSelection])
                    revealed[boxx][boxy] = False
                    revealed[firstSelection[0]][firstSelection[1]] = False
                firstSelection = None
    return firstSelection


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        image = board[box[0]][box[1]]
        DISPLAYSURF.blit(image, (left, top))
        if coverage > 0:
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def startGameAnimation(board):
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return False
    return True


# Ask the user to select 10 images
image_paths = select_images()
if len(image_paths) != 10:
    print("Please select exactly 10 images.")
else:
    main()
