import pygame
import sys
import time
pygame.init()
WIDTH, HEIGHT = 360,360  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame 終極九宮格")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
can_GREEN=(204, 255, 0)
RED=(255,0,0)
BLUE=(0,0,255)
running = True
screen.fill((255, 255, 255))
pygame.draw.line(screen,BLACK,(120,0),(120,360),5);
pygame.draw.line(screen,BLACK,(240,0),(240,360),5);
pygame.draw.line(screen,BLACK,(0,120),(360,120),5);
pygame.draw.line(screen,BLACK,(0,240),(360,240),5);
for i in range(3):
    for j in range(3):
        pygame.draw.line(screen,BLACK,(0+i*120,40+j*120),(120+i*120,40+j*120),2);
        pygame.draw.line(screen,BLACK,(0+i*120,80+j*120),(120+i*120,80+j*120),2);
        pygame.draw.line(screen,BLACK,(40+i*120,0+j*120),(40+i*120,120+j*120),2);
        pygame.draw.line(screen,BLACK,(80+i*120,0+j*120),(80+i*120,120+j*120),2);
pygame.display.update()
choice = 0
play = 0
can_fill=[2,2,2,2,2,2,2,2,2]
each_squ=[[2 for j in range(9)] for i in range(9)]

def X_win():
    pygame.display.update()
    screen.fill((255, 255, 255))
    time.sleep(2.0)
    pygame.display.update()
    font = pygame.font.Font(None, 80)
    text = font.render("X win", True, RED)
    text_rect = text.get_rect(center=(180, 180))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(2.0)
    pygame.quit()
    sys.exit()

def O_win():
    pygame.display.update()
    screen.fill((255, 255, 255))
    time.sleep(2.0)
    pygame.display.update()
    font = pygame.font.Font(None, 80)
    text = font.render("O win", True, BLUE)
    text_rect = text.get_rect(center=(180, 180))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(2.0)
    pygame.quit()
    sys.exit()

def tie():
    pygame.display.update()
    screen.fill((255, 255, 255))
    time.sleep(2.0)
    pygame.display.update()
    font = pygame.font.Font(None, 80)
    text = font.render("Tie", True, BLACK)
    text_rect = text.get_rect(center=(180, 180))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(2.0)
    pygame.quit()
    sys.exit()

