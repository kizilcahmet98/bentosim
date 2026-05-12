"""
bentosim.aquarium.entities — tüm canlı sınıfları.

Hiyerarşi:
    Entity (taban)
    ├── Fish        — 5-durumlu AI (SWIM/SPRINT/IDLE/TURN/SCHOOL)
    ├── Shark       — Hunt AI (en yakın balığa yönelir)
    ├── Whale       — Yavaş, fıskiye atar
    ├── Turtle      — SWIM/REST/RISE (yüzeye nefes için)
    ├── Crab        — Dash AI, yön değişimi
    ├── Octopus     — Mürekkep modu
    ├── Jellyfish   — Pulse animasyonu
    ├── Eel         — Çok-segmentli, dalgalı yüzme
    ├── MantaRay    — Yavaş, kanat çırpma
    └── Bubble      — Yukarı sallanma + wobble
"""

import math
import random

from ..core import cp, safeadd, lerp
from .art import (
    FISH_DB,
    SHARK_R, SHARK_L,
    WHALE_R, WHALE_L,
    TURTLE_R, TURTLE_L,
    CRAB_R, CRAB_L,
    OCTOPUS_FRAMES,
    EEL_R, EEL_L,
    RAY_R, RAY_L,
    JELLY_FRAMES,
    BUBBLE_CHARS,
    CORAL_DB, ANEMONE, STARFISH_ART,
    TREASURE_ART, ROCK_ART, SKULL_ART, ANCHOR_ART,
)


# ════════════════════════════════════════════════════════════════
#  TABAN SINIF
# ════════════════════════════════════════════════════════════════

class Entity:
    def __init__(self):
        self.dead = False

    def update(self, t, rows, cols, spd):
        pass

    def draw(self, win, theme, t):
        pass

    def emit_bubble(self):
        return None


def draw_art_spans(win, y, x, lines, spans, attr):
    """ASCII sanatın sadece opak kabul edilen yatay parçalarını çizer."""
    y = int(y)
    x = int(x)
    for i, (line, row_spans) in enumerate(zip(lines, spans)):
        for start, end in row_spans:
            safeadd(win, y + i, x + start, line[start:end], attr)


