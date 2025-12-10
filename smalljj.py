import tkinter as tk
from tkinter import messagebox, ttk
import random
import math


class JapaneseMahjong:
    """日本麻將計算器 - 核心邏輯類"""
    
    # 三元牌定義
    DRAGONS = {5: '白', 6: '發', 7: '中'}
    
    # 役表（核心役）- 加入番數標註
    YAKU_TABLE = {
        '清一色': {'fan': 6, 'description': '全同一花色', 'display': '清一色 (6番)'},
        '混一色': {'fan': 3, 'description': '字牌+同一花色', 'display': '混一色 (3番)'},
        '大三元': {'fan': 13, 'description': '3個三元牌刻子', 'display': '大三元 (役滿)'},
        '大四喜': {'fan': 13, 'description': '4個風牌刻子', 'display': '大四喜 (役滿)'},
        '國士無雙': {'fan': 13, 'description': '13種幺九牌+1對', 'display': '國士無雙 (役滿)'},
        '九蓮寶燈': {'fan': 13, 'description': '同花1,1,1,2,3,4,5,6,7,8,9,9,9', 'display': '九蓮寶燈 (役滿)'},
        '四暗刻': {'fan': 13, 'description': '4個暗刻', 'display': '四暗刻 (役滿)'},
        '七對子': {'fan': 2, 'description': '7對牌', 'display': '七對子 (2番)'},
        '対々和': {'fan': 2, 'description': '全部刻子(門前清)', 'display': '対々和 (2番)'},
        '排型對對和': {'fan': 2, 'description': '全部刻子(非門前清)', 'display': '排型對對和 (2番)'},
        '三暗刻': {'fan': 2, 'description': '3個暗刻', 'display': '三暗刻 (2番)'},
        '一盃口': {'fan': 1, 'description': '兩組一樣的順子', 'display': '一盃口 (1番)'},
        '立直': {'fan': 1, 'description': '門前清聽牌', 'display': '立直 (1番)'},
        '兩倍立直': {'fan': 2, 'description': '立直後自摸', 'display': '兩倍立直 (2番)'},
        '斷幺九': {'fan': 1, 'description': '無幺九牌', 'display': '斷幺九 (1番)'},
        '平和': {'fan': 1, 'description': '全部順子+對子', 'display': '平和 (1番)'},
        '白': {'fan': 1, 'description': '白刻子', 'display': '白 (1番)'},
        '發': {'fan': 1, 'description': '發刻子', 'display': '發 (1番)'},
        '中': {'fan': 1, 'description': '中刻子', 'display': '中 (1番)'},
    }
    
    # 點數表（1番～13番）
    BASE_POINTS = {
        1: {'tsumo': 1000, 'ron': 1000},
        2: {'tsumo': 2000, 'ron': 2000},
        3: {'tsumo': 3900, 'ron': 5800},
        4: {'tsumo': 7700, 'ron': 7700},
        5: {'tsumo': 8000, 'ron': 8000},  # 滿貫
        6: {'tsumo': 12000, 'ron': 12000},
        7: {'tsumo': 16000, 'ron': 16000},
        8: {'tsumo': 16000, 'ron': 16000},
        10: {'tsumo': 16000, 'ron': 16000},  # 跳滿
        13: {'tsumo': 16000, 'ron': 16000},  # 數え役滿
    }
    
    SUIT_NAMES = {'m': '萬', 'p': '筒', 's': '索', 'z': '字'}
    
    def parse_hand(self, input_str: str) -> dict:
        """
        解析手牌輸入
        
        支持格式：
        - 123m456p789s11z (標準格式 - 數字後跟花色)
        """
        tiles = {'m': [], 'p': [], 's': [], 'z': []}
        input_str = input_str.replace(' ', '').strip()
        
        if not input_str:
            raise ValueError("輸入為空！")
        
        i = 0
        while i < len(input_str):
            # 收集數字
            numbers = []
            while i < len(input_str) and input_str[i].isdigit():
                numbers.append(int(input_str[i]))
                i += 1
            
            # 取得花色
            if i < len(input_str) and input_str[i] in 'mpsz':
                suit = input_str[i]
                i += 1
                
                # 將數字加入該花色
                for num in numbers:
                    if not (1 <= num <= 9):
                        raise ValueError(f"牌的數字必須在1-9之間，但輸入了：{num}")
                    tiles[suit].append(num)
            elif numbers:
                raise ValueError(f"數字後面必須跟花色標記(m/p/s/z)")
        
        # 排序所有牌
        for suit in tiles:
            tiles[suit].sort()
        
        return tiles
    
    def check_yaku(self, tiles: dict, is_riichi: bool = False, is_tsumo: bool = False, has_pung: bool = False) -> list:
        """
        檢查所有符合的役
        
        Args:
            tiles: 手牌字典
            is_riichi: 是否立直
            is_tsumo: 是否自摸
            has_pung: 是否有碰過牌（影響對對和的判定）
        """
        yaku_list = []
        
        # 先檢查是否為有效的和牌型
        if not self._is_valid_winning_pattern(tiles):
            # 特殊役不需要標準和牌型
            # 檢查國士無雙
            if self._check_kokushi(tiles):
                yaku_list.append(('國士無雙', 13))
                return yaku_list
            
            # 檢查九蓮寶燈
            if self._check_nine_gates(tiles):
                yaku_list.append(('九蓮寶燈', 13))
                return yaku_list
            
            return [('無役', 0)]
        
        # 統計所有數字出現次數
        counts = self._count_tiles(tiles)
        
        # 檢查國士無雙
        if self._check_kokushi(tiles):
            yaku_list.append(('國士無雙', 13))
            return yaku_list
        
        # 檢查九蓮寶燈
        if self._check_nine_gates(tiles):
            yaku_list.append(('九蓮寶燈', 13))
            return yaku_list
        
        # 檢查大四喜 - 不能和立直疊加
        if self._check_big_four_winds(counts):
            yaku_list.append(('大四喜', 13))
            return yaku_list
        
        # 檢查清一色（全同花色）- 不能和立直疊加
        non_empty_suits = [s for s in ['m', 'p', 's'] if tiles[s]]
        if len(non_empty_suits) == 1 and not tiles['z']:
            yaku_list.append(('清一色', 6))
            return yaku_list
        
        # 檢查混一色（字牌+同花色）- 不能和立直疊加
        if len(non_empty_suits) == 1 and tiles['z']:
            yaku_list.append(('混一色', 3))
            return yaku_list
        
        # 檢查大三元 - 不能和立直疊加
        if self._check_big_three_dragons(counts):
            yaku_list.append(('大三元', 13))
            return yaku_list
        
        # 檢查三元牌
        for dragon_num, dragon_name in self.DRAGONS.items():
            if self._is_triplet(counts.get(('z', dragon_num), 0)):
                yaku_list.append((dragon_name, 1))
        
        # 檢查七對子 - 不能和立直疊加
        if self._check_seven_pairs(counts):
            yaku_list.append(('七對子', 2))
            return yaku_list
        
        # 檢查四暗刻 - 只有在沒有碰的情況下，且不能和立直疊加
        if not has_pung and self._check_four_concealed_triplets(tiles):
            yaku_list.append(('四暗刻', 13))
            return yaku_list
                # 檢查対々和（全刻子 + 門前清）
        if self._check_all_triplets(counts):
            if has_pung:
                yaku_list.append(('排型對對和', 2))
            else:
                yaku_list.append(('対々和', 2))
        
        # 檢查三暗刻（不與對對和疊加）
        if not any(yaku[0] in ['対々和', '排型對對和', '四暗刻'] for yaku in yaku_list):
            if self._check_three_concealed_triplets(tiles):
                yaku_list.append(('三暗刻', 2))
        
        # 檢查一盃口
        if self._check_ippekou(tiles):
            yaku_list.append(('一盃口', 1))
        
        # 檢查斷幺九（無幺九牌）
        if not self._has_terminal_or_honor(tiles):
            yaku_list.append(('斷幺九', 1))
        
        # 檢查立直（只有在沒有出現對對和等複合役的情況下才加立直）
        if is_riichi and not any(yaku[0] == '対々和' for yaku in yaku_list):
            if is_tsumo:
                yaku_list.append(('兩倍立直', 2))
            else:
                yaku_list.append(('立直', 1))
        
        # 沒有任何役時，返回無役（無法和牌）
        if not yaku_list:
            yaku_list = [('無役', 0)]
        
        return yaku_list
    
    @staticmethod
    def _count_tiles(tiles: dict) -> dict:
        """統計所有牌的出現次數"""
        counts = {}
        for suit in tiles:
            for num in tiles[suit]:
                key = (suit, num)
                counts[key] = counts.get(key, 0) + 1
        return counts
    
    @staticmethod
    def _is_triplet(count: int) -> bool:
        """檢查是否為刻子或槓子"""
        return count >= 3
    
    @staticmethod
    def _check_big_three_dragons(counts: dict) -> bool:
        """檢查大三元"""
        dragon_triplets = sum(1 for d in [5, 6, 7] if counts.get(('z', d), 0) >= 3)
        return dragon_triplets == 3
    
    @staticmethod
    def _check_seven_pairs(counts: dict) -> bool:
        """檢查七對子"""
        pairs = sum(1 for count in counts.values() if count == 2)
        return pairs == 7
    
    @staticmethod
    def _check_all_triplets(counts: dict) -> bool:
        """檢查所有牌是否都是刻子或對子"""
        for count in counts.values():
            if count not in [2, 3, 4]:
                return False
        # 至少有3個刻子
        triplets = sum(1 for count in counts.values() if count in [3, 4])
        return triplets >= 3
    
    @staticmethod
    def _has_terminal_or_honor(tiles: dict) -> bool:
        """檢查是否含有幺九牌或字牌"""
        for suit in ['m', 'p', 's']:
            if 1 in tiles[suit] or 9 in tiles[suit]:
                return True
        return bool(tiles['z'])
    
    @staticmethod
    def _check_kokushi(tiles: dict) -> bool:
        """檢查國士無雙 - 13種幺九牌+1對"""
        # 幺九牌：m1,m9,p1,p9,s1,s9,z1,z2,z3,z4,z5,z6,z7
        yaochuuhai = [('m', 1), ('m', 9), ('p', 1), ('p', 9), ('s', 1), ('s', 9),
                      ('z', 1), ('z', 2), ('z', 3), ('z', 4), ('z', 5), ('z', 6), ('z', 7)]
        
        # 統計所有牌
        counts = {}
        for suit in tiles:
            for num in tiles[suit]:
                key = (suit, num)
                counts[key] = counts.get(key, 0) + 1
        
        # 檢查是否有13種幺九牌
        for tile in yaochuuhai:
            if tile not in counts:
                return False
        
        # 檢查是否只有幺九牌，且總共14張
        total = sum(counts.get(tile, 0) for tile in yaochuuhai)
        return total == 14 and len(counts) == 13
    
    @staticmethod
    def _check_nine_gates(tiles: dict) -> bool:
        """檢查九蓮寶燈 - 同花1,1,1,2,3,4,5,6,7,8,9,9,9"""
        # 檢查是否只有一種花色
        non_empty_suits = [s for s in ['m', 'p', 's'] if tiles[s]]
        if len(non_empty_suits) != 1 or tiles['z']:
            return False
        
        suit = non_empty_suits[0]
        tiles_list = sorted(tiles[suit])
        
        # 應該是：1,1,1,2,3,4,5,6,7,8,9,9,9 (13張)
        expected = [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9]
        return tiles_list == expected
    
    @staticmethod
    def _check_big_four_winds(counts: dict) -> bool:
        """檢查大四喜 - 4個風牌刻子 (東南西北)"""
        wind_tiles = [('z', 1), ('z', 2), ('z', 3), ('z', 4)]
        triplet_count = sum(1 for tile in wind_tiles if counts.get(tile, 0) >= 3)
        return triplet_count == 4
    
    @staticmethod
    def _check_four_concealed_triplets(tiles: dict) -> bool:
        """
        檢查四暗刻 - 4個暗刻
        
        注：簡化版 - 假設所有刻子都是暗刻
        在真實遊戲中需要追蹤牌的來源
        """
        counts = {}
        for suit in tiles:
            for num in tiles[suit]:
                key = (suit, num)
                counts[key] = counts.get(key, 0) + 1
        
        # 檢查是否有4個刻子（每個3-4張）
        # 須有1對 + 4個刻子 = 14張
        pair_count = sum(1 for count in counts.values() if count == 2)
        triplet_count = sum(1 for count in counts.values() if count in [3, 4])
        
        return pair_count == 1 and triplet_count == 4
    
    @staticmethod
    def _check_three_concealed_triplets(tiles: dict) -> bool:
        """檢查三暗刻 - 3個暗刻"""
        counts = {}
        for suit in tiles:
            for num in tiles[suit]:
                key = (suit, num)
                counts[key] = counts.get(key, 0) + 1
        
        # 檢查是否有至少3個刻子
        triplet_count = sum(1 for count in counts.values() if count in [3, 4])
        return triplet_count >= 3
    
    @staticmethod
    def _check_pair_honour(tiles: dict) -> bool:
        """
        檢查排型對對和 - 對對和但非門前清
        即：對對和 + 有碰過的牌
        簡化版：只要是4個刻子就算排型對對和
        """
        counts = {}
        for suit in tiles:
            for num in tiles[suit]:
                key = (suit, num)
                counts[key] = counts.get(key, 0) + 1
        
        # 檢查是否有4個刻子（對對和）
        triplet_count = sum(1 for count in counts.values() if count in [3, 4])
        pair_count = sum(1 for count in counts.values() if count == 2)
        
        return pair_count == 1 and triplet_count == 4
    
    @staticmethod
    def _check_ippekou(tiles: dict) -> bool:
        """
        檢查一盃口 - 兩組一樣的順子
        
        找出所有可能的順子組合，看是否有重複
        """
        # 遍歷每個花色找順子
        sequences = {}
        
        for suit in ['m', 'p', 's']:
            tile_counts = {}
            for num in tiles[suit]:
                tile_counts[num] = tile_counts.get(num, 0) + 1
            
            # 檢查連續的3張牌是否出現2次
            for start_num in range(1, 8):  # 1-7, 因為最高是789
                if (tile_counts.get(start_num, 0) >= 1 and 
                    tile_counts.get(start_num + 1, 0) >= 1 and 
                    tile_counts.get(start_num + 2, 0) >= 1):
                    
                    seq_key = (suit, start_num)
                    if seq_key not in sequences:
                        sequences[seq_key] = 0
                    sequences[seq_key] += 1
        
        # 檢查是否有任何順子出現2次以上
        return any(count >= 2 for count in sequences.values())
    
    def _is_valid_winning_pattern(self, tiles: dict) -> bool:
        """
        檢查是否為有效的和牌形式
        標準和牌：一個對子 + 四個順子/刻子
        
        使用遞迴回溯演算法檢驗
        """
        # 統計所有牌
        all_tiles = []
        for suit in ['m', 'p', 's', 'z']:
            for num in tiles[suit]:
                all_tiles.append((suit, num))
        
        if len(all_tiles) != 14:
            return False
        
        # 嘗試每一個可能的對子 (遍歷所有牌種，找出現次數>=2的)
        pair_candidates = set()
        for suit in ['m', 'p', 's', 'z']:
            for num in set(tiles[suit]):
                count = tiles[suit].count(num)
                if count >= 2:
                    pair_candidates.add((suit, num))
        
        # 嘗試每個候選對子
        for pair_suit, pair_num in pair_candidates:
            # 複製tiles，移除一個對子
            tiles_copy = {suit: tiles[suit][:] for suit in tiles}
            tiles_copy[pair_suit].remove(pair_num)
            tiles_copy[pair_suit].remove(pair_num)
            
            # 檢查剩餘12張牌能否組成4個面子
            if self._check_melds_valid(tiles_copy):
                return True
        
        return False
    
    @staticmethod
    def _check_melds_valid(tiles: dict) -> bool:
        """檢查12張牌是否能組成4個面子 (每個3張)"""
        # 轉換為列表並排序
        tile_list = []
        for suit in ['m', 'p', 's', 'z']:
            for num in sorted(tiles[suit]):
                tile_list.append((suit, num))
        
        return JapaneseMahjong._try_form_melds(tile_list)
    
    @staticmethod
    def _try_form_melds(tile_list):
        """
        嚴格的遞迴面子檢驗
        tile_list: [(suit, num), ...] 格式的牌列表，必須是12張
        """
        if not tile_list:
            return True  # 成功 - 所有牌都已組成面子
        
        if len(tile_list) % 3 != 0:
            return False  # 失敗 - 牌數不是3倍數
        
        # 取第一張牌
        suit, num = tile_list[0]
        
        # 方法1: 嘗試形成刻子（同花色同數字 3張）
        triplet_count = sum(1 for s, n in tile_list if s == suit and n == num)
        if triplet_count >= 3:
            # 移除刻子
            remaining = tile_list[:]
            for _ in range(3):
                remaining.remove((suit, num))
            
            if JapaneseMahjong._try_form_melds(remaining):
                return True
        
        # 方法2: 嘗試形成順子（同花色連續3張）
        if suit in ['m', 'p', 's'] and num <= 7:
            # 檢查 num, num+1, num+2 是否都存在
            if (suit, num + 1) in tile_list and (suit, num + 2) in tile_list:
                # 移除順子
                remaining = tile_list[:]
                remaining.remove((suit, num))
                remaining.remove((suit, num + 1))
                remaining.remove((suit, num + 2))
                
                if JapaneseMahjong._try_form_melds(remaining):
                    return True
        
        return False
    
    def calculate_fan(self, tiles: dict, is_riichi: bool = False, is_tsumo: bool = False, has_pung: bool = False) -> tuple:
        """
        計算總番數
        
        Args:
            tiles: 手牌字典
            is_riichi: 是否立直
            is_tsumo: 是否自摸
            has_pung: 是否有碰過牌
        """
        yaku_list = self.check_yaku(tiles, is_riichi, is_tsumo, has_pung)
        total_fan = sum(fan for _, fan in yaku_list)
        return yaku_list, total_fan
    
    def get_points(self, fan: int, is_tsumo: bool = True) -> int:
        """根據番數計算點數"""
        if fan == 0:
            return 0
        
        if fan in self.BASE_POINTS:
            points = self.BASE_POINTS[fan]
        else:
            # 13番以上視為數え役滿
            points = self.BASE_POINTS[13]
        
        return points['tsumo'] if is_tsumo else points['ron']


