import pygame, random, json, os, math

# COSMOS GAME 60.0 - single-file Pydroid 3 game
pygame.init()
pygame.display.set_caption('SULTAN HIMMAT - COSMOS GAME 60.0')
info = pygame.display.Info()
W = max(360, info.current_w)
H = max(600, info.current_h)
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

WHITE=(245,248,255); CYAN=(50,220,255); BLUE=(35,90,210); GOLD=(255,205,55)
RED=(255,75,95); GREEN=(70,245,150); DARK=(5,9,28); PURPLE=(155,90,255)
FONT=pygame.font.Font(None, max(24, int(H*.035)))
SMALL=pygame.font.Font(None, max(18, int(H*.026)))
BIG=pygame.font.Font(None, max(42, int(H*.075)))
SAVE='cosmos_game_60_save.json'

def load_save():
    try:
        with open(SAVE,'r') as f: return json.load(f)
    except: return {'coins':0,'best':0,'ship':0,'weapon':1,'owned':[0]}
data=load_save()
def save():
    try:
        with open(SAVE,'w') as f: json.dump(data,f)
    except: pass

def text(s, x, y, font=FONT, color=WHITE, center=True):
    img=font.render(str(s), True, color)
    rect=img.get_rect(center=(int(x),int(y))) if center else img.get_rect(topleft=(int(x),int(y)))
    screen.blit(img,rect)

def button(label, rect, color=BLUE, font=FONT):
    pygame.draw.rect(screen,color,rect,border_radius=14)
    pygame.draw.rect(screen,CYAN,rect,2,border_radius=14)
    text(label,rect.centerx,rect.centery,font)

def new_stars():
    return [[random.randrange(W),random.randrange(H),random.choice([1,1,2,3])] for _ in range(85)]
stars=new_stars()
def background():
    screen.fill(DARK)
    for i,(x,y,r) in enumerate(stars):
        pygame.draw.circle(screen,(80,100,160), (int(x),int(y)),r)
        y += r+1
        if y>H: y=0; x=random.randrange(W)
        stars[i]=[x,y,r]

def ship_draw(x,y,scale=1,color=CYAN):
    pts=[(x,y-24*scale),(x-17*scale,y+18*scale),(x,y+10*scale),(x+17*scale,y+18*scale)]
    pygame.draw.polygon(screen,color,pts)
    pygame.draw.polygon(screen,WHITE,pts,2)
    pygame.draw.circle(screen,GOLD,(int(x),int(y+2*scale)),max(2,int(4*scale)))

state='menu'; player_x=W//2; player_y=int(H*.77); bullets=[]; enemies=[]; coins=[]; particles=[]
score=0; level=1; hp=3; shield=0; nova=0; spawn_timer=0; fire_timer=0; boss_hp=0; boss=None
left=False; right=False; firing=False; message=''; message_time=0
btn_size=max(58,int(W*.15))
left_rect=pygame.Rect(18,H-btn_size-20,btn_size,btn_size)
right_rect=pygame.Rect(28+btn_size,H-btn_size-20,btn_size,btn_size)
fire_rect=pygame.Rect(W-btn_size-18,H-btn_size-20,btn_size,btn_size)
shield_rect=pygame.Rect(W-btn_size-18,H-2*btn_size-35,btn_size,btn_size)

def start_game():
    global state,player_x,bullets,enemies,coins,score,level,hp,shield,nova,spawn_timer,fire_timer,boss,boss_hp
    state='play'; player_x=W//2; bullets=[]; enemies=[]; coins=[]; score=0; level=1; hp=3; shield=0; nova=0; spawn_timer=0; fire_timer=0; boss=None; boss_hp=0

def end_game():
    global state
    data['coins']+=score//10
    data['best']=max(data.get('best',0),score)
    save(); state='failed'