class Fish(Entity):
    SPD = {"S":(0.20,0.50), "M":(0.07,0.30), "L":(0.03,0.12), "X":(0.10,0.28)}

    # AI durumları
    ST_SWIM   = 0   # normal yüzme
    ST_SPRINT = 1   # kaçış
    ST_IDLE   = 2   # duraksama
    ST_TURN   = 3   # geri dönüş (yavaşla → dur → ters yön)
    ST_SCHOOL = 4   # sürü

    def __init__(self, cols, rows, spd_mult, theme, school_center=None):
        super().__init__()
        idx = random.randrange(len(FISH_DB))
        self.ar, self.al, sz, name = FISH_DB[idx]
        self.right = random.random() > 0.5
        self._set_art()
        self.x  = float(-self.W-10 if self.right else cols+self.W+10)
        self.base_y = float(random.randint(2, max(3, rows-5-self.H)))
        self.y  = self.base_y
        lo,hi = self.SPD.get(sz,(0.08,0.28))
        self.nom_spd = random.uniform(lo,hi) * spd_mult
        self.dx = self.nom_spd * (1 if self.right else -1)
        self.target_dx = self.dx
        self.phase= random.uniform(0, math.pi*2)
        self.amp  = random.uniform(0.1, 0.85)
        self.freq = random.uniform(0.02, 0.10)
        self.rgb  = random.choice(theme["fish"])
        self.bcd  = random.randint(8,40)
        # AI
        self.state    = self.ST_SWIM
        self.state_cd = random.randint(60,200)
        self.fear_cd  = 0
        self.turn_cd  = 0      # dönüş animasyonu süresi
        self.turn_phase = 0.0  # dönüş smooth geçiş (0→1)
        # Ekranda kalma ihtimali: çoğu balık geri dönebilir
        self.can_turn = random.random() < 0.85  # %85 geri dönebilir
        self.turn_chance = random.uniform(0.015, 0.04)  # her frame olasılık
        self.school_center = school_center
        self.size_cat = sz

    def _set_art(self):
        """Yön değişince ASCII sanatını güncelle."""
        self.lines = (self.ar if self.right else self.al).split("\n")
        self.W = max(len(l) for l in self.lines)
        self.H = len(self.lines)

    def _do_turn(self):
        """Yönü ters çevir, ASCII sanatını güncelle."""
        self.right = not self.right
        self._set_art()
        self.nom_spd = abs(self.nom_spd)
        self.dx = -self.dx  # anlık hızı da ters çevir

    def ai_tick(self, t, rows, cols, spd_mult, sharks):
        self.state_cd -= 1
        self.fear_cd  -= 1

        # Köpekbalığı korkusu → sprint + kaç (dönme ihtimali de var)
        for sh in sharks:
            dist = abs(self.x - sh.x) + abs(self.y - sh.y)
            if dist < 25:
                self.fear_cd = 80
                # Köpekbalığı aynı yönden geliyorsa → geri kaç
                shark_coming = (sh.right and sh.x < self.x) or \
                               (not sh.right and sh.x > self.x)
                if shark_coming and self.state != self.ST_TURN:
                    self.state = self.ST_SPRINT
                else:
                    self.state = self.ST_SPRINT
                break

        if self.fear_cd > 0:
            self.state = self.ST_SPRINT

        # Dönüş durumu yönetimi
        if self.state == self.ST_TURN:
            self.turn_cd -= 1
            self.turn_phase = min(1.0, self.turn_phase + 0.06)
            if self.turn_cd <= 0:
                # Dönüş tamamlandı, yüzmeye devam
                self.state = self.ST_SWIM
                self.state_cd = random.randint(60, 200)
                self.turn_phase = 0.0
            return  # dönüş sırasında başka state değişimi yok

        if self.state_cd <= 0:
            if self.state in (self.ST_SPRINT, self.ST_IDLE):
                self.state = self.ST_SWIM
            elif self.can_turn and random.random() < self.turn_chance * 40:
                # Rastgele geri dönüş kararı
                self._start_turn()
                return
            elif random.random() < 0.10:
                self.state = self.ST_IDLE
            self.state_cd = random.randint(40, 180)

        # Ekran kenarına yaklaşınca dönme ihtimali artar
        margin = cols * 0.15
        near_edge = (self.right and self.x > cols - margin) or \
                    (not self.right and self.x < margin)
        if near_edge and self.can_turn and self.state not in (self.ST_SPRINT, self.ST_TURN):
            edge_chance = 0.04 + (0.06 * (1.0 - min(1.0,
                abs(self.x - (cols if self.right else 0)) / margin)))
            if random.random() < edge_chance:
                self._start_turn()
                return

        # Hedef hız
        if self.state == self.ST_SPRINT:
            tspd = self.nom_spd * random.uniform(2.5, 3.5) * spd_mult
        elif self.state == self.ST_IDLE:
            tspd = self.nom_spd * 0.12 * spd_mult
        else:
            tspd = self.nom_spd * random.uniform(0.7, 1.3) * spd_mult

        self.target_dx = tspd * (1 if self.right else -1)

        # Sürü: merkeze doğru çek
        if self.school_center:
            cx, cy = self.school_center
            if abs(self.base_y - cy) > 3:
                self.base_y += (cy - self.base_y) * 0.01

    def _start_turn(self):
        """Dur → düşün → yön değiştir → hızlan animasyonunu başlat."""
        self.state    = self.ST_TURN
        # Dönüş 4 evrede: yavaşla(20-30) → dur(15-30) → dön+hızlan(20-30)
        self.turn_decel  = random.randint(20, 30)
        self.turn_pause  = random.randint(15, 30)
        self.turn_accel  = random.randint(20, 30)
        self.turn_cd     = self.turn_decel + self.turn_pause + self.turn_accel
        self.turn_phase  = 0.0
        # "Düşünme" sırasında yukarı-aşağı bakınma
        self.turn_glance = random.uniform(-0.4, 0.4)

    def update(self, t, rows, cols, spd_mult, sharks=None):
        if sharks is None: sharks = []
        self.ai_tick(t, rows, cols, spd_mult, sharks)

        if self.state == self.ST_TURN:
            # Hangi evredeyiz?
            elapsed = (self.turn_decel + self.turn_pause + self.turn_accel) - self.turn_cd
            if elapsed < self.turn_decel:
                # Evre 1: yavaşla (1.0 → 0.0)
                progress = elapsed / max(1, self.turn_decel)
                slow = 1.0 - progress
                actual_dx = self.target_dx * slow
                self.dx = lerp(self.dx, actual_dx, 0.10)
            elif elapsed < self.turn_decel + self.turn_pause:
                # Evre 2: durdu, "etrafa bakınıyor"
                self.dx = lerp(self.dx, 0.0, 0.25)
                # Y'de hafif bakınma
                self.base_y += math.sin(elapsed * 0.4) * self.turn_glance * 0.05
                # Pause ortasında yönü çevir
                pause_mid = self.turn_decel + self.turn_pause // 2
                if elapsed == pause_mid:
                    self._do_turn()
                    self.target_dx = self.nom_spd * (1 if self.right else -1) * spd_mult
            else:
                # Evre 3: hızlan (0.0 → 1.0, yeni yönde)
                accel_elapsed = elapsed - self.turn_decel - self.turn_pause
                progress = accel_elapsed / max(1, self.turn_accel)
                actual_dx = self.target_dx * progress
                self.dx = lerp(self.dx, actual_dx, 0.08)
        else:
            self.dx = lerp(self.dx, self.target_dx, 0.04)

        self.x += self.dx
        self.y = self.base_y + math.sin(t*self.freq*12 + self.phase)*self.amp
        self.y = max(2.0, min(float(rows-4-self.H), self.y))
        self.bcd -= 1

        # Ekran dışına çıkarsa öl (ama dönebilenleri biraz beklet)
        margin = 25 if self.can_turn else 20
        if self.x > cols + self.W + margin or self.x < -self.W - margin:
            self.dead = True

    def draw(self, win, theme, t):
        # Sprint = parlak, TURN = soluk (yavaşlama hissi)
        if self.state == self.ST_SPRINT:
            attr = cp(self.rgb, bold=True)
        elif self.state == self.ST_TURN:
            # Dönüş anında rengi kısa süre soldur
            dimmed = tuple(max(0, int(c * 0.6)) for c in self.rgb)
            attr = cp(dimmed)
        else:
            attr = cp(self.rgb)
        for i, line in enumerate(self.lines):
            safeadd(win, int(self.y)+i, int(self.x), line, attr)

    def emit_bubble(self):
        if self.bcd <= 0:
            self.bcd = random.randint(8,40)
            bx = self.x + (self.W-1 if self.right else 0)
            return Bubble(bx, self.y)
        return None

