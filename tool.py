#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  🚀 TREO CƯỢC TÀI XỈU - SIÊU AI - FULL TÍNH NĂNG         ║
║  🤖 AUTO BET - AI DỰ ĐOÁN - QUẢN LÝ VỐN                  ║
║  📊 GIAO DIỆN ĐẸP - MENU ĐIỀU KHIỂN                      ║
║  💻 CHẠY ĐƯỢC TRÊN: WINDOWS / MAC / REPLIT / RENDER      ║
╚══════════════════════════════════════════════════════════════╝
"""
import asyncio
import re
import json
import os
import sys
import time
import random
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== CÀI ĐẶT TỰ ĐỘNG ====================
def install_libs():
    libs = ['telethon', 'numpy', 'colorama']
    for lib in libs:
        try:
            __import__(lib.replace('-', '_'))
        except ImportError:
            os.system(f"{sys.executable} -m pip install {lib} -q")

install_libs()

import numpy as np
from colorama import init, Fore, Back, Style
init(autoreset=True)
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

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

# ==================== CONFIG MẶC ĐỊNH ====================
DEFAULT_CONFIG = {
    'phone': '+84346139930',
    'api_id': 35742832,
    'api_hash': '93ac3807fede03197c86170865e01571',
    'channel': '@laucuataixiuroom',
    'bot': '@laucua_tx_room_bot',
    'session_string': '',
    'bet_mode': 'fixed',
    'fixed_bet': 10000,
    'bet_percent': 5.0,
    'min_bet': 1000,
    'max_bet': 10000000,
    'max_bets_per_session': 1,
    'min_confidence': 55.0,
    'wait_after_open': 8,
    'golden_start': 20,
    'golden_end': 60,
    'max_drawdown': 35,
    'max_consecutive_loss': 6,
    'take_profit': 500000,
    'stop_loss': 500000,
    'recovery_enabled': False,
    'recovery_multiplier': 1.5,
    'recovery_max_steps': 3,
    'auto_bet': True,
    'ai_enabled': True,
    'bet_side': 'auto',
    'capital': 1000000,
}

class Config:
    def __init__(self):
        self.data = {}
        self.load()
    
    def load(self):
        try:
            if Path('config.json').exists():
                with open('config.json', 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
        except:
            self.data = {}
    
    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        return self.data.get(key, DEFAULT_CONFIG.get(key, default))
    
    def set(self, key, value):
        self.data[key] = value
    
    def reset(self):
        self.data = {}
        self.save()

CFG = Config()

# ==================== AI ENGINE ====================
class SuperAI:
    def __init__(self):
        self.history = deque(maxlen=5000)
        self.patterns = defaultdict(lambda: {'T': 0, 'X': 0, 'total': 0})
        self.results = deque(maxlen=300)
        self.total_pred = 0
        self.correct_pred = 0
        self._init_seed()
    
    def _init_seed(self):
        for _ in range(3):
            for v in ['T', 'X', 'T', 'T', 'X', 'T', 'X', 'X', 'T', 'T']:
                self.add(v)
    
    def add(self, value):
        if value not in ['T', 'X']:
            return
        self.history.append(value)
        seq = list(self.history)
        for length in range(2, min(18, len(seq))):
            for i in range(len(seq) - length):
                pattern = ''.join(seq[i:i+length])
                if i + length < len(seq):
                    self.patterns[pattern][seq[i+length]] += 1
                    self.patterns[pattern]['total'] += 1
    
    def predict(self):
        if len(self.history) < 5:
            return {'side': 'T', 'confidence': 0.5, 'level': 'THẤP', 'reasons': []}
        
        seq = list(self.history)
        scores = {'T': 0.0, 'X': 0.0}
        reasons = []
        
        # Pattern matching
        for length in range(min(15, len(seq)), 2, -1):
            pattern = ''.join(seq[-length:])
            if pattern in self.patterns and self.patterns[pattern]['total'] >= 3:
                weight = length / 12.0
                total = self.patterns[pattern]['total']
                for side in ['T', 'X']:
                    scores[side] += (self.patterns[pattern][side] / total) * weight
        
        # Normalize scores
        total = scores['T'] + scores['X']
        if total > 0:
            scores['T'] /= total
            scores['X'] /= total
            reasons.append('Pattern match')
        else:
            scores = {'T': 0.5, 'X': 0.5}
        
        # Trend analysis
        if len(seq) >= 15:
            recent = seq[-15:]
            t_ratio = sum(1 for v in recent if v == 'T') / 15
            scores['T'] = scores['T'] * 0.7 + t_ratio * 0.3
            scores['X'] = scores['X'] * 0.7 + (1 - t_ratio) * 0.3
            reasons.append(f'Trend T:{t_ratio:.0%}')
        
        # Streak analysis
        last = seq[-1]
        streak = 1
        for i in range(len(seq)-2, -1, -1):
            if seq[i] == last:
                streak += 1
            else:
                break
        
        if streak >= 6:
            opposite = 'X' if last == 'T' else 'T'
            scores[opposite] += 0.2
            reasons.append(f'Streak {streak} → đảo')
        elif streak >= 3:
            reasons.append(f'Streak {streak}')
        
        # Anti-bias
        if len(seq) >= 12:
            recent_12 = seq[-12:]
            t_count = sum(1 for v in recent_12 if v == 'T')
            if t_count >= 10 and scores['T'] > scores['X']:
                scores['X'] += 0.15
                reasons.append('Anti-bias T')
            elif t_count <= 2 and scores['X'] > scores['T']:
                scores['T'] += 0.15
                reasons.append('Anti-bias X')
        
        # Final decision
        side = 'T' if scores['T'] >= scores['X'] else 'X'
        confidence = max(scores['T'], scores['X'])
        
        if confidence >= 0.75:
            level = 'CAO'
        elif confidence >= 0.60:
            level = 'TRUNG BÌNH'
        else:
            level = 'THẤP'
        
        return {
            'side': side,
            'confidence': confidence,
            'level': level,
            'reasons': reasons,
            'scores': scores
        }
    
    def record(self, predicted, actual):
        if predicted not in ['T', 'X'] or actual not in ['T', 'X']:
            return
        self.total_pred += 1
        if predicted == actual:
            self.correct_pred += 1
        self.results.append(predicted == actual)
    
    def accuracy(self, n=None):
        r = list(self.results)
        if n and len(r) > n:
            r = r[-n:]
        return sum(r) / len(r) if r else 0.5

# ==================== RISK MANAGER ====================
class RiskManager:
    def __init__(self):
        self.capital = CFG.get('capital', 1000000)
        self.peak = self.capital
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.recovery_active = False
        self.recovery_step = 0
        self.total_trades = 0
        self.winning_trades = 0
    
    def update_capital(self, new_capital):
        self.capital = new_capital
        if new_capital > self.peak:
            self.peak = new_capital
    
    def calculate_bet(self, confidence):
        if CFG.get('bet_mode') == 'fixed':
            amount = CFG.get('fixed_bet', 10000)
        else:
            base = int(self.capital * (CFG.get('bet_percent', 5) / 100))
            amount = int(base * (0.3 + confidence * 1.4))
        
        # Drawdown protection
        dd = self.get_drawdown()
        if dd > 0.25:
            amount = int(amount * 0.2)
        elif dd > 0.15:
            amount = int(amount * 0.5)
        elif dd > 0.10:
            amount = int(amount * 0.7)
        
        # Consecutive loss protection
        if self.consecutive_losses >= 5:
            amount = int(amount * 0.1)
        elif self.consecutive_losses >= 3:
            amount = int(amount * 0.3)
        elif self.consecutive_losses >= 2:
            amount = int(amount * 0.5)
        
        # Win streak boost
        if self.consecutive_wins >= 5:
            amount = int(amount * 1.3)
        elif self.consecutive_wins >= 3:
            amount = int(amount * 1.15)
        
        # Recovery mode
        if self.recovery_active and CFG.get('recovery_enabled'):
            if self.recovery_step < CFG.get('recovery_max_steps', 3):
                amount = int(amount * (CFG.get('recovery_multiplier', 1.5) ** self.recovery_step))
        
        return max(CFG.get('min_bet', 1000), min(amount, CFG.get('max_bet', 10000000), int(self.capital * 0.12)))
    
    def record_trade(self, won):
        self.total_trades += 1
        if won:
            self.winning_trades += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.recovery_active = False
            self.recovery_step = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            if CFG.get('recovery_enabled') and self.recovery_step < CFG.get('recovery_max_steps', 3):
                if not self.recovery_active:
                    self.recovery_active = True
                self.recovery_step += 1
    
    def get_drawdown(self):
        if self.peak <= 0:
            return 0
        return (self.peak - self.capital) / self.peak
    
    def should_stop(self):
        reasons = []
        dd = self.get_drawdown()
        if dd >= CFG.get('max_drawdown', 35) / 100:
            reasons.append(f'DD {dd:.1%}')
        if self.consecutive_losses >= CFG.get('max_consecutive_loss', 6):
            reasons.append(f'{self.consecutive_losses} thua liên tiếp')
        if self.capital < CFG.get('min_bet', 1000):
            reasons.append('Hết vốn')
        profit = self.capital - CFG.get('capital', 1000000)
        if profit >= CFG.get('take_profit', 500000):
            reasons.append(f'Đạt TP +{profit:,}đ')
        if profit <= -CFG.get('stop_loss', 500000):
            reasons.append(f'Chạm SL {profit:,}đ')
        return len(reasons) > 0, ', '.join(reasons)

# ==================== DETECTOR ====================
class Detector:
    @staticmethod
    def detect(text):
        if not text:
            return None
        
        t = text.lower()
        
        if any(k in t for k in ['bắt đầu', 'mở cược', '🎮', 'phiên mới', 'đã mở']):
            return {'type': 'open'}
        
        if any(k in t for k in ['hết thời gian', 'đóng cược', '⌛', 'hết giờ', 'đã đóng']):
            return {'type': 'close'}
        
        if re.search(r'cược thành công|đã cược|🐯.*cược', text, re.I):
            r = {'type': 'bet_success'}
            if 'tài' in t: r['side'] = 'T'
            if 'xỉu' in t: r['side'] = 'X'
            return r
        
        if re.search(r'thắng|win|chúc mừng|🎉', text, re.I) and '+' in text:
            return {'type': 'win'}
        
        if re.search(r'thua|lose|😢|❌', text, re.I) and '-' in text:
            return {'type': 'loss'}
        
        if re.search(r'kết quả|📝', text, re.I):
            if re.search(r'tài.*thắng|thắng.*tài', text, re.I): return {'type': 'result', 'winner': 'T'}
            if re.search(r'xỉu.*thắng|thắng.*xỉu', text, re.I): return {'type': 'result', 'winner': 'X'}
            has_t = 'tài' in t
            has_x = 'xỉu' in t
            if has_t and not has_x: return {'type': 'result', 'winner': 'T'}
            if has_x and not has_t: return {'type': 'result', 'winner': 'X'}
            return {'type': 'result', 'winner': None}
        
        m = re.search(r'số dư\s*:?\s*([\d.,]+)', text, re.I)
        if m:
            try: return {'type': 'balance', 'amount': int(m.group(1).replace('.','').replace(',',''))}
            except: pass
        
        return None

# ==================== ENGINE ====================
class Engine:
    def __init__(self, ai, risk, client):
        self.ai = ai
        self.risk = risk
        self.client = client
        self.open_time = None
        self.state = 'idle'
        self.learned_duration = 95
        self.open_durations = deque(maxlen=30)
        self.bets_placed = []
        self.flood_until = None
        self.auto_trade = CFG.get('auto_bet', True)
        self.last_prediction = None
        self.bet_status = None
    
    def on_open(self):
        now = datetime.now()
        if self.open_time:
            d = (now - self.open_time).total_seconds()
            if 80 < d < 150:
                self.open_durations.append(d)
                if len(self.open_durations) >= 3:
                    self.learned_duration = int(np.median(list(self.open_durations)))
        self.open_time = now
        self.state = 'open'
        self.bets_placed = []
        self.bet_status = None
        self.last_prediction = self.ai.predict()
    
    def can_bet(self):
        if not self.auto_trade:
            return False, "Auto tắt"
        if self.state != 'open':
            return False, "Chưa mở phiên"
        if len(self.bets_placed) >= CFG.get('max_bets_per_session', 1):
            return False, "Đã đủ số lần"
        if self.flood_until and datetime.now() < self.flood_until:
            w = (self.flood_until - datetime.now()).total_seconds()
            return False, f"Flood {w:.0f}s"
        if not self.open_time:
            return False, "Không có thời gian"
        
        elapsed = (datetime.now() - self.open_time).total_seconds()
        remaining = self.learned_duration - elapsed
        
        if elapsed < CFG.get('wait_after_open', 8):
            return False, f"Đợi {int(CFG.get('wait_after_open', 8) - elapsed)}s"
        if remaining < 10:
            return False, f"Sắp đóng ({int(remaining)}s)"
        
        golden = self.learned_duration * (CFG.get('golden_start', 20) / 100)
        if elapsed < golden:
            return False, "Chưa đến vùng vàng"
        
        return True, "OK"
    
    async def execute_bet(self, side, amount):
        if amount >= 1000000:
            cmd = f"/{side} {amount/1000000:.1f}m"
        elif amount >= 1000:
            cmd = f"/{side} {amount//1000}k"
        else:
            cmd = f"/{side} {amount}"
        
        try:
            await self.client.send_message(CFG.get('bot'), cmd)
            self.bets_placed.append({
                'side': side,
                'amount': amount,
                'time': datetime.now().isoformat()
            })
            self.bet_status = 'pending'
            return True, cmd
        except FloodWaitError as e:
            self.flood_until = datetime.now() + timedelta(seconds=e.seconds)
            return False, f"Flood {e.seconds}s"
        except Exception as e:
            return False, str(e)
    
    def progress(self):
        if self.state == 'open' and self.open_time:
            return min(1.0, (datetime.now() - self.open_time).total_seconds() / max(1, self.learned_duration))
        return 0
    
    def remaining(self):
        if self.state == 'open' and self.open_time:
            return max(0, int(self.learned_duration - (datetime.now() - self.open_time).total_seconds()))
        return 0

# ==================== TOOL CHÍNH ====================
class Tool:
    def __init__(self):
        self.ai = SuperAI()
        self.risk = RiskManager()
        self.detector = Detector()
        self.client = None
        self.engine = None
        
        self.active = False
        self.paused = False
        self.auto_mode = CFG.get('auto_bet', True)
        self.start_time = datetime.now()
        self.session_count = 0
        self.logs = deque(maxlen=200)
        
        Path('dl').mkdir(exist_ok=True)
        self._load_state()
    
    def _load_state(self):
        try:
            if Path('dl/state.json').exists():
                with open('dl/state.json', 'r') as f:
                    d = json.load(f)
                self.risk.capital = d.get('capital', self.risk.capital)
                self.risk.peak = d.get('peak', self.risk.capital)
                self.risk.total_trades = d.get('trades', 0)
                self.risk.winning_trades = d.get('wins', 0)
        except:
            pass
    
    def _save_state(self):
        with open('dl/state.json', 'w') as f:
            json.dump({
                'capital': self.risk.capital,
                'peak': self.risk.peak,
                'trades': self.risk.total_trades,
                'wins': self.risk.winning_trades
            }, f)
    
    def log(self, msg, level='info'):
        self.logs.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'msg': msg,
            'level': level
        })
        colors = {
            'info': C.D, 'success': C.LG, 'error': C.LR,
            'ai': C.LC, 'bet': C.LM, 'win': C.LG, 'lose': C.LR
        }
        print(f"{colors.get(level, C.D)}[{datetime.now():%H:%M:%S}] {msg}{C.RS}")
    
    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        eng = self.engine
        pred = eng.last_prediction if eng else None
        
        status = f"{C.LG}🤖 AUTO{C.RS}" if self.auto_mode else f"{C.Y}🔧 MANUAL{C.RS}"
        if self.paused:
            status = f"{C.LR}⏸️ PAUSED{C.RS}"
        elif self.active:
            status = f"{C.LG}🟢 LIVE{C.RS} {status}"
        else:
            status = f"{C.D}🔴 WAIT{C.RS} {status}"
        
        profit = self.risk.capital - CFG.get('capital', 1000000)
        p_color = C.LG if profit >= 0 else C.LR
        dd = self.risk.get_drawdown()
        dd_color = C.LG if dd < 0.1 else C.Y if dd < 0.2 else C.LR
        wr = self.risk.winning_trades / max(1, self.risk.total_trades)
        ai_acc = self.ai.accuracy(50)
        
        bet_mode = CFG.get('bet_mode', 'fixed')
        if bet_mode == 'fixed':
            bet_str = f"Cố định {CFG.get('fixed_bet', 10000):,}đ"
        else:
            est = int(self.risk.capital * (CFG.get('bet_percent', 5) / 100))
            bet_str = f"{CFG.get('bet_percent', 5)}% (~{est:,}đ)"
        
        side_str = CFG.get('bet_side', 'auto')
        if side_str == 'auto': side_str = 'AI tự chọn'
        elif side_str == 'T': side_str = 'TÀI'
        else: side_str = 'XỈU'
        
        rec_str = f"{C.LG}BẬT{C.RS}" if CFG.get('recovery_enabled') else f"{C.LR}TẮT{C.RS}"
        
        print(f"""
{C.CY}╔{'═'*60}╗{C.RS}
{C.CY}║{C.RS} {C.BOLD}🚀 TREO CƯỢC SIÊU AI - FULL TOOL{C.RS}{' '*(60-38)}{C.CY}║{C.RS}
{C.CY}║{C.RS} {status} {C.D}⏱️ {str(datetime.now()-self.start_time).split('.')[0]}{C.RS}{' '*(60-35)}{C.CY}║{C.RS}
{C.CY}╠{'═'*60}╣{C.RS}""")
        
        if pred:
            s_color = C.LG if pred['side'] == 'T' else C.LR
            cf = pred['confidence']
            c_color = C.LG if cf >= 0.7 else C.Y if cf >= 0.55 else C.LR
            reasons = ' | '.join(pred.get('reasons', [])[:3])
            print(f"{C.CY}║{C.RS} {C.W}🧠 AI:{C.RS} {s_color}{pred['side']}{C.RS} {c_color}{cf:.0%}{C.RS} [{pred.get('level','?')}]")
            if reasons:
                print(f"{C.CY}║{C.RS} {C.D}📝 {reasons}{C.RS}")
        
        if eng:
            prog = eng.progress()
            rem = eng.remaining()
            bar = self._bar(prog)
            print(f"{C.CY}║{C.RS} {C.W}📊 Phiên:{C.RS} {bar} {C.LC}{prog:.0%}{C.RS} Còn{C.Y}{rem}s{C.RS} Đã đặt{len(eng.bets_placed)}/{CFG.get('max_bets_per_session',1)}")
        
        print(f"{C.CY}╠{'═'*60}╣{C.RS}")
        print(f"{C.CY}║{C.RS} {C.W}💰 Vốn:{C.RS} {C.LG}{self.risk.capital:>12,}đ{C.RS} P/L:{p_color}{profit:>10,}đ{C.RS} DD:{dd_color}{dd:>5.1%}{C.RS}")
        print(f"{C.CY}║{C.RS} {C.W}📈 Trades:{C.RS} {self.risk.total_trades} WR:{wr:.0%} Streak:W{self.risk.consecutive_wins}/L{self.risk.consecutive_losses} AI:{ai_acc:.0%}")
        print(f"{C.CY}╠{'═'*60}╣{C.RS}")
        print(f"{C.CY}║{C.RS} {C.W}⚙️ Tiền:{C.RS} {bet_str} | Cửa:{side_str} | Recovery:{rec_str}")
        print(f"{C.CY}║{C.RS} {C.W}🎯 TP:{C.LG}{CFG.get('take_profit',500000)//1000}k{C.RS} SL:{C.LR}{CFG.get('stop_loss',500000)//1000}k{C.RS} | Min:{CFG.get('min_bet',1000):,} Max:{CFG.get('max_bet',10000000):,}")
        
        for log in list(self.logs)[-4:]:
            c = {'success':C.LG,'error':C.LR,'ai':C.LC,'bet':C.LM}.get(log['level'],C.D)
            print(f"{C.CY}║{C.RS} {c}[{log['time']}] {log['msg'][:55]}{C.RS}")
        
        print(f"{C.CY}╚{'═'*60}╝{C.RS}")
        print(f"\n{C.D}MENU: [1]Auto [2]Tiền [3]Cửa [4]TP/SL [5]Recovery [6]Min/Max [7]TT [8]Thoát{C.RS}")
        print(f"{C.D}Lệnh: /auto /tien 50k /side T /tp 500k /recovery /tt /his /help{C.RS}")
    
    def _bar(self, pct, w=18):
        pct = max(0, min(1, pct))
        f = int(pct * w)
        if pct >= 0.7: return f"{C.LG}{'█'*f}{C.D}{'░'*(w-f)}{C.RS}"
        elif pct >= 0.4: return f"{C.Y}{'█'*f}{C.D}{'░'*(w-f)}{C.RS}"
        else: return f"{C.LR}{'█'*f}{C.D}{'░'*(w-f)}{C.RS}"
    
    async def handle_message(self, text, src):
        if not text or self.paused:
            return
        
        info = self.detector.detect(text)
        if not info:
            return
        
        t = info['type']
        
        if src == 'channel':
            if t == 'open':
                self.engine.on_open()
                self.active = True
                self.session_count += 1
                pred = self.engine.last_prediction
                self.log(f"🔓 #{self.session_count} | AI:{pred['side']} ({pred['confidence']:.0%})", 'ai')
                self.render()
                if self.auto_mode:
                    asyncio.create_task(self._auto_trade())
            
            elif t == 'close':
                self.engine.state = 'closed'
                self.active = False
                self.log("🔒 ĐÓNG PHIÊN", 'info')
                self.render()
            
            elif t == 'result':
                self.engine.state = 'result'
                self.active = False
                await self._handle_result(info.get('winner'))
        
        elif src == 'bot':
            if t == 'bet_success':
                self.engine.bet_status = 'confirmed'
                self.log(f"✅ Cược {info.get('side','?')} thành công", 'success')
                self.render()
            elif t == 'win':
                self.engine.bet_status = 'won'
                self.log("🎉 THẮNG!", 'win')
                self.render()
            elif t == 'loss':
                self.engine.bet_status = 'lost'
                self.log("💔 THUA!", 'lose')
                self.render()
            elif t == 'balance':
                self.risk.update_capital(info.get('amount', 0))
    
    async def _handle_result(self, winner):
        if not winner:
            self.render()
            return
        
        self.ai.add(winner)
        total_pl = 0
        
        for bet in self.engine.bets_placed:
            won = winner == bet['side']
            amt = bet['amount']
            pl = int(amt * 0.95) if won else -amt
            total_pl += pl
            self.risk.record_trade(won)
            self.ai.record(bet['side'], winner)
        
        self.risk.update_capital(self.risk.capital + total_pl)
        
        if self.engine.bets_placed:
            pl_str = f"+{total_pl:,}đ" if total_pl >= 0 else f"{total_pl:,}đ"
            self.log(f"📊 KQ:{winner} | {pl_str} | Vốn:{self.risk.capital:,}đ",
                    'win' if total_pl >= 0 else 'lose')
        
        stop, reason = self.risk.should_stop()
        if stop:
            self.log(f"🛑 DỪNG: {reason}", 'error')
            self.paused = True
            self.auto_mode = False
        
        self._save_state()
        self.render()
    
    async def _auto_trade(self):
        await asyncio.sleep(2)
        
        while self.active and not self.paused and self.auto_mode:
            can, reason = self.engine.can_bet()
            
            if can:
                pred = self.engine.last_prediction
                if pred and pred['confidence'] * 100 >= CFG.get('min_confidence', 55):
                    side = pred['side'] if CFG.get('bet_side') == 'auto' else CFG.get('bet_side', 'T')
                    amt = self.risk.calculate_bet(pred['confidence'])
                    ok, msg = await self.engine.execute_bet(side, amt)
                    self.log(f"{'✅' if ok else '❌'} {msg}", 'bet' if ok else 'error')
                    break
                else:
                    self.log("⏭️ Bỏ qua: Độ tin cậy thấp", 'error')
                    break
            else:
                if any(k in reason for k in ['Đủ', 'đóng', 'Flood']):
                    break
                await asyncio.sleep(2)
        
        # Fallback cuối phiên
        if self.active and not self.paused and self.auto_mode:
            rem = self.engine.remaining()
            if 5 < rem < 15 and len(self.engine.bets_placed) < CFG.get('max_bets_per_session', 1):
                pred = self.engine.last_prediction
                if pred and pred['confidence'] * 100 >= CFG.get('min_confidence', 55):
                    side = pred['side'] if CFG.get('bet_side') == 'auto' else CFG.get('bet_side', 'T')
                    ok, msg = await self.engine.execute_bet(side, self.risk.calculate_bet(pred['confidence']))
                    self.log(f"🆘 Fallback: {msg}", 'bet' if ok else 'error')
        
        self.render()
    
    async def menu_loop(self):
        print(f"{C.LC}>>> MENU ĐIỀU KHIỂN SẴN SÀNG{C.RS}")
        print(f"{C.D}>>> Nhập số hoặc lệnh, /help để xem menu{C.RS}")
        
        while True:
            try:
                cmd = input(f"{C.W}>>> {C.RS}").strip().lower()
                if not cmd:
                    continue
                
                if cmd in ['1', '/auto']:
                    self.auto_mode = not self.auto_mode
                    if self.engine: self.engine.auto_trade = self.auto_mode
                    self.log(f"🤖 AUTO: {'BẬT' if self.auto_mode else 'TẮT'}", 'ai')
                    self.render()
                
                elif cmd.startswith('/tien') or cmd == '2':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            amt = int(parts[-1].lower().replace('k','000').replace('m','000000'))
                            if amt == 0:
                                CFG.set('bet_mode', 'percent')
                                self.log(f"→ Chế độ % vốn ({CFG.get('bet_percent',5)}%)", 'info')
                            else:
                                CFG.set('bet_mode', 'fixed')
                                CFG.set('fixed_bet', amt)
                                self.log(f"→ Cố định {amt:,}đ/lần", 'info')
                            CFG.save()
                            self.render()
                        except:
                            print(f"{C.LR}Sai số. VD: /tien 50000{C.RS}")
                    else:
                        print(f"{C.Y}VD: /tien 50000 (cố định) hoặc /tien 0 (% vốn){C.RS}")
                
                elif cmd.startswith('/side') or cmd == '3':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        s = parts[-1].upper()
                        if s in ['T', 'X', 'AUTO']:
                            CFG.set('bet_side', s)
                            self.log(f"→ Cửa: {s}", 'info')
                            CFG.save()
                            self.render()
                        else:
                            print(f"{C.LR}Chọn T, X hoặc auto{C.RS}")
                    else:
                        print(f"{C.Y}VD: /side T (TÀI) /side X (XỈU) /side auto (AI chọn){C.RS}")
                
                elif cmd.startswith('/tp') or cmd == '4':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            CFG.set('take_profit', int(parts[-1].lower().replace('k','000').replace('m','000000')))
                            self.log(f"→ TP: {CFG.get('take_profit'):,}đ", 'info')
                            CFG.save()
                            self.render()
                        except:
                            print(f"{C.LR}Sai số{C.RS}")
                    else:
                        print(f"{C.Y}VD: /tp 500000{C.RS}")
                
                elif cmd.startswith('/sl'):
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            CFG.set('stop_loss', int(parts[-1].lower().replace('k','000').replace('m','000000')))
                            self.log(f"→ SL: {CFG.get('stop_loss'):,}đ", 'info')
                            CFG.save()
                            self.render()
                        except:
                            print(f"{C.LR}Sai số{C.RS}")
                
                elif cmd in ['5', '/recovery']:
                    CFG.set('recovery_enabled', not CFG.get('recovery_enabled'))
                    self.log(f"🔄 Recovery: {'BẬT' if CFG.get('recovery_enabled') else 'TẮT'}", 'info')
                    CFG.save()
                    self.render()
                
                elif cmd.startswith('/min') or cmd == '6':
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            CFG.set('min_bet', int(parts[-1].lower().replace('k','000').replace('m','000000')))
                            self.log(f"→ Min: {CFG.get('min_bet'):,}đ", 'info')
                            CFG.save()
                            self.render()
                        except:
                            print(f"{C.LR}Sai số{C.RS}")
                
                elif cmd.startswith('/max'):
                    parts = cmd.split()
                    if len(parts) >= 2:
                        try:
                            CFG.set('max_bet', int(parts[-1].lower().replace('k','000').replace('m','000000')))
                            self.log(f"→ Max: {CFG.get('max_bet'):,}đ", 'info')
                            CFG.save()
                            self.render()
                        except:
                            print(f"{C.LR}Sai số{C.RS}")
                
                elif cmd in ['7', '/tt', '/info']:
                    profit = self.risk.capital - CFG.get('capital', 1000000)
                    print(f"""
{C.CY}╔{'═'*45}╗
║{C.BOLD}           THÔNG TIN HỆ THỐNG{C.RS}{C.CY}              ║
╠{'═'*45}╣
║ Vốn:      {C.LG}{self.risk.capital:>15,}đ{C.RS}     {C.CY}║
║ Lãi/Lỗ:   {C.LG if profit>=0 else C.LR}{profit:>15,}đ{C.RS}     {C.CY}║
║ Peak:     {C.LG}{self.risk.peak:>15,}đ{C.RS}     {C.CY}║
║ DD:       {self.risk.get_drawdown():>14.1%}{C.RS}     {C.CY}║
║ Trades:   {self.risk.total_trades:>15}{C.RS}     {C.CY}║
║ Win Rate: {self.risk.winning_trades/max(1,self.risk.total_trades):>14.0%}{C.RS}     {C.CY}║
║ Streak:   W{self.risk.consecutive_wins}/L{self.risk.consecutive_losses:>13}{C.RS}     {C.CY}║
║ AI Acc:   {self.ai.accuracy():>14.0%}{C.RS}     {C.CY}║
║ Phiên:    {self.session_count:>15}{C.RS}     {C.CY}║
╚{'═'*45}╝{C.RS}""")
                
                elif cmd in ['8', '/exit', 'quit']:
                    print(f"{C.Y}Đang thoát...{C.RS}")
                    break
                
                elif cmd in ['/his', '/history']:
                    print(f"\n{C.CY}📜 20 LOG GẦN NHẤT:{C.RS}")
                    for log in list(self.logs)[-20:]:
                        c = {'success':C.LG,'error':C.LR,'ai':C.LC,'bet':C.LM}.get(log['level'],C.D)
                        print(f"  {c}[{log['time']}] {log['msg']}{C.RS}")
                
                elif cmd in ['/help', '/menu']:
                    print(f"""
{C.CY}╔{'═'*50}╗
║{C.BOLD}           📋 MENU ĐIỀU KHIỂN{C.RS}{C.CY}              ║
╠{'═'*50}╣
║ [1] /auto      - Bật/tắt tự động                   {C.CY}║
║ [2] /tien 50k  - Đặt tiền cố định                  {C.CY}║
║ [3] /side T    - Chọn cửa T/X/auto                 {C.CY}║
║ [4] /tp 500k   - Take profit                       {C.CY}║
║ [5] /recovery  - Bật/tắt gấp thếp                  {C.CY}║
║ [6] /min 10k   - Tiền tối thiểu                    {C.CY}║
║ [7] /tt        - Xem thông tin                     {C.CY}║
║ [8] /exit      - Thoát                             {C.CY}║
║     /his       - Xem lịch sử                       {C.CY}║
║     /save      - Lưu cấu hình                      {C.CY}║
╚{'═'*50}╝{C.RS}""")
                
                elif cmd == '/save':
                    self._save_state()
                    CFG.save()
                    print(f"{C.LG}💾 Đã lưu!{C.RS}")
                
                elif cmd == 'clear':
                    self.render()
                
                else:
                    print(f"{C.D}Không rõ lệnh. /help để xem menu{C.RS}")
                
            except KeyboardInterrupt:
                print(f"\n{C.Y}Thoát...{C.RS}")
                break
            except Exception as e:
                print(f"{C.LR}Lỗi: {e}{C.RS}")
    
    async def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"""
{C.CY}╔{'═'*60}╗
║  🚀 TREO CƯỢC SIÊU AI - FULL TOOL                      ║
║  🤖 AUTO BET - AI DỰ ĐOÁN - QUẢN LÝ VỐN              ║
║  💻 CHẠY TRÊN: WINDOWS / MAC / REPLIT / RENDER        ║
╚{'═'*60}╝{C.RS}""")
        
        try:
            session_str = CFG.get('session_string', '') or os.environ.get('SESSION_STRING', '')
            
            if session_str:
                self.client = TelegramClient(StringSession(session_str), 
                                             CFG.get('api_id'), 
                                             CFG.get('api_hash'))
            else:
                self.client = TelegramClient('session_tool', 
                                             CFG.get('api_id'), 
                                             CFG.get('api_hash'))
            
            await self.client.start(CFG.get('phone'))
            me = await self.client.get_me()
            self.log(f"Đăng nhập: {me.first_name} (@{me.username})", 'success')
            
            try:
                ch = await self.client.get_entity(CFG.get('channel'))
                self.log(f"Kênh: {ch.title}", 'success')
            except:
                self.log(f"KHÔNG TÌM THẤY KÊNH: {CFG.get('channel')}", 'error')
                return
            
            self.engine = Engine(self.ai, self.risk, self.client)
            self.engine.auto_trade = self.auto_mode
            
            @self.client.on(events.NewMessage(chats=ch))
            async def on_ch(event):
                try:
                    await self.handle_message(event.message.text or '', 'channel')
                except:
                    pass
            
            @self.client.on(events.NewMessage(chats=CFG.get('bot')))
            async def on_bot(event):
                try:
                    await self.handle_message(event.message.text or '', 'bot')
                except:
                    pass
            
            self.log("🚀 TOOL ĐÃ SẴN SÀNG!", 'success')
            self.log(f"Auto:{self.auto_mode} | Cửa:{CFG.get('bet_side')} | Tiền:{CFG.get('fixed_bet'):,}đ", 'info')
            self.render()
            
            await asyncio.gather(
                self.client.run_until_disconnected(),
                self.menu_loop()
            )
            
        except KeyboardInterrupt:
            print(f"\n{C.Y}Dừng tool{C.RS}")
        except Exception as e:
            print(f"{C.LR}Lỗi: {e}{C.RS}")
            import traceback
            traceback.print_exc()
        finally:
            if self.client:
                await self.client.disconnect()
            self._save_state()
            CFG.save()
            print(f"{C.Y}Đã lưu và thoát{C.RS}")

# ==================== WEB SERVER ====================
def run_web_server(tool):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            uptime = str(datetime.now() - tool.start_time).split('.')[0]
            profit = tool.risk.capital - CFG.get('capital', 1000000)
            wr = tool.risk.winning_trades / max(1, tool.risk.total_trades)
            
            logs_html = ''
            for log in list(tool.logs)[-30:]:
                c = {'success':'#0f0','error':'#f44','ai':'#0ff','bet':'#ff0'}.get(log['level'],'#888')
                logs_html += f'<tr><td style="color:#666">{log["time"]}</td><td style="color:{c}">{log["msg"]}</td></tr>'
            
            self.wfile.write(f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Treo Cuoc</title>
<style>
body{{font-family:Arial;background:#0a0e27;color:#fff;padding:15px}}
.card{{background:#141b3d;border-radius:15px;padding:20px;margin:15px 0}}
h1{{color:#00d4ff}} .g{{color:#0f0}} .r{{color:#f44}} .c{{color:#0ff}}
table{{width:100%;border-collapse:collapse}}
td{{padding:6px;border-bottom:1px solid rgba(255,255,255,0.03);font-size:12px}}
</style></head>
<body>
<h1>🚀 Treo Cuoc Auto</h1>
<div class="card">
<p>⏱️ Uptime: {uptime}</p>
<p>💰 Vốn: <span class="c">{tool.risk.capital:,}đ</span></p>
<p>📈 Lãi/Lỗ: <span class="{'g' if profit>=0 else 'r'}">{profit:+,}đ</span></p>
<p>🎯 Win Rate: <span class="c">{wr:.0%}</span></p>
<p>🤖 Auto: <span class="{'g' if tool.auto_mode else 'r'}">{'BẬT' if tool.auto_mode else 'TẮT'}</span></p>
</div>
<div class="card"><h3>📋 Logs</h3><table>{logs_html}</table></div>
</body></html>""".encode())
    
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

# ==================== MAIN ====================
if __name__ == '__main__':
    tool = Tool()
    run_web_server(tool)
    try:
        asyncio.run(tool.run())
    except KeyboardInterrupt:
        print(f"\n{C.Y}Done{C.RS}")
    except Exception as e:
        print(f"{C.LR}{e}{C.RS}")
