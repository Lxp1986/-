import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from card_widget import CardSelector, CardButton
from poker_engine import PokerEngine, Card

class PokerOddsCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('德州扑克胜率分析')
        self.setMinimumSize(1200, 800)
        
        # 初始化扑克引擎
        self.poker_engine = PokerEngine()
        self.hole_cards = []
        self.community_cards = []
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(main_widget)
        
        # 创建顶部区域（手牌和公共牌显示区）
        top_area = QWidget()
        top_layout = QHBoxLayout(top_area)
        
        # 手牌区域
        hole_cards_widget = QWidget()
        hole_cards_layout = QVBoxLayout(hole_cards_widget)
        hole_cards_layout.addWidget(QLabel('手牌选择'))
        self.hole_cards_selector = CardSelector()
        self.hole_cards_selector.card_selected.connect(self.on_hole_card_selected)
        self.hole_cards_selector.card_deselected.connect(self.on_hole_card_deselected)
        hole_cards_layout.addWidget(self.hole_cards_selector)
        top_layout.addWidget(hole_cards_widget)
        
        # 公共牌区域
        community_cards_widget = QWidget()
        community_cards_layout = QVBoxLayout(community_cards_widget)
        community_cards_layout.addWidget(QLabel('公共牌选择'))
        self.community_cards_selector = CardSelector()
        self.community_cards_selector.card_selected.connect(self.on_community_card_selected)
        self.community_cards_selector.card_deselected.connect(self.on_community_card_deselected)
        community_cards_layout.addWidget(self.community_cards_selector)
        top_layout.addWidget(community_cards_widget)
        
        # 添加顶部区域到主布局
        main_layout.addWidget(top_area)
        
        # 创建底部区域（胜率显示区和牌面显示区）
        bottom_area = QWidget()
        bottom_layout = QVBoxLayout(bottom_area)
        
        # 添加重置按钮
        reset_button = QPushButton('重置')
        reset_button.clicked.connect(self.reset_cards)
        bottom_layout.addWidget(reset_button)
        
        # 添加胜率显示标签
        self.odds_label = QLabel('请选择手牌和公共牌以查看胜率分析')
        self.odds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(self.odds_label)
        
        # 添加牌面显示区
        cards_display = QWidget()
        cards_layout = QHBoxLayout(cards_display)
        
        # 手牌显示区
        hole_cards_display = QWidget()
        hole_cards_display_layout = QVBoxLayout(hole_cards_display)
        hole_cards_display_layout.addWidget(QLabel('当前手牌'))
        self.hole_cards_buttons = QHBoxLayout()
        hole_cards_display_layout.addLayout(self.hole_cards_buttons)
        cards_layout.addWidget(hole_cards_display)
        
        # 公共牌显示区
        community_cards_display = QWidget()
        community_cards_display_layout = QVBoxLayout(community_cards_display)
        community_cards_display_layout.addWidget(QLabel('当前公共牌'))
        self.community_cards_buttons = QHBoxLayout()
        community_cards_display_layout.addLayout(self.community_cards_buttons)
        cards_layout.addWidget(community_cards_display)
        
        bottom_layout.addWidget(cards_display)
        main_layout.addWidget(bottom_area)
    
    def on_hole_card_selected(self, card: Card):
        if len(self.hole_cards) < 2:
            self.hole_cards.append(card)
            self.community_cards_selector.disable_card(card)
            self.update_odds()
        else:
            self.hole_cards_selector.enable_card(card)
    
    def on_hole_card_deselected(self, card: Card):
        if card in self.hole_cards:
            self.hole_cards.remove(card)
            self.community_cards_selector.enable_card(card)
            self.update_odds()
    
    def on_community_card_selected(self, card: Card):
        if len(self.community_cards) < 5:
            self.community_cards.append(card)
            self.hole_cards_selector.disable_card(card)
            self.update_odds()
        else:
            self.community_cards_selector.enable_card(card)
    
    def on_community_card_deselected(self, card: Card):
        if card in self.community_cards:
            self.community_cards.remove(card)
            self.hole_cards_selector.enable_card(card)
            self.update_odds()
    
    def _clear_card_displays(self):
        # 清空手牌显示区
        while self.hole_cards_buttons.count():
            item = self.hole_cards_buttons.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 清空公共牌显示区
        while self.community_cards_buttons.count():
            item = self.community_cards_buttons.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def update_odds(self):
        # 清空现有的牌面显示
        self._clear_card_displays()
        
        # 更新手牌显示
        for card in self.hole_cards:
            button = CardButton(card)
            button.setEnabled(False)
            self.hole_cards_buttons.addWidget(button)
        
        # 更新公共牌显示
        for card in self.community_cards:
            button = CardButton(card)
            button.setEnabled(False)
            self.community_cards_buttons.addWidget(button)
        
        # 更新胜率显示
        if len(self.hole_cards) == 2:
            win_rate = self.poker_engine.calculate_hand_strength(
                self.hole_cards, self.community_cards
            )
            self.odds_label.setText(
                f'当前手牌胜率: {win_rate:.2%}\n'
                f'手牌: {", ".join(str(card) for card in self.hole_cards)}\n'
                f'公共牌: {", ".join(str(card) for card in self.community_cards) or "无"}')
        else:
            self.odds_label.setText('请选择两张手牌以查看胜率分析')
    
    def reset_cards(self):
        self.hole_cards = []
        self.community_cards = []
        self.hole_cards_selector.reset()
        self.community_cards_selector.reset()
        self.odds_label.setText('请选择手牌和公共牌以查看胜率分析')

def main():
    app = QApplication(sys.argv)
    window = PokerOddsCalculator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()