# ════════════════════════════════════════════════════════════════
#  KÖPEKBALIK
# ════════════════════════════════════════════════════════════════

SHARK_SPANS_R = [
    ((8, 11),),
    ((8, 12), (46, 48)),
    ((8, 13), (32, 61)),
    ((8, 65),),
    ((8, 68),),
    ((8, 62),),
    ((8, 18), (33, 41), (49, 54)),
    ((8, 12), (35, 37), (47, 51)),
    ((8, 11),),
]
SHARK_SPANS_L = [
    tuple((len(SHARK_R[0]) - end, len(SHARK_R[0]) - start)
          for start, end in row)
    for row in SHARK_SPANS_R
]


class Shark(Entity):
    ST_PATROL = 0
    ST_HUNT   = 1
    ST_TURN   = 2

    def __init__(self, cols, rows, spd_mult):
        super().__init__()
        self.right = random.random() > 0.5
        self.lines = SHARK_R if self.right else SHARK_L
        self.spans = SHARK_SPANS_R if self.right else SHARK_SPANS_L
        self.W = max(len(l) for l in self.lines)
        self.H = len(self.lines)
        self.x = float(-self.W-12 if self.right else cols+self.W+12)
        self.base_y = float(random.randint(2, max(3, rows-self.H-2)))
        self.y  = self.base_y
        self.nom_spd = random.uniform(0.10,0.38) * spd_mult
        self.dx = self.nom_spd * (1 if self.right else -1)
        self.target_y= self.base_y
        self.state   = self.ST_PATROL
        self.hunt_cd = random.randint(20,60)
        self.phase   = random.uniform(0,math.pi*2)

    def update(self, t, rows, cols, spd_mult, fishes=None):
        if fishes is None: fishes=[]
        # Av takibi
        self.hunt_cd -= 1
        if self.hunt_cd <= 0:
            if fishes:
                # En yakın balığı bul
                nearby = [f for f in fishes
                          if (self.right and f.x > self.x) or
                             (not self.right and f.x < self.x)]
                if nearby:
                    prey = min(nearby, key=lambda f: abs(f.y - self.y))
                    self.target_y = prey.y
                    self.state = self.ST_HUNT
                else:
                    self.target_y += random.uniform(-4,4)
                    self.state = self.ST_PATROL
            self.hunt_cd = random.randint(25,70)

        self.y = lerp(self.y, self.target_y, 0.025)
        self.y = max(2.0, min(float(rows-self.H-1), self.y))
        self.x += self.dx
        if self.x > cols+self.W+20 or self.x < -self.W-20:
            self.dead = True

    def draw(self, win, theme, t):
        attr = cp(theme["shark"], bold=True)
        draw_art_spans(win, self.y, self.x, self.lines, self.spans, attr)

