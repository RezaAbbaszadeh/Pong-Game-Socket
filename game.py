import threading
import time
import socket
import pygame
import random
import encrypt

SIZE = 512
BALL_SPEED = 0.3
PLAYER_SPEED = 0.4

playerY = [200, 200]
right = random.choice([True, False])
down = random.choice([True, False])
controlBall = False  # true for client which should start the game. initially true for index0
BallX = 380
BallY = 230
readyShot = False  # when waiting for a player to start the game
point = [0, 0]
finished = False  # a player has 3 points
closed = False  # game closed completely
delay = 0
messageCount = 0  # number of received messages
receivedY = 0
ballreceivedY = 0

serverIP = input("Server IP: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverIP, 7856))
intro = s.recv(1024).decode("utf-8")
introarray = intro.split(",")
index = int(introarray[0])  # player index in server.  0 or 1
encryption = int(introarray[1])  # encryption type

if encryption == 1:  # symmetric
    sym = introarray[2]
    en = encrypt.Encrypt()
    en.addKey(sym)
elif encryption == 2:  # Asymmetric
    en = encrypt.Encrypt()
    en.GenerateAsymmetric()
    publicKey = en.getPublicKey()
    s.send(publicKey)
    oppPublicKeystr = s.recv(1024)
    oppPublicKey = en.getOppPublicKey(oppPublicKeystr)

if index == 0:
    controlBall = True


def Get():
    global right, closed, delay, messageCount, receivedY, ballreceivedY
    while True:
        try:
            msg = s.recv(SIZE)
            if encryption == 0:
                msg = msg.decode("utf-8")
            if encryption == 1:
                msg = en.decryptSym(msg).decode("utf-8")
            elif encryption == 2:
                msg = en.decryptAssymetric(msg).decode("utf-8")
            now = time.time()

            splitted = msg.split(',')

            if not controlBall:
                X = float(splitted[1][:5])
                Y = float(splitted[2][:5])
                ballreceivedY = Y
                threading.Thread(target=moveBallSmoothly, args=(X, Y,)).start()
                msgtime = float(splitted[3])
            else:
                msgtime = float(splitted[1])

            to_float = float(splitted[0][:5])  # get opponent Y
            op_index = 1 - index
            if 0 <= to_float <= 500:
                receivedY = to_float
                threading.Thread(target=moveSmoothly, args=(to_float, op_index,)).start()

            if msgtime > 1578262186:  # to ignore the faults
                delay = (delay * messageCount + now - msgtime) / (messageCount + 1)
                messageCount += 1
        except:
            if finished:
                print("Get finished")
                closed = True
                return False
            else:
                print("ERROR Get")


def moveSmoothly(y, index):
    global receivedY
    q = (y - playerY[index]) / 5
    playerY[index] += q
    for i in range(0, 4):
        if y != receivedY:
            break
        time.sleep(0.01)
        playerY[index] += q


def moveBallSmoothly(x, y):
    global BallX, BallY, ballreceivedY
    qx = (x - BallX) / 5
    qy = (y - BallY) / 5
    BallX += qx
    BallY += qy
    # if x>760 or x<40:
    #     cancelable = False
    # else:
    #     cancelable = True
    for i in range(0, 4):
        # if y != ballreceivedY and cancelable:
        #     break
        time.sleep(0.01)
        BallX += qx
        BallY += qy


def Send():
    global closed
    try:
        if controlBall:
            message = bytes(str(playerY[index])[:5] + "," + str(BallX) + "," + str(BallY) + "," + str(time.time()),
                            "utf-8")
            if encryption == 1:
                message = en.encryptSym(message)
            elif encryption == 2:
                message = en.encryptAsymmetric(message, oppPublicKey)
            s.send(message)
        else:
            message = bytes(str(playerY[index])[:5] + "," + str(time.time()), "utf-8")
            if encryption == 1:
                message = en.encryptSym(message)
            elif encryption == 2:
                message = en.encryptAsymmetric(message, oppPublicKey)
            s.send(message)
        if not finished:
            threading.Timer(0.05, Send).start()
        else:
            if not closed:
                print("Send finished")
                s.close()
                closed = True
            return
    except:
        if finished:
            print("Send finished")
            if not closed:
                s.close()
                closed = True
            return
        else:
            print("ERROR Send")


threadGet = threading.Thread(target=Get)
threadGet.start()
threadSend = threading.Timer(0.05, Send).start()

pygame.init()

screen = pygame.display.set_mode((800, 500))

pygame.display.set_caption("Pong")
icon = pygame.image.load('pong icon.png')
pygame.display.set_icon(icon)

playerImg = pygame.image.load('player.jpg')
playerX = [30, 750]
playerY_change = [0, 0]

BallImg = pygame.image.load('ball.png')
BallImg = pygame.transform.scale(BallImg, (40, 40))

score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
testY = 10


def show_score(x, y):
    score = font.render("Score : " + str(point[0]) + "-" + str(point[1]), True, (255, 255, 255))
    screen.blit(score, (x, y))


def player(x, y):
    screen.blit(playerImg, (x, y))


def ball(x, y):
    screen.blit(BallImg, (x, y))


def isCollision():
    if (50 >= BallX >= 49) and (-20 + playerY[0]) <= BallY <= (playerY[0] + 80):
        return True
    if (709 <= BallX <= 710) and (-20 + playerY[1]) <= BallY <= (playerY[1] + 80):
        return True


def CheckWinner():
    global BallX, index, controlBall, readyShot, right, finished

    if BallX < -40:
        point[1] += 1
        show_score(textX, testY)
        pygame.display.update()
        if point[1] == 3:
            if controlBall:
                time.sleep(2)
            finished = True
            print("finished")
        if controlBall:
            time.sleep(2)
        if index == 0:
            controlBall = True
            right = True
        else:
            controlBall = False
        readyShot = True

    if BallX > 800:
        point[0] += 1
        show_score(textX, testY)
        pygame.display.update()
        if point[0] == 3:
            if controlBall:
                time.sleep(2)
            finished = True
            print("finished")
        # if controlBall:
        if controlBall:
            time.sleep(2)
        if index == 1:
            controlBall = True
            right = False
        else:
            controlBall = False
        readyShot = True


while not finished:
    screen.fill((80, 80, 80))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
            closed = True
            s.close()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                playerY_change[index] = -PLAYER_SPEED
            if event.key == pygame.K_DOWN:
                playerY_change[index] = PLAYER_SPEED
            if event.key == pygame.K_SPACE and readyShot:
                down = random.choice([True, False])
                readyShot = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                playerY_change[index] = 0

    playerY[index] += playerY_change[index]
    if playerY[index] <= 0:
        playerY[index] = 0
    elif playerY[index] >= 400:
        playerY[index] = 400

    if controlBall:
        if not readyShot:
            collision = isCollision()
            if collision:
                right = not right
            if right:
                BallX += BALL_SPEED
            else:
                BallX -= BALL_SPEED
            if down:
                BallY += BALL_SPEED
            else:
                BallY -= BALL_SPEED

            if BallY <= 0 or BallY >= 460:
                down = not down
        else:
            if index == 0:
                BallX = playerX[index] + 21
            else:
                BallX = playerX[index] - 42
            BallY = playerY[index] + 30

    ball(BallX, BallY)
    player(playerX[0], playerY[0])
    player(playerX[1], playerY[1])

    if readyShot and (not controlBall) and ((index == 0 and BallX < 800) or (index == 1 and BallX > 0)):
        readyShot = False

    if not readyShot:
        CheckWinner()

    show_score(textX, testY)

    pygame.display.update()

print("Delay: " + str(delay))
