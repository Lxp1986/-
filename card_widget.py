from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from poker_engine import Card, Suit

class CardButton(QPushButton):
    def __init__(self, card: Card = None):
        super().__init__()
        self.card = card
        self.setFixedSize(60, 90)
        self.setStyleSheet(
            'QPushButton {'
            '   background-color: white;'
            '   border: 2px solid #ccc;'
            '   border-radius: 5px;'
            '   font-size: 16px;'
            '}'
            'QPushButton:checked {'
            '   background-color: #e0e0e0;'
            '   border: 2px solid #808080;'
            '}'
        )
        self.setCheckable(True)
        self.update_text()

    def update_text(self):
        if self.card:
            text = str(self.card)
            color = '#ff0000' if self.card.suit in [Suit.HEARTS, Suit.DIAMONDS] else '#000000'
            self.setStyleSheet(self.styleSheet() + f'QPushButton {{ color: {color}; }}')
            self.setText(text)
        else:
            self.setText('')

class CardSelector(QWidget):
    card_selected = pyqtSignal(Card)
    card_deselected = pyqtSignal(Card)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建扑克牌选择网格
        grid = QGridLayout()
        self.card_buttons = []
        
        # 添加所有可能的扑克牌
        row = 0
        for suit in Suit:
            col = 0
            for rank in range(2, 15):
                card = Card(rank, suit)
                button = CardButton(card)
                button.toggled.connect(lambda checked, c=card, b=button: 
                    self.on_card_toggled(checked, c, b))
                grid.addWidget(button, row, col)
                self.card_buttons.append(button)
                col += 1
            row += 1

        layout.addLayout(grid)

    def on_card_toggled(self, checked: bool, card: Card, button: CardButton):
        if checked:
            self.card_selected.emit(card)
        else:
            self.card_deselected.emit(card)

    def disable_card(self, card: Card):
        for button in self.card_buttons:
            if button.card == card:
                button.setEnabled(False)
                button.setChecked(False)
                break

    def enable_card(self, card: Card):
        for button in self.card_buttons:
            if button.card == card:
                button.setEnabled(True)
                break

    def reset(self):
        for button in self.card_buttons:
            button.setEnabled(True)
            button.setChecked(False)