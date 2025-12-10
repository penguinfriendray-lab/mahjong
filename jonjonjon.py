import tkinter as tk
from tkinter import messagebox, ttk
from itertools import combinations

class JapaneseMahjong:
    """日本麻將計算類"""
    
    # 三元牌定義
    DRAGONS = {'5': '白', '6': '發', '7': '中'}
    # 風牌定義
    WINDS = {'E': '東', 'S': '南', 'W': '西', 'N': '北'}
    
    # 役表
    YAKU_TABLE = {
        '立直': {'fan': 1, 'description': '聽牌時宣言'},
        '門前清自摸和': {'fan': 1, 'description': '門前清且自摸胡'},
        '平和': {'fan': 1, 'description': '全部順子+對子'},
        '斷幺九': {'fan': 1, 'description': '無幺九牌'},
        '風子（自風）': {'fan': 1, 'description': '自風刻子'},
        '風子（場風）': {'fan': 1, 'description': '場風刻子'},
        '白': {'fan': 1, 'description': '白刻子'},
        '發': {'fan': 1, 'description': '發刻子'},
        '中': {'fan': 1, 'description': '中刻子'},
        '一盃口': {'fan': 1, 'description': '相同的順子對'},
        '二盃口': {'fan': 3, 'description': '2組相同的順子對'},
        '三色同順': {'fan': 2, 'description': '3種花色相同數字的順子'},
        '三色同刻': {'fan': 2, 'description': '3種花色相同數字的刻子'},
        '一氣通貫': {'fan': 2, 'description': '一種花色123-456-789'},
        '小三元': {'fan': 2, 'description': '2種三元牌刻子+1對'},
        '混老頭': {'fan': 2, 'description': '只含字牌和幺九牌'},
        '七對子': {'fan': 2, 'description': '7對牌'},
        '対々和': {'fan': 2, 'description': '全部刻子'},
        '混全帯幺九': {'fan': 2, 'description': '全部順子刻子含幺九字牌'},
        '清全帯幺九': {'fan': 3, 'description': '全部順子刻子含幺九，無字牌'},
        '清一色': {'fan': 6, 'description': '全同一花色'},
        '混一色': {'fan': 3, 'description': '字牌+同一花色'},
        '大三元': {'fan': 13, 'description': '3個三元牌刻子'},
        '四暗刻': {'fan': 13, 'description': '4個暗刻'},
        '天和': {'fan': 13, 'description': '莊家初始胡'},
        '地和': {'fan': 13, 'description': '閒家首輪胡'},
    }
    
    # 點數表
    BASE_POINTS = {
        0: {'tsumo': 1000, 'ron': 1000},    # 無番但有役
        1: {'tsumo': 1000, 'ron': 1000},
        2: {'tsumo': 2000, 'ron': 2000},
        3: {'tsumo': 3900, 'ron': 5800},
        4: {'tsumo': 7700, 'ron': 7700},
        5: {'tsumo': 8000, 'ron': 8000},    # 滿貫
        6: {'tsumo': 12000, 'ron': 12000},
        7: {'tsumo': 16000, 'ron': 16000},
        8: {'tsumo': 16000, 'ron': 16000},
        10: {'tsumo': 16000, 'ron': 16000}, # 跳滿
        13: {'tsumo': 16000, 'ron': 16000}, # 數え役滿
        15: {'tsumo': 24000, 'ron': 24000}, # 倍滿
        18: {'tsumo': 32000, 'ron': 32000}, # 三倍滿
        20: {'tsumo': 48000, 'ron': 48000}, # 數え役滿
    }
    
    def parse_hand(self, input_str):
        """解析手牌輸入"""
        tiles = {'m': [], 'p': [], 's': [], 'z': []}
        
        # 移除所有空格
        input_str = input_str.replace(' ', '').strip()
        
        if not input_str:
            raise ValueError("輸入為空！")
        
        current_suit = None
        i = 0
        
        while i < len(input_str):
            char = input_str[i]
            
            if char in 'mpsz':
                current_suit = char
                i += 1
            elif char.isdigit():
                if current_suit is None:
                    found_suit = False
                    for j in range(i - 1, -1, -1):
                        if input_str[j] in 'mpsz':
                            current_suit = input_str[j]
                            found_suit = True
                            break
                    
                    if not found_suit:
                        for j in range(i + 1, len(input_str)):
                            if input_str[j] in 'mpsz':
                                current_suit = input_str[j]
                                found_suit = True
                                break
                    
                    if not found_suit:
                        raise ValueError(f"輸入格式錯誤！數字 '{char}' 找不到對應的花色標記")
                
                tiles[current_suit].append(int(char))
                i += 1
            else:
                raise ValueError(f"輸入格式錯誤！無法識別的字符：'{char}'")
        
        for suit in tiles:
            tiles[suit].sort()
        
        return tiles
    
    def is_winning_hand(self, tiles):
        """檢查是否為有效的胡牌"""
        total = sum(len(tiles[s]) for s in tiles)
        return total == 14
    
    def check_triplet_or_pair(self, count):
        """檢查是否為刻子、槓子或對子"""
        if count == 2:
            return 'pair'
        elif count in [3, 4]:
            return 'triplet'
        return None
    
    def check_yaku(self, tiles, is_tsumo=True, is_menzen=True, jikaze=None, bakaze=None):
        """檢查所有役"""
        yaku_list = []
        
        # 檢查清一色（全同花色）
        non_empty_suits = [s for s in ['m', 'p', 's'] if tiles[s]]
        if len(non_empty_suits) == 1 and not tiles['z']:
            yaku_list.append(('清一色', 6))
            return yaku_list
        
        # 檢查混一色（字牌+同花色）
        if len(non_empty_suits) == 1 and tiles['z']:
            yaku_list.append(('混一色', 3))
            return yaku_list
        
        # 檢查對對和（全刻子）
        all_triplets = True
        triplet_count = 0
        for suit in tiles:
            counts = {}
            for num in tiles[suit]:
                counts[num] = counts.get(num, 0) + 1
            for count in counts.values():
                if count not in [2, 3, 4]:
                    all_triplets = False
                elif count in [3, 4]:
                    triplet_count += 1
        
        if all_triplets and triplet_count >= 3:
            yaku_list.append(('対々和', 2))
        
        # 檢查七對子
        pair_count = 0
        for suit in tiles:
            counts = {}
            for num in tiles[suit]:
                counts[num] = counts.get(num, 0) + 1
            for count in counts.values():
                if count == 2:
                    pair_count += 1
        
        if pair_count == 7:
            yaku_list.append(('七對子', 2))
            return yaku_list
        
        # 檢查斷幺九（無幺九牌）
        has_yaochuuhai = False
        for suit in ['m', 'p', 's']:
            if 1 in tiles[suit] or 9 in tiles[suit]:
                has_yaochuuhai = True
        if tiles['z']:
            has_yaochuuhai = True
        
        if not has_yaochuuhai and not all_triplets:
            yaku_list.append(('斷幺九', 1))
        
        # 檢查風牌
        if tiles['z']:
            z_counts = {}
            for num in tiles['z']:
                z_counts[num] = z_counts.get(num, 0) + 1
            
            # 檢查白、發、中
            for dragon_num, dragon_name in self.DRAGONS.items():
                if int(dragon_num) in z_counts and z_counts[int(dragon_num)] >= 3:
                    yaku_list.append((dragon_name, 1))
            
            # 檢查大三元
            dragon_triplets = sum(1 for d in ['5', '6', '7'] if int(d) in z_counts and z_counts[int(d)] >= 3)
            if dragon_triplets >= 3:
                yaku_list.append(('大三元', 13))
                return yaku_list
        
        # 檢查平和
        if is_menzen and not tiles['z']:
            has_only_sequences = True
            for suit in ['m', 'p', 's']:
                counts = {}
                for num in tiles[suit]:
                    counts[num] = counts.get(num, 0) + 1
                for count in counts.values():
                    if count not in [1, 2]:
                        has_only_sequences = False
            
            if has_only_sequences:
                yaku_list.append(('平和', 1))
        
        # 檢查立直
        if is_menzen and is_tsumo:
            yaku_list.append(('立直', 1))
        
        # 檢查門前清自摸和
        if is_menzen and is_tsumo:
            yaku_list.append(('門前清自摸和', 1))
        
        return yaku_list if yaku_list else [('無役', 0)]
    
    def calculate_fan(self, tiles, is_tsumo=True, is_menzen=True, jikaze=None, bakaze=None):
        """計算番數"""
        yaku_list = self.check_yaku(tiles, is_tsumo, is_menzen, jikaze, bakaze)
        total_fan = sum(fan for _, fan in yaku_list)
        return yaku_list, total_fan
    
    def get_points(self, fan, is_tsumo=True):
        """根據番數計算點數"""
        # 無役不能胡
        if fan == 0:
            return 0
        
        if fan in self.BASE_POINTS:
            points = self.BASE_POINTS[fan]
            return points['tsumo'] if is_tsumo else points['ron']
        elif fan >= 13:
            points = self.BASE_POINTS[13]
            return points['tsumo'] if is_tsumo else points['ron']
        return 0


class MahjongGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("日本麻將計算器")
        self.root.geometry("750x850")
        
        self.mahjong = JapaneseMahjong()
        
        # 標題
        title_frame = ttk.Frame(root)
        title_frame.pack(pady=15)
        
        title_label = ttk.Label(title_frame, text="日本麻將計算器", 
                               font=("Arial", 18, "bold"))
        title_label.pack()
        
        # 輸入區域
        input_frame = ttk.LabelFrame(root, text="輸入手牌", padding=15)
        input_frame.pack(padx=20, pady=10, fill="x")
        
        info_label = ttk.Label(input_frame, 
                              text="格式：123m456p789s11z (筒-餅-索-字牌，共14張)",
                              font=("Arial", 9), foreground="gray")
        info_label.pack(anchor="w", pady=(0, 5))
        
        info_label2 = ttk.Label(input_frame, 
                               text="字牌：1=東 2=南 3=西 4=北 5=白 6=發 7=中",
                               font=("Arial", 9), foreground="gray")
        info_label2.pack(anchor="w", pady=(0, 10))
        
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 13), width=40)
        self.input_entry.pack(pady=10, fill="x")
        self.input_entry.bind("<Return>", lambda e: self.calculate())
        
        # 選項區域
        option_frame = ttk.LabelFrame(root, text="設定選項", padding=10)
        option_frame.pack(padx=20, pady=10, fill="x")
        
        self.is_tsumo = tk.BooleanVar(value=True)
        self.is_menzen = tk.BooleanVar(value=True)
        
        tsumo_check = ttk.Checkbutton(option_frame, text="自摸", variable=self.is_tsumo)
        tsumo_check.pack(side="left", padx=5)
        
        menzen_check = ttk.Checkbutton(option_frame, text="門前清", variable=self.is_menzen)
        menzen_check.pack(side="left", padx=5)
        
        # 按鈕區域
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        
        calc_btn = ttk.Button(button_frame, text="計算", command=self.calculate)
        calc_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(button_frame, text="清除", command=self.clear)
        clear_btn.pack(side="left", padx=5)
        
        # 結果區域
        result_frame = ttk.LabelFrame(root, text="計算結果", padding=15)
        result_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.result_text = tk.Text(text_frame, font=("Courier", 11), height=20, 
                                   wrap="word", bg="white", relief="sunken", border=1)
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set, state="disabled")
        
        self.result_text.tag_config("title", foreground="#0066cc", font=("Courier", 11, "bold"))
        self.result_text.tag_config("yaku", foreground="#009900", font=("Courier", 10))
        self.result_text.tag_config("points", foreground="#cc0000", font=("Courier", 10, "bold"))
        self.result_text.tag_config("error", foreground="#cc0000")
    
    def display_result(self, text, tag=""):
        """更新結果文字框"""
        self.result_text.config(state="normal")
        if tag:
            self.result_text.insert("end", text, tag)
        else:
            self.result_text.insert("end", text)
        self.result_text.config(state="disabled")
    
    def calculate(self):
        """計算胡牌"""
        input_hand = self.input_entry.get().strip()
        
        if not input_hand:
            messagebox.showwarning("警告", "請輸入手牌！")
            return
        
        try:
            tiles = self.mahjong.parse_hand(input_hand)
            
            total_tiles = sum(len(tiles[s]) for s in tiles)
            if total_tiles != 14:
                suit_names = {'m': '筒', 'p': '餅', 's': '索', 'z': '字'}
                detail = "\n詳細分析：\n"
                for suit, name in suit_names.items():
                    if tiles[suit]:
                        detail += f"  {name}：{tiles[suit]} ({len(tiles[suit])}張)\n"
                messagebox.showerror("錯誤", f"手牌數量錯誤！\n當前：{total_tiles}張\n需要：14張{detail}")
                return
            
            yaku_list, fan = self.mahjong.calculate_fan(
                tiles, 
                is_tsumo=self.is_tsumo.get(),
                is_menzen=self.is_menzen.get()
            )
            
            tsumo_points = self.mahjong.get_points(fan, True)
            ron_points = self.mahjong.get_points(fan, False)
            
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", "end")
            
            result = "════════════════════════════════════════\n"
            self.display_result(result)
            self.display_result("        日本麻將計算結果\n", "title")
            self.display_result("════════════════════════════════════════\n")
            
            self.display_result(f"\n輸入手牌：{input_hand}\n")
            self.display_result(f"總牌數：{total_tiles}張\n\n")
            
            self.display_result("【手牌分析】\n")
            suit_names = {'m': '筒', 'p': '餅', 's': '索', 'z': '字'}
            for suit, name in suit_names.items():
                if tiles[suit]:
                    tiles_str = ''.join(map(str, tiles[suit]))
                    self.display_result(f"  {name}：{tiles_str} ({len(tiles[suit])}張)\n")
            
            self.display_result("\n【符合的役】\n")
            if yaku_list and yaku_list[0][0] != '無役':
                for yaku_name, yaku_fan in yaku_list:
                    yaku_info = f"  ✓ {yaku_name}（{yaku_fan}番）\n"
                    self.display_result(yaku_info, "yaku")
            else:
                self.display_result("  ○ 無役（不能胡）\n")
            
            self.display_result("\n────────────────────────────────────────\n")
            self.display_result(f"總番數：{fan}番\n\n")
            
            if fan > 0:
                points_info = f"自摸：{tsumo_points}點\n榮胡：{ron_points}點\n"
                self.display_result(points_info, "points")
            else:
                self.display_result("無役不能胡！\n", "error")
            
            self.display_result("\n════════════════════════════════════════\n")
            
            self.result_text.config(state="disabled")
            
        except ValueError as e:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", "end")
            self.display_result(f"❌ 輸入錯誤：\n{str(e)}", "error")
            self.result_text.config(state="disabled")
    
    def clear(self):
        """清除輸入和結果"""
        self.input_entry.delete(0, "end")
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")
        self.input_entry.focus()


