import tkinter as tk
from tkinter import messagebox, ttk


class JapaneseMahjong:
    """日本麻將計算器 - 核心邏輯類"""
    
    # 三元牌定義
    DRAGONS = {5: '白', 6: '發', 7: '中'}
    
    # 役表（核心役）
    YAKU_TABLE = {
        '清一色': {'fan': 6, 'description': '全同一花色'},
        '混一色': {'fan': 3, 'description': '字牌+同一花色'},
        '大三元': {'fan': 13, 'description': '3個三元牌刻子'},
        '七對子': {'fan': 2, 'description': '7對牌'},
        '対々和': {'fan': 2, 'description': '全部刻子'},
        '斷幺九': {'fan': 1, 'description': '無幺九牌'},
        '平和': {'fan': 1, 'description': '全部順子+對子'},
        '白': {'fan': 1, 'description': '白刻子'},
        '發': {'fan': 1, 'description': '發刻子'},
        '中': {'fan': 1, 'description': '中刻子'},
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
    
    SUIT_NAMES = {'m': '筒', 'p': '餅', 's': '索', 'z': '字'}
    
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
    
    def check_yaku(self, tiles: dict) -> list:
        """檢查所有符合的役"""
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
        
        # 統計所有數字出現次數
        counts = self._count_tiles(tiles)
        
        # 檢查大三元
        if self._check_big_three_dragons(counts):
            yaku_list.append(('大三元', 13))
            return yaku_list
        
        # 檢查三元牌
        for dragon_num, dragon_name in self.DRAGONS.items():
            if self._is_triplet(counts.get(dragon_num, 0)):
                yaku_list.append((dragon_name, 1))
        
        # 檢查七對子
        if self._check_seven_pairs(counts):
            yaku_list.append(('七對子', 2))
            return yaku_list
        
        # 檢查対々和（全刻子）
        if self._check_all_triplets(counts):
            yaku_list.append(('対々和', 2))
        
        # 檢查斷幺九（無幺九牌）
        if not self._has_terminal_or_honor(tiles):
            yaku_list.append(('斷幺九', 1))
        
        # 基本役：只要能形成順子+對子或刻子+對子就算有役
        if self._is_valid_winning_pattern(tiles):
            if not yaku_list or (len(yaku_list) == 1 and yaku_list[0][0] == '無役'):
                yaku_list = [('基本和', 1)]
        
        return yaku_list if yaku_list else [('無役', 0)]
    
    @staticmethod
    def _count_tiles(tiles: dict) -> dict:
        """統計所有牌的出現次數"""
        counts = {}
        for suit in tiles:
            for num in tiles[suit]:
                counts[num] = counts.get(num, 0) + 1
        return counts
    
    @staticmethod
    def _is_triplet(count: int) -> bool:
        """檢查是否為刻子或槓子"""
        return count >= 3
    
    @staticmethod
    def _check_big_three_dragons(counts: dict) -> bool:
        """檢查大三元"""
        dragon_triplets = sum(1 for d in [5, 6, 7] if counts.get(d, 0) >= 3)
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
        
        # 嘗試每一個可能的對子
        pair_candidates = {}
        for suit in ['m', 'p', 's', 'z']:
            for num in set(tiles[suit]):
                count = tiles[suit].count(num)
                if count >= 2:
                    if (suit, num) not in pair_candidates:
                        pair_candidates[(suit, num)] = 0
                    pair_candidates[(suit, num)] += count // 2
        
        # 嘗試每個候選對子
        for (pair_suit, pair_num) in pair_candidates.keys():
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
    
    def calculate_fan(self, tiles: dict) -> tuple:
        """計算總番數"""
        yaku_list = self.check_yaku(tiles)
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


class MahjongGUI:
    """日本麻將計算器 - GUI介面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("日本麻將計算器")
        self.root.geometry("800x900")
        self.mahjong = JapaneseMahjong()
        
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
            text="格式：123m456p789s11z (筒-餅-索-字牌，共14張)",
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
        
        ttk.Checkbutton(option_frame, text="自摸", variable=self.is_tsumo).pack(side="left", padx=10)
        ttk.Checkbutton(option_frame, text="門前清", variable=self.is_menzen).pack(side="left", padx=10)
    
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
        self.result_text.tag_config("points", foreground="#cc0000", font=("Courier", 10, "bold"))
        self.result_text.tag_config("error", foreground="#cc0000")
    
    def _insert_result(self, text: str, tag: str = ""):
        """向結果框插入文本"""
        self.result_text.config(state="normal")
        self.result_text.insert("end", text, tag)
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
            
            # 檢查手牌數量
            if total_tiles != 14:
                self._show_tile_error(tiles, total_tiles)
                return
            
            # 計算役和點數（根據實時選項）
            yaku_list, fan = self.mahjong.calculate_fan(tiles)
            is_tsumo = self.is_tsumo.get()  # 實時讀取選項
            tsumo_points = self.mahjong.get_points(fan, True)
            ron_points = self.mahjong.get_points(fan, False)
            
            self._display_result(tiles, yaku_list, fan, tsumo_points, ron_points, is_tsumo)
            
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
    
    def _display_result(self, tiles, yaku_list, fan, tsumo_points, ron_points, is_tsumo):
        """顯示計算結果"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        
        # 標題和分隔線
        self._insert_result("════════════════════════════════════════\n")
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
        
        # 符合的役
        self._insert_result("\n【符合的役】\n")
        if yaku_list and yaku_list[0][0] != '無役':
            for yaku_name, yaku_fan in yaku_list:
                self._insert_result(f"  ✓ {yaku_name}（{yaku_fan}番）\n", "yaku")
        else:
            self._insert_result("  ○ 無役（不能胡）\n")
        
        # 番數和點數
        self._insert_result("\n────────────────────────────────────────\n")
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