def draw_hud():
    text('SCORE '+str(score),W*.22,28,SMALL,WHITE)
    text('LEVEL '+str(level),W*.50,28,SMALL,CYAN)
    text('HP '+str(hp),W*.78,28,SMALL,RED if hp==1 else WHITE)
    text('COINS '+str(data['coins']),W*.5,58,SMALL,GOLD)

def menu_screen():
    text('SULTAN HIMMAT',W/2,H*.19,BIG,CYAN)
    text('VERSION 60.0',W/2,H*.26,FONT,GOLD)
    ship_draw(W/2,H*.38,2.2)
    bw=int(W*.72); bh=max(48,int(H*.075)); x=(W-bw)//2
    button('START MISSION',pygame.Rect(x,int(H*.49),bw,bh),BLUE)
    button('SHIP HANGAR',pygame.Rect(x,int(H*.59),bw,bh),PURPLE)
    button('WEAPON LAB',pygame.Rect(x,int(H*.69),bw,bh), (25,135,100))
    button('HOW TO PLAY',pygame.Rect(x,int(H*.79),bw,bh), (70,75,115))
    text('Best score: '+str(data.get('best',0)),W/2,H*.91,SMALL)

def hangar_screen():
    text('SHIP HANGAR',W/2,65,BIG,CYAN)
    ships=[('Scout',0,CYAN),('Viper',80,GREEN),('Phoenix',160,GOLD),('Titan',250,PURPLE)]
    for i,(name,cost,col) in enumerate(ships):
        yy=int(H*.22)+i*int(H*.14)
        rect=pygame.Rect(int(W*.12),yy,int(W*.76),int(H*.105))
        pygame.draw.rect(screen,(20,30,65),rect,border_radius=12); pygame.draw.rect(screen,col,rect,2,border_radius=12)
        text(name+'  '+('OWNED' if i in data['owned'] else str(cost)+' coins'),W*.5,yy+rect.height*.35,SMALL)
        text('SELECTED' if data['ship']==i else ('TAP TO BUY/SELECT'),W*.5,yy+rect.height*.72,SMALL,GOLD if data['ship']==i else WHITE)
    button('BACK',pygame.Rect(W*.25,H-int(H*.11),W*.5,int(H*.075)),BLUE)

def weapon_screen():
    text('WEAPON LAB',W/2,H*.22,BIG,CYAN)
    text('Weapon level: '+str(data['weapon']),W/2,H*.38,FONT)
    text('Upgrade cost: '+str(data['weapon']*100)+' coins',W/2,H*.46,SMALL,GOLD)
    button('UPGRADE',pygame.Rect(W*.2,H*.55,W*.6,H*.09),(25,135,100))
    button('BACK',pygame.Rect(W*.25,H*.72,W*.5,H*.08),BLUE)

def game_buttons():
    for r,label,col in [(left_rect,'◀',(25,65,125)),(right_rect,'▶',(25,65,125)),(fire_rect,'FIRE',(145,35,65)),(shield_rect,'NOVA',(95,45,155))]:
        pygame.draw.rect(screen,col,r,border_radius=14); pygame.draw.rect(screen,CYAN,r,2,border_radius=14); text(label,r.centerx,r.centery,SMALL)

def draw_play():
    for b in bullets:
        pygame.draw.rect(screen,CYAN,(int(b[0]-3),int(b[1]-10),6,16),border_radius=3)
    for e in enemies:
        pygame.draw.circle(screen,RED,(int(e[0]),int(e[1])),int(e[2]))
        pygame.draw.circle(screen,GOLD,(int(e[0]),int(e[1])),max(3,int(e[2]*.35)))
    for c in coins:
        pygame.draw.circle(screen,GOLD,(int(c[0]),int(c[1])),9); pygame.draw.circle(screen,WHITE,(int(c[0]),int(c[1])),9,2)
    if boss:
        pygame.draw.rect(screen,PURPLE,(boss[0]-45,boss[1]-22,90,44),border_radius=8)
        pygame.draw.rect(screen,RED,(W*.2,75,W*.6,9))
        pygame.draw.rect(screen,GREEN,(W*.2,75,W*.6*max(0,boss_hp/20),9))
    ship_draw(player_x,player_y,1.15, GOLD if shield>0 else CYAN)
    if shield>0: pygame.draw.circle(screen,CYAN,(int(player_x),int(player_y)),34,2)
    draw_hud(); game_buttons()