while running :
    if (choice) :
        for i in range(3):
            for j in range(3):
                if (each_squ[((choice-1)//3)*3 + i][((choice-1)%3)*3 + j]==2):
                    pygame.draw.rect(screen, can_GREEN, (10+(((choice-1)%3)*3 + j)*40, 10+(((choice-1)//3)*3 + i)*40, 20, 20))
    else :
        for i in range(9):
            for j in range(9):
                if (each_squ[i][j]==2):
                    pygame.draw.rect(screen, can_GREEN, (10+j*40, 10+i*40, 20, 20))        
    pygame.display.update()
    while True:
        nex=0
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if ((each_squ[y//40][x//40]==2) and (((y//120)*3 + x//120 + 1 == choice) or ( choice == 0) )):
                    for i in range (9):
                        for j in range(9):
                            if (each_squ[i][j]==2):
                                pygame.draw.rect(screen, WHITE, (10+j*40, 10+i*40, 20, 20))
                    a=y//40
                    b=x//40
                    if play==0:
                        pygame.draw.circle(screen,BLUE,(20+b*40, 20+a*40), 15, 3)
                        each_squ[a][b]=0
                    else :
                        pygame.draw.line(screen,RED,(5+b*40, 5+a*40),(35+b*40, 35+a*40) , 3)
                        pygame.draw.line(screen,RED,(5+b*40, 35+a*40),(35+b*40, 5+a*40) , 3)
                        each_squ[a][b]=1
                    pygame.display.update()
                    nex=1
                    c = (a%3)*3 + (b%3) + 1
                    d = ((a//3)*3 + (b//3))
                    can_fill[d]=can_fill[d]+1
                    for i in range(3):
                        if each_squ[(d//3)*3+i][(d%3)*3] == play and each_squ[(d//3)*3+i][(d%3)*3+1] == play and each_squ[(d//3)*3+i][(d%3)*3+2] == play :
                            pygame.draw.rect(screen, WHITE, (3+(d%3)*120, 3+(d//3)*120, 114, 114))
                            if play==0:
                                pygame.draw.circle(screen,BLUE,(60+(d%3)*120, 60+(d//3)*120), 50, 8)
                            else :
                                pygame.draw.line(screen,RED,(10+(d%3)*120, 10+(d//3)*120),(110+(d%3)*120, 110+(d//3)*120) , 8)
                                pygame.draw.line(screen,RED,(10+(d%3)*120, 110+(d//3)*120),(110+(d%3)*120, 10+(d//3)*120) , 8) 
                            can_fill[d]=play
                        elif each_squ[(d//3)*3][(d%3)*3+i] == play and each_squ[(d//3)*3+1][(d%3)*3+i] == play and each_squ[(d//3)*3+2][(d%3)*3+i] == play :
                            pygame.draw.rect(screen, WHITE, (3+(d%3)*120, 3+(d//3)*120, 114, 114))
                            if play==0:
                                pygame.draw.circle(screen,BLUE,(60+(d%3)*120, 60+(d//3)*120), 50, 8)
                            else :
                                pygame.draw.line(screen,RED,(10+(d%3)*120, 10+(d//3)*120),(110+(d%3)*120, 110+(d//3)*120) , 8)
                                pygame.draw.line(screen,RED,(10+(d%3)*120, 110+(d//3)*120),(110+(d%3)*120, 10+(d//3)*120) , 8)
                            can_fill[d]=play
                    if each_squ[(d//3)*3][(d%3)*3] == play and each_squ[(d//3)*3+1][(d%3)*3+1] == play and each_squ[(d//3)*3+2][(d%3)*3+2] == play :
                        pygame.draw.rect(screen, WHITE, (3+(d%3)*120, 3+(d//3)*120, 114, 114))
                        if play==0:
                            pygame.draw.circle(screen,BLUE,(60+(d%3)*120, 60+(d//3)*120), 50, 8)
                        else :
                            pygame.draw.line(screen,RED,(10+(d%3)*120, 10+(d//3)*120),(110+(d%3)*120, 110+(d//3)*120) , 8)
                            pygame.draw.line(screen,RED,(10+(d%3)*120, 110+(d//3)*120),(110+(d%3)*120, 10+(d//3)*120) , 8)
                        can_fill[d]=play
                    elif each_squ[(d//3)*3+2][(d%3)*3] == play and each_squ[(d//3)*3+1][(d%3)*3+1] == play and each_squ[(d//3)*3][(d%3)*3+2] == play :
                        pygame.draw.rect(screen, WHITE, (3+(d%3)*120, 3+(d//3)*120, 114, 114))
                        if play==0:
                            pygame.draw.circle(screen,BLUE,(60+(d%3)*120, 60+(d//3)*120), 50, 8)
                        else :
                            pygame.draw.line(screen,RED,(10+(d%3)*120, 10+(d//3)*120),(110+(d%3)*120, 110+(d//3)*120) , 8)
                            pygame.draw.line(screen,RED,(10+(d%3)*120, 110+(d//3)*120),(110+(d%3)*120, 10+(d//3)*120) , 8)
                        can_fill[d]=play
                    pygame.display.update()
                    if (can_fill[d]<2):
                        for i in range(3):
                            for j in range(3):
                                each_squ[(d//3)*3+i][(d%3)*3+j]=can_fill[d]
                    if can_fill[c-1]>=2 and can_fill[c-1]<11:
                        choice=c
                    else :
                        choice=0
                    break
                    
        if nex == 1:
            for i in range(3):
                if can_fill[0+3*i]==1 and can_fill[1+3*i]==1 and can_fill[2+3*i]==1 :
                    X_win()
                if can_fill[0+3*i]==0 and can_fill[1+3*i]==0 and can_fill[2+3*i]==0 :
                    O_win()
                if can_fill[0+i]==1 and can_fill[3+i]==1 and can_fill[6+i]==1 :
                    X_win()
                if can_fill[0+i]==0 and can_fill[3+i]==0 and can_fill[6+i]==0 :
                    O_win()
            if can_fill[0]==1 and can_fill[4]==1 and can_fill[8]==1 :
                X_win()
            if can_fill[2]==1 and can_fill[4]==1 and can_fill[6]==1 :
                X_win()
            if can_fill[0]==0 and can_fill[4]==0 and can_fill[8]==0 :
                O_win()
            if can_fill[2]==0 and can_fill[4]==0 and can_fill[6]==0 :
                O_win()
            fa=0
            for i in range(9):
                if can_fill[i]<2 or can_fill[i]==11:
                    fa+=1
            if fa==9:
                tie()
            break
    play = 1 - play