class Firework:
    """超大煙火：佔滿螢幕版"""
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.particles = []
        
        colors = ['#FFB6C1', '#87CEEB', '#DDA0DD', '#F0E68C', '#FFFFFF', '#FF69B4', '#98FB98']
        main_color = random.choice(colors)
        num_particles = 100  # 修正：原本寫 random.randint = 25（錯誤）
        
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.gauss(20, 5)
            p_color = main_color if random.random() > 0.3 else random.choice(colors)
            
            self.particles.append({
                'x': x,
                'y': y,
                'prev_x': x,
                'prev_y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': p_color,
                'life': random.randint(60, 100),
                'max_life': 100,
                'id': None,
                'trail_id': None
            })
    
    def update(self):
        """更新煙火粒子位置"""
        alive = False
        for p in self.particles:
            if p['life'] > 0:
                alive = True
                
                p['prev_x'] = p['x']
                p['prev_y'] = p['y']
                
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.2
                p['vx'] *= 0.96
                p['vy'] *= 0.96
                p['life'] -= 1
                
                if p['trail_id']:
                    self.canvas.delete(p['trail_id'])
                if p['id']:
                    self.canvas.delete(p['id'])
                
                alpha_ratio = p['life'] / p['max_life']
                
                if alpha_ratio > 0.1:
                    width = 3 * alpha_ratio
                    p['trail_id'] = self.canvas.create_line(
                        p['prev_x'], p['prev_y'], p['x'], p['y'],
                        fill=p['color'], 
                        width=max(1, width)
                    )
                    
                    size = 4 * alpha_ratio
                    p['id'] = self.canvas.create_oval(
                        p['x'] - size, p['y'] - size,
                        p['x'] + size, p['y'] + size,
                        fill=p['color'], outline=''
                    )
        return alive
    
    def cleanup(self):
        """清理煙火粒子"""
        for p in self.particles:
            if p['trail_id']:
                self.canvas.delete(p['trail_id'])
            if p['id']:
                self.canvas.delete(p['id'])

    
    def update(self):
        """更新煙火粒子位置"""
        alive = False
        for p in self.particles:
            if p['life'] > 0:
                alive = True
                
                p['prev_x'] = p['x']
                p['prev_y'] = p['y']
                
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.2   # 稍微增加重力
                p['vx'] *= 0.96  # 減少阻力：0.94 → 0.96（飛更遠）
                p['vy'] *= 0.96
                p['life'] -= 1
                
                if p['trail_id']:
                    self.canvas.delete(p['trail_id'])
                if p['id']:
                    self.canvas.delete(p['id'])
                
                alpha_ratio = p['life'] / p['max_life']
                
                if alpha_ratio > 0.1:
                    # 更粗的軌跡線
                    width = 5 * alpha_ratio  # 1.5 → 3
                    p['trail_id'] = self.canvas.create_line(
                        p['prev_x'], p['prev_y'], p['x'], p['y'],
                        fill=p['color'], 
                        width=max(1, width)
                    )
                    
                    # 更大的光點
                    size = 5 * alpha_ratio  # 1.5 → 4
                    p['id'] = self.canvas.create_oval(
                        p['x'] - size, p['y'] - size,
                        p['x'] + size, p['y'] + size,
                        fill=p['color'], outline=''
                    )
        return alive
    
    def cleanup(self):
        """清理煙火粒子"""
        for p in self.particles:
            if p['trail_id']:
                self.canvas.delete(p['trail_id'])
            if p['id']:
                self.canvas.delete(p['id'])

            if p['id']:
                self.canvas.delete(p['id'])




