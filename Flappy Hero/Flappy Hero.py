from itertools import cycle
import random  # For generating random numbers
import sys     # We will use sys.exit to exit the program

import pygame
from pygame.locals import * # Basic pygame imports

pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()
pygame.mixer.music.load('gallery/audio/soundtrack.mp3')
pygame.mixer.music.set_volume(-5)
pygame.mixer.music.play(-1)


# Global Variables for the game
FPS = 30 #แสดงผลจำนวนภาพต่อ 1 วินาที
SCREENWIDTH  = 288
SCREENHEIGHT = 512
PIPEGAPSIZE  = 110 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79

# image, sound and hitmask  dicts
IMAGES = {}
SOUNDS = {}
HITMASKS = {} 

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = [
 # character1 >> Superman
    ['gallery/sprites/superman1.png',
     'gallery/sprites/superman2.png',
     'gallery/sprites/superman3.png'
    ],
 # character2 >> Ironman
    ['gallery/sprites/ironman1.png',
     'gallery/sprites/ironman2.png',
     'gallery/sprites/ironman3.png'
     ],
 # character3 >> Spiderman
    ['gallery/sprites/spiderman1.png',
     'gallery/sprites/spiderman2.png',
     'gallery/sprites/spiderman3.png',
    ],
]

# list of backgrounds
BACKGROUNDS_LIST = ['gallery/sprites/background-day.png',
	                'gallery/sprites/background-night.png']

# list of pipes
PIPES_LIST = ['gallery/sprites/pipe-blue.png',
              'gallery/sprites/pipe-darkblue.png']

try:   #
    xrange
except NameError:
    xrange = range

def main():
    global SCREEN, FPSCLOCK
    pygame.init()      #ฟังก์ชัน pygame.init () ซึ่งจะต้องเรียกใช้เสมอหลังจากนำเข้าโมดูล pygame และก่อนที่จะเรียกฟังก์ชัน Pygame อื่น ๆ มันต้องถูกเรียกใช้ก่อนเพื่อให้ฟังก์ชัน Pygame ทำงานได้ 
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) #ฟังก์ชัน set_mode () ความกว้างและความสูงในการสร้างหน้าต่างเป็นพิกเซล 
    pygame.display.set_caption('Flappy Hero') #ตั้งค่าข้อความ ที่จะปรากฏที่ด้านบนของหน้าต่าง

    # numbers sprites for score display
    IMAGES['numbers'] = (
    	pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('gallery/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()

    # sounds
    SOUNDS['die']    = pygame.mixer.Sound('gallery/audio/die.wav')
    SOUNDS['hit']    = pygame.mixer.Sound('gallery/audio/hit.wav')
    SOUNDS['point']  = pygame.mixer.Sound('gallery/audio/point.wav')
    SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    SOUNDS['wing']   = pygame.mixer.Sound('gallery/audio/wing.wav')

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )


        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = WelcomeScreen()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def WelcomeScreen():
    # Shows welcome images on the screen (แสดงภาพต้อนรับบนหน้าจอ) #
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them    
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,  
                }

        # adjust playery, playerIndex, basex   #loopIter = loop iteration(วนซ้ำ)
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0)) # set backgound image at position x=0 y=0
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update() # update screen changed
        FPSCLOCK.tick(FPS) # tell pygame that 1 frame has passed


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4 

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped (ความเร็วของ player )
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward accleration (ความเร่งของผู้เล่น)
    playerRot     =  45   # player's rotation (การหมุนของผู้เล่น)
    playerVelRot  =   3   # angular speed (ความเร็วเชิงมุม)
    playerRotThr  =  20   # rotation threshold (เกณฑ์การหมุน)
    playerFlapAcc =  -9   # players speed on flapping (ผู้เล่นความเร็วในการกระพือ)
    playerFlapped = False # True when player flaps


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}") 
                SOUNDS['point'].play()
 
        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement (การเคลื่อนไหวของผู้เล่น)
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left (เคลื่อนท่อไปทางซ้าย)
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # เพิ่มท่อใหม่ เมื่อท่อแรกกำลังจะแตะทางซ้ายของหน้าจอ
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # ลบท่อแรกออก ถ้าท่อเลื่อนออกจากหน้าจอทางซ้าย
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold 	(การหมุนของผู้เล่น)
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot) #rotate an image
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change (เปลี่ยนความเร็วของผู้เล่น)
        if playerVelY < 15:
            playerVelY += playerAccY


        # rotate only when it's a pipe crash (หมุนเมื่อชนท่อ)
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)


        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground (เช็คว่าผู้เล่นชนเข้ากับพื้นไหม)
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects   #pygame object for storing rectangular coordinates (จัดเก็บพิกัดสี่เหลี่ยม)
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:  
    #The int value of the width of the rectangle.
    #The int value of the height of the rectangle.
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
