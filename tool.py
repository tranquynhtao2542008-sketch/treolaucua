#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  🚀 TREO CƯỢC TÀI XỈU - SIÊU AI - CHẠY LUÔN KHÔNG CẦN CÀI ║
║  🤖 AUTO BET - AI DỰ ĐOÁN - QUẢN LÝ VỐN                  ║
║  📊 GIAO DIỆN ĐẸP - MENU ĐIỀU KHIỂN - NHẬP OTP TRỰC TIẾP ║
║  💻 CHẠY: WINDOWS / MAC / LINUX / REPLIT                  ║
╚══════════════════════════════════════════════════════════════╝
"""
import subprocess
import sys
import os

# ==================== TỰ ĐỘNG CÀI THƯ VIỆN ====================
print(">>> Đang kiểm tra thư viện...")
LIBS = ['telethon', 'numpy', 'colorama']
for lib in LIBS:
    try:
        __import__(lib.replace('-', '_'))
        print(f"  ✓ {lib} đã có")
    except ImportError:
        print(f"  ⏳ Đang cài {lib}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "-q"])
        print(f"  ✓ {lib} đã cài xong")

print(">>> Tất cả thư viện đã sẵn sàng!\n")

import asyncio
import re
import json
import time
import random
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
from pathlib import Path

import numpy as np
from colorama import init, Fore, Back, Style
init(autoreset=True)
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, SessionPasswordNeededError

# ==================== MÀU SẮC ====================
class C:
    G = Fore.GREEN
    R = Fore.RED
    Y = Fore.YELLOW
    CY = Fore.CYAN
    M = Fore.MAGENTA
    W = Fore.WHITE
    D = Fore.LIGHTBLACK_EX
    LG = Fore.LIGHTGREEN_EX
    LR = Fore.LIGHTRED_EX
    LY = Fore.LIGHTYELLOW_EX
    LC = Fore.LIGHTCYAN_EX
    LM = Fore.LIGHTMAGENTA_EX
    BOLD = Style.BRIGHT
    RS = Style.RESET_ALL

# ==================== CONFIG ====================
PHONE = "+84346139930"
API_ID = 35742832
API_HASH = "93ac3807fede03197c86170865e01571"
CHANNEL = "@laucuataixiuroom"
BOT = "@laucua_tx_room_bot"
SESSION_FILE = "treo_session"

# ==================== CÀI ĐẶT ====================
class Config:
    def __init__(self):
        self.data = {
            'fixed_bet': 10000,
            'bet_percent': 5.0,
            'bet_mode': 'fixed',
            'bet_side': 'auto',
            'max_bets': 1,
            'min_confidence': 55,
            'wait_open': 8,
            'tp': 500000,
            'sl': 500000,
            'recovery': False,
            'auto_bet': True,
            'ai_enabled': True,
        }
        self.load()
    
    def load(self):
        try:
            with open('treo_config.json', 'r') as f:
                self.data.update(json.load(f))
        except:
            pass
    
    def save(self):
        with open('treo_config.json', 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value

CFG = Config()

# ==================== AI ====================
class AI:
    def __init__(self):
        self.h = deque(maxlen=5000)
        self.p = defaultdict(lambda: {'T':0,'X':0,'t':0})
        self.r = deque(maxlen=300)
        self.tp = 0
        self.cp = 0
        self._seed()
    
    def _seed(self):
        for _ in range(3):
            for v in ['T','X','T','T','X','T','X','X','T','T']:
                self.add(v)
    
    def add(self, v):
        if v not in ['T','X']: return
        self.h.append(v)
        s = list(self.h)
        for l in range(2, min(15, len(s))):
            for i in range(len(s)-l):
                pat = ''.join(s[i:i+l])
                if i+l < len(s):
                    self.p[pat][s[i+l]] += 1
                    self.p[pat]['t'] += 1
    
    def predict(self):
        if len(self.h) < 5:
            return {'s':'T','c':0.5,'lv':'THẤP'}
        
        s = list(self.h)
        sc = {'T':0.0,'X':0.0}
        tw = 0
        rs = []
        
        for l in range(min(14,len(s)), 2, -1):
            pat = ''.join(s[-l:])
            if pat in self.p and self.p[pat]['t'] >= 3:
                w = l/10.0
                t = self.p[pat]['t']
                for sd in ['T','X']:
                    sc[sd] += (self.p[pat][sd]/t)*w
                tw += w
        
        if tw > 0:
            for sd in sc: sc[sd] /= tw
            rs.append(f'{len(self.p)} mẫu')
        else:
            sc = {'T':0.5,'X':0.5}
        
        if len(s) >= 10:
            t10 = sum(1 for v in s[-10:] if v=='T')/10
            sc['T'] = sc['T']*0.7 + t10*0.3
            sc['X'] = sc['X']*0.7 + (1-t10)*0.3
            rs.append(f'Trend T:{t10:.0%}')
        
        last = s[-1]
        streak = 1
        for i in range(len(s)-2,-1,-1):
            if s[i]==last: streak+=1
            else: break
        
        if streak >= 6:
            opp = 'X' if last=='T' else 'T'
            sc[opp] += 0.2
            rs.append(f'Streak {streak} → đảo')
        
        if len(s) >= 12:
            t12 = sum(1 for v in s[-12:] if v=='T')
            if t12 >= 10 and sc['T'] > sc['X']:
                sc['X'] += 0.15
                rs.append('Anti-bias T')
            elif t12 <= 2 and sc['X'] > sc['T']:
                sc['T'] += 0.15
                rs.append('Anti-bias X')
        
        sd = 'T' if sc['T'] >= sc['X'] else 'X'
        cf = max(sc['T'], sc['X'])
        lv = 'CAO' if cf>=0.7 else 'TB' if cf>=0.6 else 'THẤP'
        
        return {'s':sd,'c':cf,'lv':lv,'rs':rs}
    
    def record(self, p, a):
        if p not in ['T','X'] or a not in ['T','X']: return
        self.tp += 1
        if p==a: self.cp += 1
        self.r.append(p==a)
    
    def acc(self, n=None):
        r = list(self.r)
        if n and len(r)>n: r = r[-n:]
        return sum(r)/len(r) if r else 0.5

# ==================== RISK ====================
class Risk:
    def __init__(self):
        self.cap = 1000000
        self.peak = self.cap
        self.cw = 0
        self.cl = 0
        self.ra = False
        self.rs = 0
        self.tt = 0
        self.wt = 0
    
    def upd(self, c):
        self.cap = c
        if c > self.peak: self.peak = c
    
    def bet(self, cf):
        if CFG.get('bet_mode') == 'fixed':
            amt = CFG.get('fixed_bet', 10000)
        else:
            base = int(self.cap * (CFG.get('bet_percent',5)/100))
            amt = int(base * (0.3 + cf*1.4))
        
        dd = self.dd()
        if dd > 0.25: amt = int(amt*0.2)
        elif dd > 0.15: amt = int(amt*0.5)
        elif dd > 0.1: amt = int(amt*0.7)
        
        if self.cl >= 5: amt = int(amt*0.1)
        elif self.cl >= 3: amt = int(amt*0.3)
        elif self.cl >= 2: amt = int(amt*0.5)
        
        if self.cw >= 5: amt = int(amt*1.3)
        elif self.cw >= 3: amt = int(amt*1.15)
        
        if self.ra and CFG.get('recovery') and self.rs < 3:
            amt = int(amt * (1.5 ** self.rs))
        
        return max(1000, min(amt, 10000000, int(self.cap*0.12)))
    
    def rec(self, won):
        self.tt += 1
        if won:
            self.wt += 1; self.cw += 1; self.cl = 0
            self.ra = False; self.rs = 0
        else:
            self.cl += 1; self.cw = 0
            if CFG.get('recovery') and self.rs < 3:
                if not self.ra: self.ra = True
                self.rs += 1
    
    def dd(self):
        return (self.peak-self.cap)/self.peak if self.peak>0 else 0
    
    def stop(self):
        r = []
        dd = self.dd()
        if dd >= 0.35: r.append(f'DD {dd:.1%}')
        if self.cl >= 6: r.append(f'{self.cl} thua')
        if self.cap < 1000: r.append('Hết vốn')
        profit = self.cap - 1000000
        if profit >= CFG.get('tp'): r.append(f'TP +{profit:,}đ')
        if profit <= -CFG.get('sl'): r.append(f'SL {profit:,}đ')
        return len(r)>0, ', '.join(r)

# ==================== DETECTOR ====================
class Detector:
    @staticmethod
    def detect(text):
        if not text: return None
        t = text.lower()
        
        if any(k in t for k in ['bắt đầu','mở cược','🎮','phiên mới','đã mở']):
            return {'t':'open'}
        if any(k in t for k in ['hết thời gian','đóng cược','⌛','hết giờ']):
            return {'t':'close'}
        if re.search(r'cược thành công|đã cược|🐯.*cược', text, re.I):
            r = {'t':'bet_ok'}
            if 'tài' in t: r['s']='T'
            if 'xỉu' in t: r['s']='X'
            return r
        if re.search(r'thắng|win|🎉', text, re.I) and '+' in text:
            return {'t':'win'}
        if re.search(r'thua|lose|😢', text, re.I) and '-' in text:
            return {'t':'loss'}
        if re.search(r'kết quả|📝', text, re.I):
            if re.search(r'tài.*thắng|thắng.*tài', text, re.I): return {'t':'result','w':'T'}
            if re.search(r'xỉu.*thắng|thắng.*xỉu', text, re.I): return {'t':'result','w':'X'}
            ht = 'tài' in t; hx = 'xỉu' in t
            if ht and not hx: return {'t':'result','w':'T'}
            if hx and not ht: return {'t':'result','w':'X'}
            return {'t':'result','w':None}
        m = re.search(r'số dư\s*:?\s*([\d.,]+)', text, re.I)
        if m:
            try: return {'t':'bal','a':int(m.group(1).replace('.','').replace(',',''))}
            except: pass
        return None

# ==================== ENGINE ====================
class Engine:
    def __init__(self, ai, risk, client):
        self.ai = ai; self.risk = risk; self.client = client
        self.ot = None; self.st = 'idle'
        self.ld = 95; self.od = deque(maxlen=30)
        self.bp = []; self.fu = None
        self.at = CFG.get('auto_bet')
        self.lp = None; self.bs = None
    
    def on_open(self):
        now = datetime.now()
        if self.ot:
            d = (now-self.ot).total_seconds()
            if 80<d<150:
                self.od.append(d)
                if len(self.od)>=3: self.ld = int(np.median(list(self.od)))
        self.ot = now; self.st = 'open'; self.bp = []
        self.bs = None; self.lp = self.ai.predict()
    
    def can_bet(self):
        if not self.at: return False,"Auto tắt"
        if self.st != 'open': return False,"Chưa mở"
        if len(self.bp) >= CFG.get('max_bets',1): return False,"Đủ"
        if self.fu and datetime.now() < self.fu:
            return False,f"Flood {(self.fu-datetime.now()).total_seconds():.0f}s"
        if not self.ot: return False,"Ko time"
        e = (datetime.now()-self.ot).total_seconds()
        r = self.ld - e
        if e < CFG.get('wait_open',8): return False,f"Đợi {int(CFG.get('wait_open',8)-e)}s"
        if r < 10: return False,f"Sắp đóng ({int(r)}s)"
        if e < self.ld*0.2: return False,"Chưa vùng vàng"
        return True,"OK"
    
    async def exec_bet(self, side, amt):
        if amt >= 1000000: cmd = f"/{side} {amt/1000000:.1f}m"
        elif amt >= 1000: cmd = f"/{side} {amt//1000}k"
        else: cmd = f"/{side} {amt}"
        try:
            await self.client.send_message(BOT, cmd)
            self.bp.append({'s':side,'a':amt})
            self.bs = 'pending'
            return True, cmd
        except FloodWaitError as e:
            self.fu = datetime.now()+timedelta(seconds=e.seconds)
            return False, f"Flood {e.seconds}s"
        except Exception as e:
            return False, str(e)
    
    def prog(self):
        if self.st=='open' and self.ot:
            return min(1.0,(datetime.now()-self.ot).total_seconds()/max(1,self.ld))
        return 0
    
    def rem(self):
        if self.st=='open' and self.ot:
            return max(0,int(self.ld-(datetime.now()-self.ot).total_seconds()))
        return 0

# ==================== TOOL ====================
class Tool:
    def __init__(self):
        self.ai = AI()
        self.risk = Risk()
        self.det = Detector()
        self.client = None
        self.eng = None
        
        self.active = False
        self.paused = False
        self.auto = CFG.get('auto_bet')
        self.st = datetime.now()
        self.sess = 0
        self.logs = deque(maxlen=200)
        
        self._load()
    
    def _load(self):
        try:
            with open('treo_state.json','r') as f:
                d = json.load(f)
            self.risk.cap = d.get('cap',1000000)
            self.risk.peak = d.get('peak',self.risk.cap)
            self.risk.tt = d.get('tt',0)
            self.risk.wt = d.get('wt',0)
        except: pass
    
    def _save(self):
        with open('treo_state.json','w') as f:
            json.dump({'cap':self.risk.cap,'peak':self.risk.peak,'tt':self.risk.tt,'wt':self.risk.wt},f)
    
    def log(self, msg, lv='info'):
        self.logs.append({'t':datetime.now().strftime('%H:%M:%S'),'m':msg,'l':lv})
        cc = {'info':C.D,'success':C.LG,'error':C.LR,'ai':C.LC,'bet':C.LM,'win':C.LG,'lose':C.LR}
        print(f"{cc.get(lv,C.D)}[{datetime.now():%H:%M:%S}] {msg}{C.RS}")
    
    def render(self):
        os.system('cls' if os.name=='nt' else 'clear')
        eng = self.eng
        pred = eng.lp if eng else None
        
        st = f"{C.LG}🤖 AUTO{C.RS}" if self.auto else f"{C.Y}🔧 MANUAL{C.RS}"
        if self.paused: st = f"{C.LR}⏸️ PAUSE{C.RS}"
        elif self.active: st = f"{C.LG}🟢 LIVE{C.RS} {st}"
        else: st = f"{C.D}🔴 WAIT{C.RS} {st}"
        
        profit = self.risk.cap - 1000000
        pc = C.LG if profit>=0 else C.LR
        dd = self.risk.dd()
        dc = C.LG if dd<0.1 else C.Y if dd<0.2 else C.LR
        wr = self.risk.wt/max(1,self.risk.tt)
        ai_acc = self.ai.acc(50)
        
        bm = CFG.get('bet_mode','fixed')
        if bm == 'fixed':
            bs = f"Cố định {CFG.get('fixed_bet',10000):,}đ"
        else:
            est = int(self.risk.cap*(CFG.get('bet_percent',5)/100))
            bs = f"{CFG.get('bet_percent',5)}% (~{est:,}đ)"
        
        ss = CFG.get('bet_side','auto')
        if ss == 'auto': ss = 'AI chọn'
        elif ss == 'T': ss = 'TÀI'
        else: ss = 'XỈU'
        
        rec = f"{C.LG}BẬT{C.RS}" if CFG.get('recovery') else f"{C.LR}TẮT{C.RS}"
        
        print(f"""
{C.CY}╔{'═'*60}╗{C.RS}
{C.CY}║{C.RS} {C.BOLD}🚀 TREO CƯỢC SIÊU AI - CHẠY LUÔN{C.RS}{' '*(60-40)}{C.CY}║{C.RS}
{C.CY}║{C.RS} {st} {C.D}⏱️ {str(datetime.now()-self.st).split('.')[0]}{C.RS}{' '*(60-35)}{C.CY}║{C.RS}
{C.CY}╠{'═'*60}╣{C.RS}""")
        
        if pred:
            sc = C.LG if pred['s']=='T' else C.LR
            print(f"{C.CY}║{C.RS} {C.W}🧠 AI:{C.RS} {sc}{pred['s']}{C.RS} {pred['c']:.0%} [{pred['lv']}]")
        
        if eng:
            p = eng.prog(); r = eng.rem()
            bar = self._bar(p)
            print(f"{C.CY}║{C.RS} {C.W}📊 Phiên:{C.RS} {bar} {C.LC}{p:.0%}{C.RS} Còn{C.Y}{r}s{C.RS} Đã đặt{len(eng.bp)}/{CFG.get('max_bets',1)}")
        
        print(f"{C.CY}╠{'═'*60}╣{C.RS}")
        print(f"{C.CY}║{C.RS} {C.W}💰 Vốn:{C.RS} {C.LG}{self.risk.cap:>12,}đ{C.RS} P/L:{pc}{profit:>10,}đ{C.RS} DD:{dc}{dd:>5.1%}{C.RS}")
        print(f"{C.CY}║{C.RS} {C.W}📈 Trades:{C.RS} {self.risk.tt} WR:{wr:.0%} Streak:W{self.risk.cw}/L{self.risk.cl} AI:{ai_acc:.0%}")
        print(f"{C.CY}╠{'═'*60}╣{C.RS}")
        print(f"{C.CY}║{C.RS} {C.W}⚙️ Tiền:{C.RS} {bs} | Cửa:{ss} | Recovery:{rec}")
        print(f"{C.CY}║{C.RS} {C.W}🎯 TP:{C.LG}{CFG.get('tp')//1000}k{C.RS} SL:{C.LR}{CFG.get('sl')//1000}k{C.RS}")
        
        for log in list(self.logs)[-4:]:
            c = {'success':C.LG,'error':C.LR,'ai':C.LC,'bet':C.LM}.get(log['l'],C.D)
            print(f"{C.CY}║{C.RS} {c}[{log['t']}] {log['m'][:55]}{C.RS}")
        
        print(f"{C.CY}╚{'═'*60}╝{C.RS}")
        print(f"\n{C.D}[1]Auto [2]Tiền [3]Cửa [4]TP/SL [5]Recovery [6]TT [7]Thoát{C.RS}")
        print(f"{C.D}Lệnh: /auto /tien 50k /side T /tp 500k /recovery /tt /his /help{C.RS}")
    
    def _bar(self, pct, w=18):
        pct = max(0,min(1,pct))
        f = int(pct*w)
        if pct>=0.7: return f"{C.LG}{'█'*f}{C.D}{'░'*(w-f)}{C.RS}"
        elif pct>=0.4: return f"{C.Y}{'█'*f}{C.D}{'░'*(w-f)}{C.RS}"
        else: return f"{C.LR}{'█'*f}{C.D}{'░'*(w-f)}{C.RS}"
    
    async def handle(self, text, src):
        if not text or self.paused: return
        info = self.det.detect(text)
        if not info: return
        t = info['t']
        
        if src == 'channel':
            if t == 'open':
                self.eng.on_open()
                self.active = True; self.sess += 1
                pred = self.eng.lp
                self.log(f"🔓 #{self.sess} | AI:{pred['s']} ({pred['c']:.0%})", 'ai')
                self.render()
                if self.auto: asyncio.create_task(self._auto())
            elif t == 'close':
                self.eng.st = 'closed'; self.active = False
                self.log("🔒 ĐÓNG", 'info'); self.render()
            elif t == 'result':
                self.eng.st = 'result'; self.active = False
                await self._result(info.get('w'))
        elif src == 'bot':
            if t == 'bet_ok':
                self.eng.bs = 'ok'
                self.log(f"✅ Cược {info.get('s','?')} OK", 'success'); self.render()
            elif t == 'win':
                self.eng.bs = 'won'
                self.log("🎉 THẮNG!", 'win'); self.render()
            elif t == 'loss':
                self.eng.bs = 'lost'
                self.log("💔 THUA!", 'lose'); self.render()
            elif t == 'bal':
                self.risk.upd(info.get('a',0))
    
    async def _result(self, w):
        if not w: self.render(); return
        self.ai.add(w)
        tpl = 0
        
        for b in self.eng.bp:
            won = w == b['s']
            amt = b['a']
            pl = int(amt*0.95) if won else -amt
            tpl += pl
            self.risk.rec(won)
            self.ai.record(b['s'], w)
        
        self.risk.upd(self.risk.cap + tpl)
        
        if self.eng.bp:
            ps = f"+{tpl:,}đ" if tpl>=0 else f"{tpl:,}đ"
            self.log(f"📊 KQ:{w} | {ps} | Vốn:{self.risk.cap:,}đ", 'win' if tpl>=0 else 'lose')
        
        stop, reason = self.risk.stop()
        if stop:
            self.log(f"🛑 DỪNG: {reason}", 'error')
            self.paused = True; self.auto = False
        
        self._save(); self.render()
    
    async def _auto(self):
        await asyncio.sleep(2)
        while self.active and not self.paused and self.auto:
            can, reason = self.eng.can_bet()
            if can:
                pred = self.eng.lp
                if pred and pred['c']*100 >= CFG.get('min_confidence',55):
                    side = pred['s'] if CFG.get('bet_side')=='auto' else CFG.get('bet_side','T')
                    amt = self.risk.bet(pred['c'])
                    ok, msg = await self.eng.exec_bet(side, amt)
                    self.log(f"{'✅' if ok else '❌'} {msg}", 'bet' if ok else 'error')
                    break
                else:
                    self.log("⏭️ Skip: conf thấp", 'error'); break
            else:
                if any(k in reason for k in ['Đủ','đóng','Flood']): break
                await asyncio.sleep(2)
        
        if self.active and not self.paused and self.auto:
            r = self.eng.rem()
            if 5<r<15 and len(self.eng.bp) < CFG.get('max_bets',1):
                pred = self.eng.lp
                if pred and pred['c']*100 >= CFG.get('min_confidence',55):
                    side = pred['s'] if CFG.get('bet_side')=='auto' else CFG.get('bet_side','T')
                    ok, msg = await self.eng.exec_bet(side, self.risk.bet(pred['c']))
                    self.log(f"🆘 FB: {msg}", 'bet' if ok else 'error')
        self.render()
    
    async def menu(self):
        print(f"{C.LC}>>> MENU ĐIỀU KHIỂN SẴN SÀNG{C.RS}")
        print(f"{C.D}>>> Nhập số hoặc lệnh, /help để xem menu{C.RS}")
        
        while True:
            try:
                cmd = input(f"{C.W}>>> {C.RS}").strip().lower()
                if not cmd: continue
                
                if cmd in ['1','/auto']:
                    self.auto = not self.auto
                    if self.eng: self.eng.at = self.auto
                    self.log(f"🤖 AUTO: {'BẬT' if self.auto else 'TẮT'}", 'ai')
                    self.render()
                
                elif cmd.startswith('/tien') or cmd == '2':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            amt = int(parts[-1].lower().replace('k','000').replace('m','000000'))
                            if amt == 0:
                                CFG.set('bet_mode','percent')
                                self.log(f"→ % vốn ({CFG.get('bet_percent',5)}%)", 'info')
                            else:
                                CFG.set('bet_mode','fixed')
                                CFG.set('fixed_bet', amt)
                                self.log(f"→ {amt:,}đ/lần", 'info')
                            CFG.save(); self.render()
                        except: print(f"{C.LR}Sai số{C.RS}")
                    else: print(f"{C.Y}VD: /tien 50000{C.RS}")
                
                elif cmd.startswith('/side') or cmd == '3':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        s = parts[-1].upper()
                        if s in ['T','X','AUTO']:
                            CFG.set('bet_side', s)
                            self.log(f"→ Cửa: {s}", 'info')
                            CFG.save(); self.render()
                        else: print(f"{C.LR}Chọn T, X hoặc auto{C.RS}")
                    else: print(f"{C.Y}VD: /side T{C.RS}")
                
                elif cmd.startswith('/tp') or cmd == '4':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            CFG.set('tp', int(parts[-1].lower().replace('k','000').replace('m','000000')))
                            self.log(f"→ TP: {CFG.get('tp'):,}đ", 'info')
                            CFG.save(); self.render()
                        except: print(f"{C.LR}Sai số{C.RS}")
                
                elif cmd.startswith('/sl'):
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            CFG.set('sl', int(parts[-1].lower().replace('k','000').replace('m','000000')))
                            self.log(f"→ SL: {CFG.get('sl'):,}đ", 'info')
                            CFG.save(); self.render()
                        except: print(f"{C.LR}Sai số{C.RS}")
                
                elif cmd in ['5','/recovery']:
                    CFG.set('recovery', not CFG.get('recovery'))
                    self.log(f"🔄 Recovery: {'BẬT' if CFG.get('recovery') else 'TẮT'}", 'info')
                    CFG.save(); self.render()
                
                elif cmd in ['6','/tt','/info']:
                    profit = self.risk.cap - 1000000
                    print(f"""
{C.CY}THÔNG TIN:{C.RS}
  Vốn: {C.LG}{self.risk.cap:,}đ{C.RS}
  Lãi/Lỗ: {C.LG if profit>=0 else C.LR}{profit:+,}đ{C.RS}
  DD: {self.risk.dd():.1%}
  Trades: {self.risk.tt} | WR: {self.risk.wt/max(1,self.risk.tt):.0%}
  Streak: W{self.risk.cw}/L{self.risk.cl}
  AI Acc: {self.ai.acc():.0%}
  Phiên: {self.sess}
                    """)
                
                elif cmd in ['7','/exit','quit']: break
                
                elif cmd in ['/his','/history']:
                    for log in list(self.logs)[-20:]:
                        c = {'success':C.LG,'error':C.LR,'ai':C.LC,'bet':C.LM}.get(log['l'],C.D)
                        print(f"  {c}[{log['t']}] {log['m']}{C.RS}")
                
                elif cmd in ['/help','/menu']:
                    print(f"""
{C.CY}╔{'═'*45}╗
║{C.BOLD}         📋 MENU ĐIỀU KHIỂN{C.RS}{C.CY}            ║
╠{'═'*45}╣
║ [1] /auto     - Bật/tắt tự động                {C.CY}║
║ [2] /tien 50k - Đặt tiền cố định               {C.CY}║
║ [3] /side T   - Chọn cửa T/X/auto              {C.CY}║
║ [4] /tp 500k  - Take profit                    {C.CY}║
║ [5] /recovery - Bật/tắt gấp thếp               {C.CY}║
║ [6] /tt       - Xem thông tin                  {C.CY}║
║ [7] /exit     - Thoát                          {C.CY}║
║     /his      - Xem lịch sử                    {C.CY}║
║     /save     - Lưu cấu hình                   {C.CY}║
╚{'═'*45}╝{C.RS}""")
                
                elif cmd == '/save':
                    self._save(); CFG.save()
                    print(f"{C.LG}💾 Đã lưu!{C.RS}")
                
                elif cmd == 'clear': self.render()
                else: print(f"{C.D}Không rõ lệnh. /help{C.RS}")
                
            except KeyboardInterrupt:
                print(f"\n{C.Y}Thoát...{C.RS}"); break
            except Exception as e:
                print(f"{C.LR}Lỗi: {e}{C.RS}")
    
    async def run(self):
        os.system('cls' if os.name=='nt' else 'clear')
        
        print(f"""
{C.CY}╔{'═'*55}╗
║  🚀 TREO CƯỢC SIÊU AI - CHẠY LUÔN                   ║
║  🤖 AUTO BET - AI DỰ ĐOÁN - NHẬP OTP TRỰC TIẾP    ║
╚{'═'*55}╝{C.RS}""")
        
        try:
            print(f"\n{C.Y}>>> ĐANG KẾT NỐI TELEGRAM...{C.RS}")
            self.client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print(f"{C.Y}>>> CHƯA ĐĂNG NHẬP - GỬI OTP ĐẾN {PHONE}{C.RS}")
                await self.client.send_code_request(PHONE)
                
                otp = input(f"{C.W}>>> NHẬP MÃ OTP (5 số từ Telegram): {C.RS}").strip()
                
                try:
                    await self.client.sign_in(PHONE, otp)
                except SessionPasswordNeededError:
                    pw = input(f"{C.W}>>> NHẬP MẬT KHẨU 2 LỚP: {C.RS}").strip()
                    await self.client.sign_in(password=pw)
            
            me = await self.client.get_me()
            self.log(f"Đăng nhập: {me.first_name} (@{me.username})", 'success')
            
            try:
                ch = await self.client.get_entity(CHANNEL)
                self.log(f"Kênh: {ch.title}", 'success')
            except:
                self.log(f"KHÔNG TÌM THẤY KÊNH: {CHANNEL}", 'error')
                self.log(f"Hãy tham gia kênh {CHANNEL} trước!", 'error')
                return
            
            self.eng = Engine(self.ai, self.risk, self.client)
            self.eng.at = self.auto
            
            @self.client.on(events.NewMessage(chats=ch))
            async def on_ch(event):
                try: await self.handle(event.message.text or '', 'channel')
                except: pass
            
            @self.client.on(events.NewMessage(chats=BOT))
            async def on_bot(event):
                try: await self.handle(event.message.text or '', 'bot')
                except: pass
            
            self.log("🚀 TOOL ĐÃ SẴN SÀNG!", 'success')
            self.render()
            
            await asyncio.gather(
                self.client.run_until_disconnected(),
                self.menu()
            )
            
        except KeyboardInterrupt:
            print(f"\n{C.Y}Dừng{C.RS}")
        except Exception as e:
            print(f"{C.LR}Lỗi: {e}{C.RS}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client: await self.client.disconnect()
            self._save(); CFG.save()
            print(f"{C.Y}Đã lưu{C.RS}")

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        asyncio.run(Tool().run())
    except KeyboardInterrupt:
        print(f"\n{C.Y}Done{C.RS}")
    except Exception as e:
        print(f"{C.LR}{e}{C.RS}")