def main():
    root = tk.Tk()
    gui = MahjongGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    """日本麻將計算類"""
    
    # 役表（基本役）
    YAKU_TABLE = {
        '平和': {'fan': 1, 'description': '全部順子+對子'},
        '斷幺九': {'fan': 1, 'description': '無幺九牌'},
        '風子（自風）': {'fan': 1, 'description': '自風刻子'},
        '風子（場風）': {'fan': 1, 'description': '場風刻子'},
        '三元牌（白）': {'fan': 1, 'description': '白刻子'},
        '三元牌（發）': {'fan': 1, 'description': '發刻子'},
        '三元牌（中）': {'fan': 1, 'description': '中刻子'},
        '一盃口': {'fan': 1, 'description': '相同的順子對'},
        '二盃口': {'fan': 3, 'description': '2組相同的順子對'},
        '三色同順': {'fan': 2, 'description': '3種花色相同數字的順子'},
        '三色同刻': {'fan': 2, 'description': '3種花色相同數字的刻子'},
        '一氣通貫': {'fan': 2, 'description': '一種花色123-456-789'},
        '小三元': {'fan': 2, 'description': '2種三元牌刻子+1對'},
        '混老頭': {'fan': 2, 'description': '只含字牌和幺九牌'},
        '七對子': {'fan': 2, 'description': '7對牌'},
        '対々和': {'fan': 2, 'description': '全部刻子'},
        '混全帯幺九': {'fan': 2, 'description': '全部順子刻子含幺九字牌'},
        '清全帯幺九': {'fan': 3, 'description': '全部順子刻子含幺九，無字牌'},
        '花牌': {'fan': 1, 'description': '所有順子'},
        '清一色': {'fan': 6, 'description': '全同一花色'},
        '混一色': {'fan': 3, 'description': '字牌+同一花色'},
        '字牌七對子': {'fan': 13, 'description': '7個字牌對'},
        '大三元': {'fan': 13, 'description': '3個三元牌刻子'},
        '四暗刻': {'fan': 13, 'description': '4個暗刻'},
        '天和': {'fan': 13, 'description': '莊家初始胡'},
        '地和': {'fan': 13, 'description': '閒家首輪胡'},
    }
    
    # 點數表（1番～13番的點數）
    BASE_POINTS = {
        1: {'tsumo': 1000, 'ron': 1000},
        2: {'tsumo': 2000, 'ron': 2000},
        3: {'tsumo': 3900, 'ron': 5800},
        4: {'tsumo': 7700, 'ron': 7700},
        5: {'tsumo': 8000, 'ron': 8000},
        6: {'tsumo': 12000, 'ron': 12000},
        7: {'tsumo': 16000, 'ron': 16000},
        8: {'tsumo': 16000, 'ron': 16000},
        10: {'tsumo': 16000, 'ron': 16000},
        13: {'tsumo': 16000, 'ron': 16000},
        15: {'tsumo': 24000, 'ron': 24000},
        18: {'tsumo': 32000, 'ron': 32000},
        20: {'tsumo': 48000, 'ron': 48000},
    }
    
    def parse_hand(self, input_str):
        """解析手牌輸入
        支持格式：
        - 123m456p789s11z (標準格式)
        - m123p456s789z11 (花色在數字前)
        - 1m2m3m4p5p6p7s8s9s1z1z (逐個標記)
        """
        tiles = {'m': [], 'p': [], 's': [], 'z': []}
        
        # 移除所有空格
        input_str = input_str.replace(' ', '').strip()
        
        if not input_str:
            raise ValueError("輸入為空！")
        
        current_suit = None
        i = 0
        
        while i < len(input_str):
            char = input_str[i]
            
            if char in 'mpsz':
                current_suit = char
                i += 1
            elif char.isdigit():
                # 如果之前沒有設置花色，向前找花色
                if current_suit is None:
                    # 向前查找最近的花色標記
                    found_suit = False
                    for j in range(i - 1, -1, -1):
                        if input_str[j] in 'mpsz':
                            current_suit = input_str[j]
                            found_suit = True
                            break
                    
                    # 如果向前沒找到，向後找
                    if not found_suit:
                        for j in range(i + 1, len(input_str)):
                            if input_str[j] in 'mpsz':
                                current_suit = input_str[j]
                                found_suit = True
                                break
                    
                    if not found_suit:
                        raise ValueError(f"輸入格式錯誤！數字 '{char}' 找不到對應的花色標記（m/p/s/z）")
                
                tiles[current_suit].append(int(char))
                i += 1
            else:
                raise ValueError(f"輸入格式錯誤！無法識別的字符：'{char}'")
        
        # 排序
        for suit in tiles:
            tiles[suit].sort()
        
        return tiles
    
    def is_winning_hand(self, tiles):
        """檢查是否為有效的胡牌"""
        total = sum(len(tiles[s]) for s in tiles)
        return total == 14
    
    def check_basic_yaku(self, tiles):
        """檢查基本役"""
        yaku_list = []
        
        # 檢查清一色（全同花色）
        non_empty_suits = [s for s in ['m', 'p', 's'] if tiles[s]]
        if len(non_empty_suits) == 1 and not tiles['z']:
            yaku_list.append(('清一色', 6))
            return yaku_list
        
        # 檢查混一色（字牌+同花色）
        if len(non_empty_suits) == 1 and tiles['z']:
            yaku_list.append(('混一色', 3))
            return yaku_list
        
        # 檢查對對和（全刻子）
        all_triplets = True
        for suit in tiles:
            numbers = tiles[suit]
            counts = {}
            for num in numbers:
                counts[num] = counts.get(num, 0) + 1
            for count in counts.values():
                if count not in [2, 3, 4]:
                    all_triplets = False
                    break
        
        if all_triplets:
            yaku_list.append(('對對和', 2))
        
        # 檢查七對子
        pair_count = 0
        for suit in tiles:
            numbers = tiles[suit]
            counts = {}
            for num in numbers:
                counts[num] = counts.get(num, 0) + 1
            for count in counts.values():
                if count == 2:
                    pair_count += 1
                elif count != 0:
                    break
        
        if pair_count == 7:
            yaku_list.append(('七對子', 2))
        
        # 檢查斷幺九（無幺九牌）
        has_yaochuuhai = False
        for suit in ['m', 'p', 's']:
            if 1 in tiles[suit] or 9 in tiles[suit]:
                has_yaochuuhai = True
        if tiles['z']:
            has_yaochuuhai = True
        
        if not has_yaochuuhai:
            yaku_list.append(('斷幺九', 1))
        
        return yaku_list
    
    def calculate_fan(self, tiles):
        """計算番數"""
        yaku_list = self.check_basic_yaku(tiles)
        total_fan = sum(fan for _, fan in yaku_list)
        return yaku_list, total_fan
    
    def get_points(self, fan, is_tsumo=True):
        """根據番數計算點數"""
        if fan in self.BASE_POINTS:
            points = self.BASE_POINTS[fan]
            return points['tsumo'] if is_tsumo else points['ron']
        elif fan >= 13:
            points = self.BASE_POINTS[13]
            return points['tsumo'] if is_tsumo else points['ron']
        return 0


class MahjongGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("日本麻將計算器")
        self.root.geometry("700x800")
        
        self.mahjong = JapaneseMahjong()
        
        # 標題
        title_frame = ttk.Frame(root)
        title_frame.pack(pady=15)
        
        title_label = ttk.Label(title_frame, text="日本麻將計算器", 
                               font=("Arial", 18, "bold"))
        title_label.pack()
        
        # 輸入區域
        input_frame = ttk.LabelFrame(root, text="輸入手牌", padding=15)
        input_frame.pack(padx=20, pady=10, fill="x")
        
        info_label = ttk.Label(input_frame, 
                              text="格式：123m456p789s11z (筒-餅-索-字牌，共14張)",
                              font=("Arial", 9), foreground="gray")
        info_label.pack(anchor="w", pady=(0, 10))
        
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 13), width=40)
        self.input_entry.pack(pady=10, fill="x")
        self.input_entry.bind("<Return>", lambda e: self.calculate())
        
        # 按鈕區域
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        
        calc_btn = ttk.Button(button_frame, text="計算", command=self.calculate)
        calc_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(button_frame, text="清除", command=self.clear)
        clear_btn.pack(side="left", padx=5)
        
        # 結果區域
        result_frame = ttk.LabelFrame(root, text="計算結果", padding=15)
        result_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # 建立文字區域
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.result_text = tk.Text(text_frame, font=("Courier", 11), height=25, 
                                   wrap="word", bg="white", relief="sunken",
                                   border=1)
        self.result_text.pack(side="left", fill="both", expand=True)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set, state="disabled")
        
        # 設定標籤顏色
        self.result_text.tag_config("title", foreground="#0066cc", font=("Courier", 11, "bold"))
        self.result_text.tag_config("yaku", foreground="#009900", font=("Courier", 10))
        self.result_text.tag_config("points", foreground="#cc0000", font=("Courier", 10, "bold"))
        self.result_text.tag_config("error", foreground="#cc0000")
    
    def display_result(self, text, tag=""):
        """更新結果文字框"""
        self.result_text.config(state="normal")
        if tag:
            self.result_text.insert("end", text, tag)
        else:
            self.result_text.insert("end", text)
        self.result_text.config(state="disabled")
    
    def calculate(self):
        """計算胡牌"""
        input_hand = self.input_entry.get().strip()
        
        if not input_hand:
            messagebox.showwarning("警告", "請輸入手牌！")
            return
        
        try:
            # 解析手牌
            tiles = self.mahjong.parse_hand(input_hand)
            
            # 檢查手牌數量
            total_tiles = sum(len(tiles[s]) for s in tiles)
            if total_tiles != 14:
                # 詳細的錯誤訊息
                suit_names = {'m': '筒', 'p': '餅', 's': '索', 'z': '字'}
                detail = "\n詳細分析：\n"
                for suit, name in suit_names.items():
                    if tiles[suit]:
                        detail += f"  {name}：{tiles[suit]} ({len(tiles[suit])}張)\n"
                    else:
                        detail += f"  {name}：無\n"
                messagebox.showerror("錯誤", f"手牌數量錯誤！\n當前：{total_tiles}張\n需要：14張{detail}")
                return
            
            # 計算役和番數
            yaku_list, fan = self.mahjong.calculate_fan(tiles)
            
            # 計算點數
            tsumo_points = self.mahjong.get_points(fan, True)
            ron_points = self.mahjong.get_points(fan, False)
            
            # 清空並顯示結果
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", "end")
            
            # 標題
            result = "════════════════════════════════════════\n"
            self.display_result(result)
            self.display_result("        日本麻將計算結果\n", "title")
            self.display_result("════════════════════════════════════════\n")
            
            # 輸入的手牌
            self.display_result(f"\n輸入手牌：{input_hand}\n")
            self.display_result(f"總牌數：{total_tiles}張\n\n")
            
            # 手牌分析
            self.display_result("【手牌分析】\n")
            suit_names = {'m': '筒', 'p': '餅', 's': '索', 'z': '字'}
            for suit, name in suit_names.items():
                if tiles[suit]:
                    tiles_str = ''.join(map(str, tiles[suit]))
                    self.display_result(f"  {name}：{tiles_str} ({len(tiles[suit])}張)\n")
            
            # 符合的役
            self.display_result("\n【符合的役】\n")
            if yaku_list:
                for yaku_name, yaku_fan in yaku_list:
                    yaku_info = f"  ✓ {yaku_name}（{yaku_fan}番）\n"
                    self.display_result(yaku_info, "yaku")
            else:
                self.display_result("  ○ 無特殊役（鳴き胡）\n")
            
            # 番數和點數
            self.display_result("\n────────────────────────────────────────\n")
            self.display_result(f"總番數：{fan}番\n\n")
            
            points_info = f"自摸：{tsumo_points}點\n榮胡：{ron_points}點\n"
            self.display_result(points_info, "points")
            
            self.display_result("\n════════════════════════════════════════\n")
            
            self.result_text.config(state="disabled")
            
        except ValueError as e:
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", "end")
            self.display_result(f"❌ 輸入錯誤：\n{str(e)}", "error")
            self.result_text.config(state="disabled")
    
    def clear(self):
        """清除輸入和結果"""
        self.input_entry.delete(0, "end")
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")
        self.input_entry.focus()


def main():
    root = tk.Tk()
    gui = MahjongGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()