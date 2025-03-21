from enum import Enum
from typing import List, Tuple
import random

class Suit(Enum):
    SPADES = '♠'
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'

class Card:
    def __init__(self, rank: int, suit: Suit):
        if not 2 <= rank <= 14:
            raise ValueError("Rank must be between 2 and 14")
        self.rank = rank
        self.suit = suit

    def __str__(self):
        rank_str = {
            14: 'A', 13: 'K', 12: 'Q', 11: 'J'
        }.get(self.rank, str(self.rank))
        return f"{rank_str}{self.suit.value}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

class PokerEngine:
    def __init__(self):
        self.deck = self._create_deck()

    def _create_deck(self) -> List[Card]:
        deck = []
        for suit in Suit:
            for rank in range(2, 15):
                deck.append(Card(rank, suit))
        return deck

    def calculate_hand_strength(self, hole_cards: List[Card], community_cards: List[Card]) -> float:
        """计算当前手牌的相对强度"""
        if len(hole_cards) != 2:
            raise ValueError("Must have exactly 2 hole cards")
        if len(community_cards) > 5:
            raise ValueError("Cannot have more than 5 community cards")

        # 从牌组中移除已知的牌
        available_cards = [card for card in self.deck 
                         if card not in hole_cards and card not in community_cards]
        
        # 模拟对手可能的手牌
        win_count = 0
        total_simulations = 100  # 可以根据需要调整模拟次数
        
        for _ in range(total_simulations):
            # 随机选择对手的两张手牌
            opponent_cards = random.sample(available_cards, 2)
            
            # 随机补齐公共牌到5张
            remaining_cards = [card for card in available_cards 
                             if card not in opponent_cards]
            needed_cards = 5 - len(community_cards)
            if needed_cards > 0:
                simulation_community = community_cards + \
                    random.sample(remaining_cards, needed_cards)
            else:
                simulation_community = community_cards

            # 判断胜负
            if self._compare_hands(hole_cards, opponent_cards, simulation_community):
                win_count += 1

        return win_count / total_simulations

    def _get_hand_rank(self, hand: List[Card], community: List[Card]) -> Tuple[int, List[int]]:
        """计算一手牌的大小，返回(牌型等级, 同等级下的大小值列表)"""
        all_cards = hand + community
        all_cards.sort(key=lambda x: x.rank, reverse=True)
        
        # 检查同花顺
        for suit in Suit:
            suited_cards = [card for card in all_cards if card.suit == suit]
            if len(suited_cards) >= 5:
                for i in range(len(suited_cards) - 4):
                    if suited_cards[i].rank == suited_cards[i+4].rank + 4:
                        return (8, [suited_cards[i].rank])
        
        # 检查四条
        rank_count = {}  # 统计每个点数的数量
        for card in all_cards:
            rank_count[card.rank] = rank_count.get(card.rank, 0) + 1
        for rank, count in rank_count.items():
            if count == 4:
                kickers = [r for r in rank_count if r != rank]
                return (7, [rank, max(kickers)])
        
        # 检查葫芦
        three_rank = None
        pair_rank = None
        for rank, count in rank_count.items():
            if count == 3 and (three_rank is None or rank > three_rank):
                three_rank = rank
            elif count == 2 and (pair_rank is None or rank > pair_rank):
                pair_rank = rank
        if three_rank is not None and pair_rank is not None:
            return (6, [three_rank, pair_rank])
        
        # 检查同花
        for suit in Suit:
            suited_cards = [card for card in all_cards if card.suit == suit]
            if len(suited_cards) >= 5:
                return (5, [card.rank for card in suited_cards[:5]])
        
        # 检查顺子
        ranks = sorted(set(card.rank for card in all_cards), reverse=True)
        for i in range(len(ranks) - 4):
            if ranks[i] == ranks[i+4] + 4:
                return (4, [ranks[i]])
        
        # 检查三条
        if three_rank is not None:
            kickers = sorted([r for r in rank_count if r != three_rank], reverse=True)
            return (3, [three_rank] + kickers[:2])
        
        # 检查两对
        pairs = [r for r, c in rank_count.items() if c == 2]
        if len(pairs) >= 2:
            pairs.sort(reverse=True)
            kickers = [r for r in rank_count if r not in pairs[:2]]
            return (2, pairs[:2] + [max(kickers)])
        
        # 检查一对
        if pairs:
            kickers = [r for r in rank_count if r != pairs[0]]
            kickers.sort(reverse=True)
            return (1, [pairs[0]] + kickers[:3])
        
        # 高牌
        return (0, [card.rank for card in all_cards[:5]])

    def _compare_hands(self, hand1: List[Card], hand2: List[Card], 
                      community: List[Card]) -> bool:
        """比较两副手牌的大小，返回hand1是否胜出"""
        rank1, values1 = self._get_hand_rank(hand1, community)
        rank2, values2 = self._get_hand_rank(hand2, community)
        
        if rank1 != rank2:
            return rank1 > rank2
        
        # 如果牌型相同，比较同等级下的大小值
        for v1, v2 in zip(values1, values2):
            if v1 != v2:
                return v1 > v2
        
        return True  # 完全相等的情况，算作胜利