# ════════════════════════════════════════════════════════════════
#  BALİNA
# ════════════════════════════════════════════════════════════════

WHALE_SPANS_R = [
    ((10, 15), (45, 50)),
    ((11, 14), (33, 58)),
    ((4, 17), (24, 59)),
    ((10, 60),),
    ((9, 59),),
    ((8, 54),),
    ((7, 52),),
    ((6, 10),),
    ((7, 9),),
]
WHALE_SPANS_L = [
    tuple((len(WHALE_R[0]) - end, len(WHALE_R[0]) - start)
          for start, end in row)
    for row in WHALE_SPANS_R
]


class Whale(Entity):
    def __init__(self, cols, rows, spd_mult):
        super().__init__()
        self.right = random.random() > 0.5
        self.lines = WHALE_R if self.right else WHALE_L
        self.spans = WHALE_SPANS_R if self.right else WHALE_SPANS_L
        self.W = max(len(l) for l in self.lines)
        self.x = float(-self.W-15 if self.right else cols+self.W+15)
        self.base_y = float(random.randint(3, max(4,rows-9)))
        self.y  = self.base_y
        self.dx = random.uniform(0.025,0.07)*spd_mult*(1 if self.right else -1)
        self.phase = random.uniform(0,math.pi*2)
        self.spout_cd = random.randint(60,140)

    def update(self, t, rows, cols, spd_mult):
        self.x += self.dx
        self.y = self.base_y + math.sin(t*0.025+self.phase)*0.7
        self.y = max(2.0, min(float(rows-9), self.y))
        self.spout_cd -= 1
        if self.x > cols+self.W+20 or self.x < -self.W-20:
            self.dead = True

    def emit_spout(self):
        if self.spout_cd <= 0:
            self.spout_cd = random.randint(60,140)
            sx = self.x + self.W//2
            return [Bubble(sx+dx, self.y-1) for dx in range(-2,3)]
        return []

    def draw(self, win, theme, t):
        attr = cp(theme["whale"], bold=True)
        draw_art_spans(win, self.y, self.x, self.lines, self.spans, attr)

# ════════════════════════════════════════════════════════════════
#  DENİZANASI
# ════════════════════════════════════════════════════════════════