running=True
while running:
    dt=clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                if state=='play': state='pause'
                elif state=='pause': state='play'
            if state=='play':
                if event.key in (pygame.K_LEFT,pygame.K_a): left=True
                if event.key in (pygame.K_RIGHT,pygame.K_d): right=True
                if event.key in (pygame.K_SPACE,pygame.K_UP): firing=True
                if event.key==pygame.K_x and nova<=0: nova=3.0; shield=2.0; enemies.clear()
        elif event.type==pygame.KEYUP:
            if event.key in (pygame.K_LEFT,pygame.K_a): left=False
            if event.key in (pygame.K_RIGHT,pygame.K_d): right=False
            if event.key in (pygame.K_SPACE,pygame.K_UP): firing=False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            pos=event.pos
            if state=='menu':
                bw=int(W*.72); x=(W-bw)//2; bh=max(48,int(H*.075))
                if pygame.Rect(x,int(H*.49),bw,bh).collidepoint(pos): start_game()
                elif pygame.Rect(x,int(H*.59),bw,bh).collidepoint(pos): state='hangar'
                elif pygame.Rect(x,int(H*.69),bw,bh).collidepoint(pos): state='weapon'
                elif pygame.Rect(x,int(H*.79),bw,bh).collidepoint(pos): state='help'
            elif state=='hangar':
                if pos[1]>H-int(H*.12): state='menu'
                else:
                    i=int((pos[1]-int(H*.22))/int(H*.14))
                    ships=[('Scout',0),('Viper',80),('Phoenix',160),('Titan',250)]
                    if 0<=i<len(ships):
                        name,cost=ships[i]
                        if i in data['owned']: data['ship']=i
                        elif data['coins']>=cost: data['coins']-=cost; data['owned'].append(i); data['ship']=i
                        save()
            elif state=='weapon':
                if pygame.Rect(W*.2,H*.55,W*.6,H*.09).collidepoint(pos):
                    cost=data['weapon']*100
                    if data['coins']>=cost: data['coins']-=cost; data['weapon']+=1; save()
                elif pos[1]>H*.68: state='menu'
            elif state=='help': state='menu'
            elif state=='failed': state='menu'
            elif state=='pause':
                if pos[1]<H*.58: state='play'
                else: state='menu'
            elif state=='play':
                if left_rect.collidepoint(pos): left=True
                elif right_rect.collidepoint(pos): right=True
                elif fire_rect.collidepoint(pos): firing=True
                elif shield_rect.collidepoint(pos) and nova<=0: nova=5; shield=2; enemies.clear()
        elif event.type==pygame.MOUSEBUTTONUP:
            left=right=firing=False
        elif event.type==pygame.FINGERDOWN:
            pos=(int(event.x*W),int(event.y*H))
            if state=='play':
                if left_rect.collidepoint(pos): left=True
                elif right_rect.collidepoint(pos): right=True
                elif fire_rect.collidepoint(pos): firing=True
                elif shield_rect.collidepoint(pos) and nova<=0: nova=5; shield=2; enemies.clear()
            elif state=='menu':
                if pos[1]<H*.57: start_game()
                elif pos[1]<H*.67: state='hangar'
                elif pos[1]<H*.77: state='weapon'
                else: state='help'
        elif event.type==pygame.FINGERUP: left=right=firing=False

    background()
    if state=='menu': menu_screen()
    elif state=='hangar': hangar_screen()
    elif state=='weapon': weapon_screen()
    elif state=='help':
        text('HOW TO PLAY',W/2,H*.2,BIG,CYAN)
        text('Move with LEFT / RIGHT buttons',W/2,H*.38,SMALL)
        text('Hold FIRE to shoot enemies',W/2,H*.46,SMALL)
        text('NOVA clears enemies and gives shield',W/2,H*.54,SMALL)
        text('Collect gold coins for upgrades',W/2,H*.62,SMALL)
        button('BACK',pygame.Rect(W*.25,H*.76,W*.5,H*.08),BLUE)
        if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[1]>H*.72: state='menu'
    elif state=='pause':
        text('PAUSED',W/2,H*.35,BIG,GOLD)
        button('RESUME',pygame.Rect(W*.2,H*.48,W*.6,H*.09),BLUE)
        button('MAIN MENU',pygame.Rect(W*.2,H*.62,W*.6,H*.09),PURPLE)
    elif state=='failed':
        text('MISSION FAILED',W/2,H*.3,BIG,RED)
        text('Score: '+str(score),W/2,H*.42,FONT)
        text('Best: '+str(data.get('best',0)),W/2,H*.49,SMALL,GOLD)
        button('MAIN MENU',pygame.Rect(W*.2,H*.61,W*.6,H*.09),BLUE)
        button('PLAY AGAIN',pygame.Rect(W*.2,H*.73,W*.6,H*.09),(25,135,100))
        if pygame.mouse.get_pressed()[0]:
            pos=pygame.mouse.get_pos()
            if pygame.Rect(W*.2,H*.73,W*.6,H*.09).collidepoint(pos): start_game()
    elif state=='play':
        if left: player_x-=W*.55*dt
        if right: player_x+=W*.55*dt
        player_x=max(24,min(W-24,player_x))
        shield=max(0,shield-dt); nova=max(0,nova-dt)
        fire_timer-=dt
        if firing and fire_timer<=0:
            for k in range(min(4,data['weapon'])): bullets.append([player_x+(k-(min(4,data['weapon'])-1)/2)*9,player_y-20])
            fire_timer=max(.09,.24-data['weapon']*.015)
        for b in bullets: b[1]-=H*.9*dt
        bullets=[b for b in bullets if b[1]>-20]
        spawn_timer-=dt
        if spawn_timer<=0:
            spawn_timer=max(.25,1.0-level*.035)
            if level%5==0 and boss is None: boss=[W/2,125]; boss_hp=20
            else: enemies.append([random.randint(25,W-25),-20,random.randint(13,20),random.uniform(H*.16,H*.27)])
        for e in enemies: e[1]+=e[3]*dt
        for c in coins: c[1]+=H*.18*dt
        for b in bullets[:]:
            hit=False
            for e in enemies[:]:
                if math.hypot(b[0]-e[0],b[1]-e[1])<e[2]+5:
                    if e in enemies: enemies.remove(e)
                    if b in bullets: bullets.remove(b)
                    score+=10; hit=True
                    if random.random()<.25: coins.append([e[0],e[1]])
                    break
            if boss and not hit and abs(b[0]-boss[0])<50 and abs(b[1]-boss[1])<30:
                boss_hp-=1
                if b in bullets: bullets.remove(b)
                if boss_hp<=0: boss=None; score+=100; level+=1; coins.append([W/2,125])
        for e in enemies[:]:
            if e[1]>H-120:
                enemies.remove(e)
                if shield<=0: hp-=1
            elif math.hypot(player_x-e[0],player_y-e[1])<e[2]+18:
                enemies.remove(e)
                if shield<=0: hp-=1
        for c in coins[:]:
            if math.hypot(player_x-c[0],player_y-c[1])<30:
                coins.remove(c); data['coins']+=5; save()
            elif c[1]>H: coins.remove(c)
        if score>=level*150: level+=1
        if hp<=0: end_game()
        draw_play()
    pygame.display.flip()

save(); pygame.quit()
