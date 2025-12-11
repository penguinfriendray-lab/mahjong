import tkinter as tk
from tkinter import messagebox, ttk
import itertools

class JapaneseMahjong:
    """日本麻將計算核心 - 進階版"""
    
    # 牌的定義
    SUIT_NAMES = {'m': '萬', 'p': '筒', 's': '索', 'z': '字'}
    DRAGONS = {5: '白', 6: '發', 7: '中'}
    WINDS = {1: '東', 2: '南', 3: '西', 4: '北'}
    
    # 完整的役表（整合您的輸入）
    YAKU_TABLE = {
        # 1番
        '立直': {'fan': 1, 'display': '立直 (1番)'},
        '門前清自摸和': {'fan': 1, 'display': '門前清自摸和 (1番)'},
        '斷幺九': {'fan': 1, 'display': '斷幺九 (1番)'},
        '平和': {'fan': 1, 'display': '平和 (1番)'},
        '一盃口': {'fan': 1, 'display': '一盃口 (1番)'},
        '白': {'fan': 1, 'display': '白 (1番)'},
        '發': {'fan': 1, 'display': '發 (1番)'},
        '中': {'fan': 1, 'display': '中 (1番)'},
        '風子（自風）': {'fan': 1, 'display': '自風 (1番)'},
        '風子（場風）': {'fan': 1, 'display': '場風 (1番)'},
        
        # 2番
        '三色同順': {'fan': 2, 'display': '三色同順 (2番)'}, # 門前2番，副露1番(簡化處理)
        '一氣通貫': {'fan': 2, 'display': '一氣通貫 (2番)'}, # 門前2番，副露1番
        '混全帯幺九': {'fan': 2, 'display': '混全帯幺九 (2番)'}, # 門前2番，副露1番
        '七對子': {'fan': 2, 'display': '七對子 (2番)'},
        '対々和': {'fan': 2, 'display': '対々和 (2番)'},
        '三暗刻': {'fan': 2, 'display': '三暗刻 (2番)'},
        '三色同刻': {'fan': 2, 'display': '三色同刻 (2番)'},
        '混老頭': {'fan': 2, 'display': '混老頭 (2番)'},
        '小三元': {'fan': 2, 'display': '小三元 (2番)'},
        
        # 3番
        '混一色': {'fan': 3, 'display': '混一色 (3番)'}, # 門前3番，副露2番
        '二盃口': {'fan': 3, 'display': '二盃口 (3番)'},
        '純全帯幺九': {'fan': 3, 'display': '純全帯幺九 (3番)'},
        
        # 6番
        '清一色': {'fan': 6, 'display': '清一色 (6番)'}, # 門前6番，副露5番
        
        # 役滿
        '大三元': {'fan': 13, 'display': '大三元 (役滿)'},
        '四暗刻': {'fan': 13, 'display': '四暗刻 (役滿)'},
        '國士無雙': {'fan': 13, 'display': '國士無雙 (役滿)'},
        '大四喜': {'fan': 13, 'display': '大四喜 (役滿)'},
        '小四喜': {'fan': 13, 'display': '小四喜 (役滿)'},
        '九蓮寶燈': {'fan': 13, 'display': '九蓮寶燈 (役滿)'},
        '字一色': {'fan': 13, 'display': '字一色 (役滿)'},
        '綠一色': {'fan': 13, 'display': '綠一色 (役滿)'},
        '清老頭': {'fan': 13, 'display': '清老頭 (役滿)'},
    }

    BASE_POINTS = {
        1: {'tsumo': 1000, 'ron': 1000},
        2: {'tsumo': 2000, 'ron': 2000},
        3: {'tsumo': 3900, 'ron': 5800},
        4: {'tsumo': 7700, 'ron': 7700},
        5: {'tsumo': 8000, 'ron': 8000}, # 滿貫
        6: {'tsumo': 12000, 'ron': 12000}, # 跳滿
        8: {'tsumo': 16000, 'ron': 16000}, # 倍滿
        11: {'tsumo': 24000, 'ron': 24000}, # 三倍滿
        13: {'tsumo': 32000, 'ron': 32000}, # 役滿
    }

    def parse_hand(self, input_str):
        """解析手牌"""
        tiles = {'m': [], 'p': [], 's': [], 'z': []}
        input_str = input_str.replace(' ', '').strip()
        i = 0
        while i < len(input_str):
            numbers = []
            while i < len(input_str) and input_str[i].isdigit():
                numbers.append(int(input_str[i]))
                i += 1
            if i < len(input_str) and input_str[i] in 'mpsz':
                suit = input_str[i]
                i += 1
                for num in numbers:
                    tiles[suit].append(num)
        for suit in tiles:
            tiles[suit].sort()
        return tiles

    def calculate_fan(self, tiles, is_tsumo=True, is_menzen=True, is_riichi=False):
        """主計算邏輯"""
        total_tiles = sum(len(tiles[s]) for s in tiles)
        if total_tiles != 14:
            raise ValueError(f"手牌張數錯誤 ({total_tiles}張)，必須為14張")

        yaku_list = []
        
        # 1. 檢查役滿
        yakuman_list = self._check_yakuman(tiles)
        if yakuman_list:
            return yakuman_list, sum(f for _, f in yakuman_list)

        # 2. 檢查七對子 (特殊牌型)
        pair_count = sum(tiles[s].count(n) == 2 for s in tiles for n in set(tiles[s]))
        if pair_count == 7:
            yaku_list.append(('七對子', 2))
            # 七對子也可以複合斷幺九、混一色等，這裡簡化處理，繼續檢查其他性質

        # 3. 標準牌型解析 (分解為 4面子 + 1雀頭)
        structures = self._analyze_hand(tiles)
        
        if not structures and not any(y[0] == '七對子' for y in yaku_list):
             return [('無役', 0)], 0
        
        # 如果能組成標準牌型，找出番數最高的組合
        best_yaku_list = yaku_list
        best_fan = sum(f for _, f in yaku_list)

        # 對每一種可能的拆解方式進行役判定
        for melds, pair in structures:
            current_yaku = []
            
            # --- 門前/狀態役 ---
            if is_riichi and is_menzen: current_yaku.append(('立直', 1))
            if is_tsumo and is_menzen: current_yaku.append(('門前清自摸和', 1))
            
            # --- 染手系 ---
            suits = [s for s in ['m', 'p', 's'] if tiles[s]]
            has_honor = bool(tiles['z'])
            if len(suits) == 1:
                if not has_honor:
                    current_yaku.append(('清一色', 6 if is_menzen else 5))
                else:
                    current_yaku.append(('混一色', 3 if is_menzen else 2))
            
            # --- 役牌 ---
            dragon_map = {5: '白', 6: '發', 7: '中'}
            for (m_type, m_suit, m_val) in melds:
                if m_type == 'triplet' and m_suit == 'z':
                    if m_val in dragon_map:
                        current_yaku.append((dragon_map[m_val], 1))
                    # 簡化：假設場風自風都是東(1)
                    if m_val == 1: 
                        current_yaku.append(('風子（自風）', 1))

            # --- 斷幺九 ---
            has_yao = False
            # 檢查雀頭
            if pair[0] == 'z' or pair[1] in [1, 9]: has_yao = True
            # 檢查面子
            for m_type, m_suit, m_val in melds:
                if m_suit == 'z': has_yao = True
                elif m_type == 'triplet' and m_val in [1, 9]: has_yao = True
                elif m_type == 'sequence' and (m_val == 1 or m_val == 7): has_yao = True # 123 或 789
            
            if not has_yao:
                current_yaku.append(('斷幺九', 1))
            else:
                # 檢查混全帶/純全帶/混老頭
                is_all_yao_melds = True
                has_honor_in_melds = (pair[0] == 'z')
                
                for m_type, m_suit, m_val in melds:
                    if m_suit == 'z':
                        has_honor_in_melds = True
                    elif m_type == 'triplet':
                        if m_val not in [1, 9]: is_all_yao_melds = False
                    elif m_type == 'sequence':
                        if m_val not in [1, 7]: is_all_yao_melds = False
                    
                    if pair[0] != 'z' and pair[1] not in [1, 9]: is_all_yao_melds = False

                if is_all_yao_melds:
                    # 檢查是否全是刻子(對對和)
                    is_toitoi = all(m[0] == 'triplet' for m in melds)
                    if is_toitoi:
                        if has_honor_in_melds: current_yaku.append(('混老頭', 2))
                        # 清老頭在役滿檢查過了
                    else:
                        if has_honor_in_melds: current_yaku.append(('混全帯幺九', 2))
                        else: current_yaku.append(('純全帯幺九', 3))

            # --- 平和 (簡單判斷：全順子 + 雀頭非役牌 + 門前) ---
            if is_menzen:
                is_all_seq = all(m[0] == 'sequence' for m in melds)
                # 雀頭判斷簡化：只要不是三元牌
                is_pair_val = not (pair[0] == 'z' and pair[1] in [5, 6, 7])
                if is_all_seq and is_pair_val:
                    current_yaku.append(('平和', 1))

            # --- 杯口系 ---
            if is_menzen:
                seqs = [f"{m[1]}{m[2]}" for m in melds if m[0] == 'sequence']
                from collections import Counter
                seq_counts = Counter(seqs)
                pairs_count = sum(1 for c in seq_counts.values() if c >= 2)
                if pairs_count == 2:
                    current_yaku.append(('二盃口', 3))
                elif pairs_count == 1:
                    current_yaku.append(('一盃口', 1))

            # --- 三色同順 ---
            seq_vals = {'m': [], 'p': [], 's': []}
            for m in melds:
                if m[0] == 'sequence' and m[1] in seq_vals:
                    seq_vals[m[1]].append(m[2])
            
            # 找共同的數字
            common_seq = set(seq_vals['m']) & set(seq_vals['p']) & set(seq_vals['s'])
            if common_seq:
                current_yaku.append(('三色同順', 2))

            # --- 三色同刻 ---
            tri_vals = {'m': [], 'p': [], 's': []}
            for m in melds:
                if m[0] == 'triplet' and m[1] in tri_vals:
                    tri_vals[m[1]].append(m[2])
            common_tri = set(tri_vals['m']) & set(tri_vals['p']) & set(tri_vals['s'])
            if common_tri:
                current_yaku.append(('三色同刻', 2))

            # --- 一氣通貫 ---
            for s in ['m', 'p', 's']:
                has_123 = False
                has_456 = False
                has_789 = False
                for m in melds:
                    if m[0] == 'sequence' and m[1] == s:
                        if m[2] == 1: has_123 = True
                        if m[2] == 4: has_456 = True
                        if m[2] == 7: has_789 = True
                if has_123 and has_456 and has_789:
                    current_yaku.append(('一氣通貫', 2))

            # --- 對對和 ---
            if all(m[0] == 'triplet' for m in melds):
                current_yaku.append(('対々和', 2))
                
            # --- 三暗刻 (假設所有輸入的手牌都是暗刻) ---
            triplets_count = sum(1 for m in melds if m[0] == 'triplet')
            if triplets_count >= 3:
                current_yaku.append(('三暗刻', 2))
            
            # --- 小三元 ---
            dragons = sum(1 for m in melds if m[0] == 'triplet' and m[1] == 'z' and m[2] in [5,6,7])
            pair_is_dragon = (pair[0] == 'z' and pair[1] in [5,6,7])
            if dragons == 2 and pair_is_dragon:
                current_yaku.append(('小三元', 2))

            # 計算此組合的總番
            current_fan = sum(f for _, f in current_yaku)
            if current_fan > best_fan:
                best_yaku_list = current_yaku
                best_fan = current_fan

        # 合併七對子結果（如果有）
        if best_fan == 0 and not best_yaku_list:
             return [('無役', 0)], 0
             
        return best_yaku_list, best_fan

    def _check_yakuman(self, tiles):
        """檢查役滿"""
        yaku = []
        counts = self._count_all(tiles)
        
        # 國士無雙
        yao = [('m',1),('m',9),('p',1),('p',9),('s',1),('s',9),
               ('z',1),('z',2),('z',3),('z',4),('z',5),('z',6),('z',7)]
        if all(counts.get(k, 0) >= 1 for k in yao) and sum(counts.values()) == 14:
            yaku.append(('國士無雙', 13))
            return yaku

        # 九蓮寶燈
        for s in ['m', 'p', 's']:
            if len(tiles[s]) == 14:
                ref = [1,1,1,2,3,4,5,6,7,8,9,9,9]
                if sorted(tiles[s]) == ref:
                    yaku.append(('九蓮寶燈', 13))
                    return yaku

        # 字一色
        if len(tiles['z']) == 14:
            yaku.append(('字一色', 13))
            return yaku

        # 綠一色 (s23468 + z6)
        is_green = True
        for s in tiles:
            for n in tiles[s]:
                if not ( (s=='s' and n in [2,3,4,6,8]) or (s=='z' and n==6) ):
                    is_green = False
        if is_green:
            yaku.append(('綠一色', 13))
            return yaku

        # 大三元 / 大四喜 / 四暗刻 需要面子解析，這裡做簡單統計檢查
        triplets = 0
        dragons = 0
        winds = 0
        for k, v in counts.items():
            if v >= 3:
                triplets += 1
                if k[0] == 'z':
                    if k[1] in [5,6,7]: dragons += 1
                    if k[1] in [1,2,3,4]: winds += 1
        
        if dragons == 3: yaku.append(('大三元', 13))
        if winds == 4: yaku.append(('大四喜', 13))
        if triplets == 4: yaku.append(('四暗刻', 13)) # 簡化：假設暗刻
        
        return yaku

    def _analyze_hand(self, tiles):
        """
        將手牌分解為所有可能的 (面子列表, 雀頭) 組合
        返回: [ ( [(type, suit, val), ...], (suit, val) ), ... ]
        """
        results = []
        
        # 找出可能的雀頭
        pair_candidates = []
        for s in tiles:
            for n in set(tiles[s]):
                if tiles[s].count(n) >= 2:
                    pair_candidates.append((s, n))
        
        for p_suit, p_val in pair_candidates:
            # 複製並移除雀頭
            rem_tiles = {s: sorted(tiles[s][:]) for s in tiles}
            rem_tiles[p_suit].remove(p_val)
            rem_tiles[p_suit].remove(p_val)
            
            # 嘗試遞迴分解剩餘12張牌
            found_melds = self._get_melds_recursive(rem_tiles)
            for melds in found_melds:
                results.append((melds, (p_suit, p_val)))
                
        return results

    def _get_melds_recursive(self, tiles):
        """遞迴找出所有面子組合"""
        # 檢查是否為空
        if sum(len(tiles[s]) for s in tiles) == 0:
            return [[]]
        
        # 找第一張牌
        first_suit = next(s for s in tiles if tiles[s])
        first_val = tiles[first_suit][0]
        
        possible_combinations = []
        
        # 1. 嘗試刻子
        if tiles[first_suit].count(first_val) >= 3:
            new_tiles = {s: tiles[s][:] for s in tiles}
            for _ in range(3): new_tiles[first_suit].remove(first_val)
            
            sub_results = self._get_melds_recursive(new_tiles)
            for res in sub_results:
                possible_combinations.append([('triplet', first_suit, first_val)] + res)
        
        # 2. 嘗試順子
        if first_suit != 'z' and first_val <= 7:
            if (first_val + 1) in tiles[first_suit] and (first_val + 2) in tiles[first_suit]:
                new_tiles = {s: tiles[s][:] for s in tiles}
                new_tiles[first_suit].remove(first_val)
                new_tiles[first_suit].remove(first_val + 1)
                new_tiles[first_suit].remove(first_val + 2)
                
                sub_results = self._get_melds_recursive(new_tiles)
                for res in sub_results:
                    possible_combinations.append([('sequence', first_suit, first_val)] + res)
                    
        return possible_combinations

    def _count_all(self, tiles):
        counts = {}
        for s in tiles:
            for n in tiles[s]:
                key = (s, n)
                counts[key] = counts.get(key, 0) + 1
        return counts

    def get_points(self, fan, is_tsumo=True):
        if fan == 0: return 0
        if fan >= 13: fan = 13
        elif fan >= 11: fan = 11
        elif fan >= 8: fan = 8
        elif fan >= 6: fan = 6
        elif fan >= 5: fan = 5
        
        pts = self.BASE_POINTS.get(fan, self.BASE_POINTS[1])
        return pts['tsumo'] if is_tsumo else pts['ron']


class MahjongGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("日本麻將計算器 - 進階版")
        self.root.geometry("800x900")
        self.mahjong = JapaneseMahjong()
        self.setup_ui()
    
    def setup_ui(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Microsoft JhengHei", 20, "bold"))
        style.configure("Result.TLabel", font=("Courier New", 12))
        
        ttk.Label(self.root, text="日本麻將計算器", style="Title.TLabel").pack(pady=20)
        
        # 輸入區
        frame_input = ttk.LabelFrame(self.root, text="手牌輸入", padding=15)
        frame_input.pack(fill="x", padx=20)
        
        ttk.Label(frame_input, text="範例: 123m456p789s11z (支援三色、一氣通貫等)").pack(anchor="w")
        self.entry = ttk.Entry(frame_input, font=("Arial", 14))
        self.entry.pack(fill="x", pady=10)
        self.entry.bind("<Return>", lambda e: self.calc())
        
        # 選項區
        frame_opts = ttk.Frame(self.root)
        frame_opts.pack(pady=10)
        self.var_tsumo = tk.BooleanVar(value=True)
        self.var_riichi = tk.BooleanVar(value=False)
        self.var_menzen = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(frame_opts, text="自摸", variable=self.var_tsumo).pack(side="left", padx=10)
        ttk.Checkbutton(frame_opts, text="立直", variable=self.var_riichi).pack(side="left", padx=10)
        ttk.Checkbutton(frame_opts, text="門前清", variable=self.var_menzen).pack(side="left", padx=10)
        
        # 按鈕
        ttk.Button(self.root, text="計算", command=self.calc, width=20).pack(pady=5)
        ttk.Button(self.root, text="清除", command=self.clear, width=20).pack(pady=5)
        
        # 結果區
        self.txt_result = tk.Text(self.root, height=20, font=("Microsoft JhengHei", 11))
        self.txt_result.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 標籤顏色
        self.txt_result.tag_config("title", foreground="blue", font=("Microsoft JhengHei", 12, "bold"))
        self.txt_result.tag_config("yaku", foreground="green")
        self.txt_result.tag_config("yakuman", foreground="red", font=("Microsoft JhengHei", 12, "bold"))
        self.txt_result.tag_config("error", foreground="red")

    def calc(self):
        hand = self.entry.get()
        self.txt_result.delete("1.0", "end")
        
        if not hand: return
        
        try:
            tiles = self.mahjong.parse_hand(hand)
            yaku_list, fan = self.mahjong.calculate_fan(
                tiles, 
                is_tsumo=self.var_tsumo.get(),
                is_menzen=self.var_menzen.get(),
                is_riichi=self.var_riichi.get()
            )
            
            points = self.mahjong.get_points(fan, self.var_tsumo.get())
            
            self._show_result(hand, yaku_list, fan, points)
            
        except Exception as e:
            self.txt_result.insert("end", f"錯誤: {str(e)}", "error")

    def _show_result(self, hand, yaku_list, fan, points):
        self.txt_result.insert("end", f"輸入手牌: {hand}\n")
        self.txt_result.insert("end", "-"*40 + "\n")
        
        if yaku_list[0][0] == '無役':
            self.txt_result.insert("end", "無法和牌 (無役 或 牌型不符)\n", "error")
            return

        for name, f in yaku_list:
            display = self.mahjong.YAKU_TABLE.get(name, {}).get('display', f"{name} ({f}番)")
            tag = "yakuman" if f >= 13 else "yaku"
            self.txt_result.insert("end", f"✓ {display}\n", tag)
            
        self.txt_result.insert("end", "-"*40 + "\n")
        
        summary = "役滿" if fan >= 13 else f"{fan} 番"
        self.txt_result.insert("end", f"總計: {summary}\n", "title")
        
        pt_type = "自摸" if self.var_tsumo.get() else "榮胡"
        self.txt_result.insert("end", f"{pt_type}點數: {points} 點\n")

    def clear(self):
        self.entry.delete(0, "end")
        self.txt_result.delete("1.0", "end")

if __name__ == "__main__":
    root = tk.Tk()
    app = MahjongGUI(root)
    root.mainloop()