class Jellyfish(Entity):
    def __init__(self, cols, rows):
        super().__init__()
        # Her denizanasının kendi pulsing renk döngüsü var
        self.x = float(random.randint(3, max(4,cols-12)))
        self.base_y = float(random.randint(2, max(3,rows-9)))
        self.y = self.base_y
        self.phase  = random.uniform(0,math.pi*2)
        self.dx     = random.uniform(-0.04,0.04)
        self.amp    = random.uniform(1.0,2.5)
        self.freq   = random.uniform(0.025,0.08)
        self.frame  = random.randint(0, len(JELLY_FRAMES)-1)
        self.fcd    = random.randint(8,18)
        self.ttl    = random.randint(600,1400)
        self.age    = 0
        self.pulse_t= 0.0   # renk pulse fazı

    def update(self, t, rows, cols, spd_mult=1.0):
        self.age += 1
        if self.age >= self.ttl: self.dead = True
        self.x += self.dx + math.sin(t*0.22+self.phase)*0.04
        self.y  = self.base_y + math.sin(t*self.freq+self.phase)*self.amp
        self.x  = max(1.0, min(float(cols-12), self.x))
        self.y  = max(2.0, min(float(rows-8), self.y))
        self.fcd -= 1
        if self.fcd <= 0:
            self.frame = (self.frame+1) % len(JELLY_FRAMES)
            self.fcd = random.randint(8,18)
        self.pulse_t += 0.05

    def draw(self, win, theme, t):
        # Pulsing parlaklık
        bright = (math.sin(self.pulse_t)*0.5+0.5)
        jc = theme["jelly"]
        dark_jc = tuple(max(0,int(c*0.4)) for c in jc)
        frame = JELLY_FRAMES[self.frame]
        for i,line in enumerate(frame):
            a = cp(jc, bold=True) if i <= 1 else cp(dark_jc, dim=True)
            safeadd(win, int(self.y)+i, int(self.x), line, a)

# ════════════════════════════════════════════════════════════════
#  KAPLUMBAĞA
# ════════════════════════════════════════════════════════════════

class Turtle(Entity):
    ST_SWIM  = 0
    ST_REST  = 1
    ST_RISE  = 2   # nefes almak için yüzeye çıkma

    def __init__(self, cols, rows, spd_mult):
        super().__init__()
        self.right = random.random() > 0.5
        self.lines = TURTLE_R if self.right else TURTLE_L
        self.W = max(len(l) for l in self.lines)
        self.x = float(-self.W-8 if self.right else cols+self.W+8)
        self.base_y = float(random.randint(3, max(4,rows-7)))
        self.y = self.base_y
        self.dx = random.uniform(0.02,0.09)*spd_mult*(1 if self.right else -1)
        self.phase = random.uniform(0,math.pi*2)
        self.state = self.ST_SWIM
        self.state_cd = random.randint(150,400)
        self.bcd = random.randint(20,60)

    def update(self, t, rows, cols, spd_mult):
        self.state_cd -= 1
        if self.state_cd <= 0:
            choices = [self.ST_SWIM, self.ST_REST, self.ST_RISE]
            weights = [0.6, 0.25, 0.15]
            self.state = random.choices(choices, weights=weights)[0]
            self.state_cd = random.randint(80,250)
            if self.state == self.ST_RISE:
                self.base_y = max(2.0, self.base_y - random.uniform(2,5))

        if self.state != self.ST_REST:
            self.x += self.dx
        # Su dalgası hareketi
        self.y = self.base_y + math.sin(t*0.045+self.phase)*0.6
        self.y = max(2.0, min(float(rows-7), self.y))

        if self.state == self.ST_RISE and self.base_y > 3:
            self.base_y = lerp(self.base_y, 3.0, 0.01)
        elif self.state == self.ST_SWIM:
            # Orijinal derinliğe geri dön
            orig = float(random.randint(4,max(5,rows-7)))
            self.base_y = lerp(self.base_y, orig, 0.002)

        self.bcd -= 1
        if self.x > cols+self.W+15 or self.x < -self.W-15:
            self.dead = True

    def emit_bubble(self):
        if self.bcd <= 0:
            self.bcd = random.randint(20,60)
            return Bubble(self.x+2, self.y)
        return None

    def draw(self, win, theme, t):
        attr = cp(theme["turtle"], bold=True)
        for i,line in enumerate(self.lines):
            safeadd(win, int(self.y)+i, int(self.x), line, attr)

# ════════════════════════════════════════════════════════════════
#  YENGEÇ
# ════════════════════════════════════════════════════════════════