class MahjongGUI:
    """日本麻將計算器 - GUI介面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("日本麻將計算器")
        self.root.geometry("800x900")
        self.mahjong = JapaneseMahjong()
        
        # 煙火相關
        self.fireworks = []
        self.firework_canvas = None
        self.firework_animation_id = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """設置使用者介面"""
        # 標題
        title_label = ttk.Label(
            self.root, 
            text="日本麻將計算器", 
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=15)
        
        # 輸入區域
        self._setup_input_frame()
        
        # 選項區域
        self._setup_option_frame()
        
        # 按鈕區域
        self._setup_button_frame()
        
        # 結果區域
        self._setup_result_frame()
    
    def _setup_input_frame(self):
        """設置輸入區域"""
        input_frame = ttk.LabelFrame(self.root, text="輸入手牌", padding=15)
        input_frame.pack(padx=20, pady=10, fill="x")
        
        ttk.Label(
            input_frame, 
            text="格式：123m456p789s11z (萬-筒-索-字牌，共14張)",
            font=("Arial", 9), 
            foreground="gray"
        ).pack(anchor="w", pady=(0, 5))
        
        ttk.Label(
            input_frame, 
            text="字牌：1=東 2=南 3=西 4=北 5=白 6=發 7=中",
            font=("Arial", 9), 
            foreground="gray"
        ).pack(anchor="w", pady=(0, 10))
        
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 13), width=40)
        self.input_entry.pack(pady=10, fill="x")
        self.input_entry.bind("<Return>", lambda e: self.calculate())
    
    def _setup_option_frame(self):
        """設置選項區域"""
        option_frame = ttk.LabelFrame(self.root, text="計算選項", padding=10)
        option_frame.pack(padx=20, pady=5, fill="x")
        
        self.is_tsumo = tk.BooleanVar(value=True)
        self.is_menzen = tk.BooleanVar(value=True)
        self.is_riichi = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(option_frame, text="自摸", variable=self.is_tsumo).pack(side="left", padx=10)
        ttk.Checkbutton(option_frame, text="門前清", variable=self.is_menzen).pack(side="left", padx=10)
        ttk.Checkbutton(option_frame, text="立直", variable=self.is_riichi).pack(side="left", padx=10)
    
    def _setup_button_frame(self):
        """設置按鈕區域"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="計算", command=self.calculate, width=15).pack(side="left", padx=5)
        ttk.Button(button_frame, text="清除", command=self.clear, width=15).pack(side="left", padx=5)
    
    def _setup_result_frame(self):
        """設置結果區域"""
        result_frame = ttk.LabelFrame(self.root, text="計算結果", padding=15)
        result_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # 結果文字框
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.result_text = tk.Text(
            text_frame, 
            font=("Courier", 11), 
            height=20, 
            wrap="word", 
            bg="white", 
            state="disabled"
        )
        self.result_text.pack(side="left", fill="both", expand=True)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 設定標籤樣式
        self.result_text.tag_config("title", foreground="#0066cc", font=("Courier", 11, "bold"))
        self.result_text.tag_config("yaku", foreground="#009900", font=("Courier", 10))
        self.result_text.tag_config("yakuman", foreground="#FF0000", font=("Courier", 11, "bold"))
        self.result_text.tag_config("points", foreground="#cc0000", font=("Courier", 10, "bold"))
        self.result_text.tag_config("error", foreground="#cc0000")
    
    def _insert_result(self, text: str, tag: str = ""):
        """向結果框插入文本"""
        self.result_text.config(state="normal")
        self.result_text.insert("end", text, tag)
        self.result_text.config(state="disabled")
    
    def _show_fireworks(self):
        """顯示煙火動畫＋簡潔役滿特效"""
        self._stop_fireworks()
        
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        
        # 建立透明頂層視窗
        self.firework_window = tk.Toplevel(self.root)
        self.firework_window.geometry(f"{w}x{h}+{x}+{y}")
        self.firework_window.overrideredirect(True)
        self.firework_window.attributes("-topmost", True)
        
        TRANS_COLOR = "#000001"
        self.firework_window.configure(bg=TRANS_COLOR)
        try:
            self.firework_window.attributes("-transparentcolor", TRANS_COLOR)
        except Exception:
            self.firework_window.attributes("-alpha", 0.9)
        
        # 畫布
        self.firework_canvas = tk.Canvas(
            self.firework_window,
            bg=TRANS_COLOR,
            highlightthickness=0
        )
        self.firework_canvas.pack(fill="both", expand=True)
        
        cw, ch = w, h
        
        # 1. 簡單半透明黑幕（漸暗效果）
        self.firework_canvas.create_rectangle(
            0, 0, cw, ch,
            fill="#000000",
            stipple="gray50",
            outline=""
        )
        
        # 2. 役滿文字（中央，固定不動）
        center_x, center_y = cw // 2, ch // 2
        
        self.firework_canvas.create_text(
            center_x, center_y - 5,
            text="役 滿",
            font=("Microsoft JhengHei", 52, "bold"),
            fill="#FFFFFF"
        )
        
        # 下方小字
        self.firework_canvas.create_text(
            center_x, center_y + 35,
            text="恭喜達成役滿",
            font=("Microsoft JhengHei", 15),
            fill="#F0E68C"
        )
        
        # 初始化動畫狀態
        self._firework_start_time = 0
        
        # 開始動畫
        self._animate_fireworks()





    
    def _animate_fireworks(self):
        """煙火動畫（集中在役滿附近）"""
        # 限制畫面上最多 3 顆煙火
        if len(self.fireworks) < 3 and random.random() < 0.08:
            canvas_width = self.root.winfo_width()
            canvas_height = self.root.winfo_height()
            
            # 煙火集中在畫面中央（役滿文字）附近
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            # 在中心點周圍 ±150 像素範圍內隨機
            x = center_x + random.randint(-150, 150)
            y = center_y + random.randint(-100, 100)
            
            self.fireworks.append(Firework(self.firework_canvas, x, y))
        
        # 更新煙火
        active_fireworks = []
        for fw in self.fireworks:
            if fw.update():
                active_fireworks.append(fw)
            else:
                fw.cleanup()
        self.fireworks = active_fireworks
        
        # 動畫時間控制
        self._firework_start_time += 1
        if self._firework_start_time < 180:
            self.firework_animation_id = self.root.after(50, self._animate_fireworks)
        else:
            self._stop_fireworks()




    
    def _stop_fireworks(self):
        """停止煙火動畫與役滿特效"""
        if getattr(self, "firework_animation_id", None):
            self.root.after_cancel(self.firework_animation_id)
            self.firework_animation_id = None
        
        if hasattr(self, "firework_window") and self.firework_window:
            self.firework_window.destroy()
            self.firework_window = None
            self.firework_canvas = None
        
        self.fireworks = []
        self._firework_start_time = 0
        self._yakuman_anim_phase = 0

    
    def calculate(self):
        """計算胡牌"""
        # 先停止之前的煙火
        self._stop_fireworks()
        
        input_hand = self.input_entry.get().strip()
        
        if not input_hand:
            messagebox.showwarning("警告", "請輸入手牌！")
            return
        
        try:
            tiles = self.mahjong.parse_hand(input_hand)
            total_tiles = sum(len(tiles[s]) for s in tiles)
            
            # 檢查手牌數量
            if total_tiles != 14:
                self._show_tile_error(tiles, total_tiles)
                return
            
            # 實時讀取選項
            is_tsumo = self.is_tsumo.get()
            is_riichi = self.is_riichi.get()
            
            # 計算役和點數
            yaku_list, fan = self.mahjong.calculate_fan(tiles, is_riichi, is_tsumo)
            tsumo_points = self.mahjong.get_points(fan, True)
            ron_points = self.mahjong.get_points(fan, False)
            
            # 檢查是否為役滿
            is_yakuman = fan >= 13 and yaku_list[0][0] != '無役'
            
            self._display_result(tiles, yaku_list, fan, tsumo_points, ron_points, is_tsumo, is_riichi, is_yakuman)
            
            # 如果是役滿，顯示煙火
            if is_yakuman:
                self.root.after(500, self._show_fireworks)
            
        except ValueError as e:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", "end")
            self._insert_result(f"❌ 輸入錯誤：\n{str(e)}", "error")
            self.result_text.config(state="disabled")
    
    def _show_tile_error(self, tiles: dict, total: int):
        """顯示牌數錯誤訊息"""
        detail = "\n詳細分析：\n"
        for suit, name in self.mahjong.SUIT_NAMES.items():
            if tiles[suit]:
                detail += f"  {name}：{tiles[suit]} ({len(tiles[suit])}張)\n"
        
        messagebox.showerror(
            "錯誤", 
            f"手牌數量錯誤！\n當前：{total}張\n需要：14張{detail}"
        )
    
    def _display_result(self, tiles, yaku_list, fan, tsumo_points, ron_points, is_tsumo, is_riichi, is_yakuman):
        """顯示計算結果"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        
        # 標題和分隔線
        self._insert_result("════════════════════════════════════════\n")
        if is_yakuman:
            self._insert_result("     🎊 役滿達成！🎊\n", "yakuman")
        else:
            self._insert_result("        日本麻將計算結果\n", "title")
        self._insert_result("════════════════════════════════════════\n")
        
        # 輸入的手牌
        input_hand = self.input_entry.get()
        self._insert_result(f"\n輸入手牌：{input_hand}\n")
        self._insert_result(f"總牌數：{sum(len(tiles[s]) for s in tiles)}張\n\n")
        
        # 手牌分析
        self._insert_result("【手牌分析】\n")
        for suit, name in self.mahjong.SUIT_NAMES.items():
            if tiles[suit]:
                tiles_str = ''.join(map(str, tiles[suit]))
                self._insert_result(f"  {name}：{tiles_str} ({len(tiles[suit])}張)\n")
        
        # 選項信息
        self._insert_result("\n【選項狀態】\n")
        self._insert_result(f"  {'✓' if is_riichi else '○'} 立直\n")
        
        # 符合的役（加上番數標註）
        self._insert_result("\n【符合的役】\n")
        if yaku_list and yaku_list[0][0] != '無役':
            for yaku_name, yaku_fan in yaku_list:
                if yaku_fan >= 13:
                    self._insert_result(f"  ✓ {yaku_name} (役滿)\n", "yakuman")
                elif yaku_fan >= 6:
                    self._insert_result(f"  ✓ {yaku_name} ({yaku_fan}番)\n", "points")
                else:
                    self._insert_result(f"  ✓ {yaku_name} ({yaku_fan}番)\n", "yaku")
        else:
            self._insert_result("  ○ 無役（不能胡）\n")
        
        # 番數和點數
        self._insert_result("\n────────────────────────────────────────\n")
        if is_yakuman:
            self._insert_result(f"總番數：{fan}番 (役滿)\n\n", "yakuman")
        else:
            self._insert_result(f"總番數：{fan}番\n\n")
        
        # 根據是否自摸顯示相應的點數
        if fan > 0:
            if is_tsumo:
                self._insert_result(f"自摸：{tsumo_points}點\n", "points")
            else:
                self._insert_result(f"榮胡：{ron_points}點\n", "points")
        else:
            self._insert_result("無役不能胡！\n", "error")
        
        self._insert_result("\n════════════════════════════════════════\n")
        self.result_text.config(state="disabled")
    
    def clear(self):
        """清除輸入和結果"""
        self._stop_fireworks()
        self.input_entry.delete(0, "end")
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")
        self.input_entry.focus()


def main():
    """主程式入口"""
    root = tk.Tk()
    gui = MahjongGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
