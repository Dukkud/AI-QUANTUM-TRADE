"""Deterministic paper broker. No live order transport."""
from dataclasses import dataclass

@dataclass
class PaperOrder:
    order_id: str
    asset: str
    direction: str
    entry: float
    stop_loss: float
    target: float
    quantity: float
    status: str = 'PAPER'

class PaperBroker:
    def __init__(self): self.orders=[]
    def submit(self, order: PaperOrder):
        if order.quantity <= 0: raise ValueError('quantity must be positive')
        self.orders.append(order); return order