class Crab(Entity):
    def __init__(self, cols, rows, spd_mult):
        super().__init__()
        self.right = random.random() > 0.5
        self.x = float(random.randint(2, max(3,cols-10)))
        self.y = float(rows-4)
        base_spd = random.uniform(0.04,0.14)*spd_mult
        self.dx = base_spd*(1 if self.right else -1)
        self.nom_spd = base_spd
        self.frame = 0; self.fcd = random.randint(10,20)
        self.dir_cd = random.randint(60,140)
        self.dash_cd = random.randint(80,220); self.dashing=False; self.dash_t=0
        self.ttl = random.randint(350,900); self.age=0

    def update(self, t, rows, cols, spd_mult):
        self.age += 1
        if self.age >= self.ttl: self.dead = True
        # Dash AI
        self.dash_cd -= 1
        if self.dash_cd<=0 and not self.dashing:
            self.dashing=True; self.dash_t=random.randint(12,28)
            self.dx=abs(self.dx)*3*(1 if self.right else -1)
            self.dash_cd=random.randint(80,220)
        if self.dashing:
            self.dash_t-=1
            if self.dash_t<=0:
                self.dashing=False
                self.dx=self.nom_spd*spd_mult*(1 if self.right else -1)
        # Yön değişimi
        self.dir_cd-=1
        if self.dir_cd<=0:
            self.right=not self.right
            self.dx=abs(self.dx)*(1 if self.right else -1)
            self.dir_cd=random.randint(60,140)
        self.x+=self.dx
        self.x=max(1.0,min(float(cols-10),self.x))
        self.fcd-=1
        if self.fcd<=0: self.frame^=1; self.fcd=random.randint(10,20)
        self.y=float(rows-4)  # kumda kal

    def draw(self, win, theme, t):
        attr=cp(theme["crab"],bold=True)
        frames=CRAB_R if self.right else CRAB_L
        for i,line in enumerate(frames[self.frame]):
            safeadd(win,int(self.y)+i,int(self.x),line,attr)

# ════════════════════════════════════════════════════════════════
#  AHTAPOT
# ════════════════════════════════════════════════════════════════

class Octopus(Entity):
    def __init__(self, cols, rows):
        super().__init__()
        self.x = float(random.randint(4,max(5,cols-12)))
        self.base_y = float(random.randint(3,max(4,rows-8)))
        self.y = self.base_y
        self.dx = random.uniform(-0.035,0.035)
        self.phase = random.uniform(0,math.pi*2)
        self.frame=0; self.fcd=random.randint(12,25)
        self.ttl=random.randint(500,1100); self.age=0
        # "mürekkep" patlaması
        self.ink_cd=random.randint(200,500); self.inking=False; self.ink_t=0

    def update(self, t, rows, cols, spd_mult=1.0):
        self.age+=1
        if self.age>=self.ttl: self.dead=True
        self.x+=self.dx+math.sin(t*0.18+self.phase)*0.06
        self.y=self.base_y+math.sin(t*0.06+self.phase)*1.1
        self.x=max(2.0,min(float(cols-12),self.x))
        self.y=max(2.0,min(float(rows-7),self.y))
        self.fcd-=1
        if self.fcd<=0: self.frame=(self.frame+1)%2; self.fcd=random.randint(12,25)
        self.ink_cd-=1
        if self.ink_cd<=0 and not self.inking:
            self.inking=True; self.ink_t=30
            self.ink_cd=random.randint(200,500)
        if self.inking:
            self.ink_t-=1
            if self.ink_t<=0: self.inking=False

    def draw(self, win, theme, t):
        col = theme["octo"] if not self.inking else tuple(max(0,c-80) for c in theme["octo"])
        attr=cp(col,bold=True)
        frame=OCTOPUS_FRAMES[self.frame]
        for i,line in enumerate(frame):
            safeadd(win,int(self.y)+i,int(self.x),line,attr)

# ════════════════════════════════════════════════════════════════
#  YILAN BALIĞI
# ════════════════════════════════════════════════════════════════

class Eel(Entity):
    def __init__(self, cols, rows, spd_mult):
        super().__init__()
        self.right = random.random()>0.5
        base = EEL_R[0] if self.right else EEL_L[0]
        # Dinamik uzunluk
        seg = random.randint(2,5)
        self.art = base * seg if self.right else base * seg
        self.W = len(self.art)
        self.x = float(-self.W-5 if self.right else cols+self.W+5)
        self.base_y = float(random.randint(3,max(4,rows-6)))
        self.y = self.base_y
        self.dx = random.uniform(0.06,0.18)*spd_mult*(1 if self.right else -1)
        self.phase = random.uniform(0,math.pi*2)

    def update(self, t, rows, cols, spd_mult):
        self.x += self.dx
        self.y = self.base_y + math.sin(t*0.07+self.phase)*1.5
        self.y = max(2.0,min(float(rows-5),self.y))
        if self.x>cols+self.W+10 or self.x<-self.W-10: self.dead=True

    def draw(self, win, theme, t):
        attr=cp(theme["eel"],bold=True)
        safeadd(win,int(self.y),int(self.x),self.art,attr)

