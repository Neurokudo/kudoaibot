# app/handlers/states.py
"""Состояния пользователя для диалогов"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class UserState:
    """Состояние пользователя"""
    user_id: int
    current_screen: str = "main"
    video_model: Optional[str] = None  # "veo3" или "sora2"
    video_mode: Optional[str] = None   # "helper", "manual", "meme"
    waiting_for: Optional[str] = None  # Ожидание ввода от пользователя
    video_params: Dict[str, Any] = field(default_factory=dict)
    last_prompt: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    tryon_data: Dict[str, Any] = field(default_factory=dict)  # Данные для примерочной
    
    def reset(self):
        """Сброс состояния"""
        self.current_screen = "main"
        self.video_model = None
        self.video_mode = None
        self.waiting_for = None
        self.video_params = {}
        self.last_prompt = None
        self.tryon_data = {}

# Хранилище состояний пользователей
user_states: Dict[int, UserState] = {}

def get_user_state(user_id: int) -> UserState:
    """Получить или создать состояние пользователя"""
    if user_id not in user_states:
        user_states[user_id] = UserState(user_id=user_id)
    user_states[user_id].last_activity = datetime.now()
    return user_states[user_id]

def set_user_state(user_id: int, state_data: dict):
    """Установить состояние пользователя из словаря"""
    # Получаем существующее состояние или создаем новое
    if user_id not in user_states:
        user_states[user_id] = UserState(user_id=user_id)
    
    # Обновляем поля состояния из словаря
    state = user_states[user_id]
    for key, value in state_data.items():
        if hasattr(state, key):
            setattr(state, key, value)
    
    state.last_activity = datetime.now()

def clear_user_state(user_id: int):
    """Очистить состояние пользователя"""
    if user_id in user_states:
        user_states[user_id].reset()

def is_waiting_for_input(user_id: int) -> bool:
    """Проверить, ждёт ли бот ввода от пользователя"""
    state = get_user_state(user_id)
    return state.waiting_for is not None