# ════════════════════════════════════════════════════════════════
#  IŞIN BALIĞI (MANTA RAY)
# ════════════════════════════════════════════════════════════════

class MantaRay(Entity):
    def __init__(self, cols, rows, spd_mult):
        super().__init__()
        self.right=random.random()>0.5
        self.lines=RAY_R if self.right else RAY_L
        self.W=max(len(l) for l in self.lines)
        self.x=float(-self.W-8 if self.right else cols+self.W+8)
        self.base_y=float(random.randint(3,max(4,rows-8)))
        self.y=self.base_y
        self.dx=random.uniform(0.04,0.14)*spd_mult*(1 if self.right else -1)
        self.phase=random.uniform(0,math.pi*2)

    def update(self, t, rows, cols, spd_mult):
        self.x+=self.dx
        self.y=self.base_y+math.sin(t*0.04+self.phase)*2.0
        self.y=max(2.0,min(float(rows-8),self.y))
        if self.x>cols+self.W+15 or self.x<-self.W-15: self.dead=True

    def draw(self, win, theme, t):
        attr=cp(theme["ray_fish"],bold=True)
        for i,line in enumerate(self.lines):
            safeadd(win,int(self.y)+i,int(self.x),line,attr)

# ════════════════════════════════════════════════════════════════
#  KABARCIK
# ════════════════════════════════════════════════════════════════

class Bubble(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.x=float(x)+random.uniform(-1.5,1.5)
        self.y=float(y)
        self.char=random.choice(BUBBLE_CHARS)
        self.dy=-random.uniform(0.07,0.22)
        self.wobble=random.uniform(0,math.pi*2)
        self.age=0

    def update(self, t, rows, cols, spd_mult=1.0):
        self.y+=self.dy
        self.x+=math.sin(t*5+self.wobble)*0.06
        self.age+=1
        if self.y<1.5: self.dead=True

    def draw(self, win, theme, t):
        fade_attr=cp(theme["bubble"],dim=True)
        safeadd(win,int(self.y),int(self.x),self.char,fade_attr)

# ════════════════════════════════════════════════════════════════
#  ZEMİN DEKORASYON
# ════════════════════════════════════════════════════════════════

class BottomDecor:
    def __init__(self, cols, rows):
        self.items=[]
        n=min(16,max(5,cols//8))
        positions=sorted(random.sample(range(2,cols-10),min(n,cols-14)))
        pool=["coral"]*5+["star"]*2+["treasure"]*1+["rock"]*2+["skull"]*1+["anchor"]*1+["anemone"]*2
        random.shuffle(pool)
        for i,px in enumerate(positions):
            k=pool[i%len(pool)]
            if k=="coral":        art=random.choice(CORAL_DB)
            elif k=="anemone":    art=random.choice(ANEMONE)
            elif k=="star":       art=STARFISH_ART
            elif k=="treasure":   art=TREASURE_ART
            elif k=="skull":      art=SKULL_ART
            elif k=="anchor":     art=ANCHOR_ART
            else:                 art=ROCK_ART
            y=rows-3-len(art)
            self.items.append((k,px,y,art))

    def draw(self, win, theme, t):
        cmap={
            "coral":    theme["coral"],
            "anemone":  theme["jelly"],
            "star":     theme["star"],
            "treasure": theme["treasure"],
            "skull":    (200,200,200),
            "anchor":   (150,160,170),
            "rock":     theme["rock"],
        }
        for kind,px,sy,art in self.items:
            rgb=cmap.get(kind,theme["coral"])
            bold=(kind in ("treasure","star"))
            pulse=kind in ("anemone",)
            if pulse:
                v=math.sin(t*0.08)*0.3+0.7
                rgb=tuple(int(c*v) for c in rgb)
            attr=cp(rgb,bold=bold)
            for i,line in enumerate(art):
                safeadd(win,sy+i,px,line,attr)
