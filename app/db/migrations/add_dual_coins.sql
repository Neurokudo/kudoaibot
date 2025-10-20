-- Миграция: Добавление двух типов монеток
-- Дата: 2025-10-20
-- Описание: Поддержка подписочных (сгорают) и постоянных (не сгорают) монеток

-- Добавляем новые колонки если их нет
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_coins INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS permanent_coins INT DEFAULT 0;

-- Мигрируем старые балансы в permanent_coins (не сгорающие)
UPDATE users 
SET permanent_coins = COALESCE(balance, 0)
WHERE permanent_coins = 0 AND balance > 0;

-- Комментарии для документации
COMMENT ON COLUMN users.subscription_coins IS '🟢 Подписочные монетки (сгорают через 30 дней)';
COMMENT ON COLUMN users.permanent_coins IS '🟣 Купленные монетки (не сгорают никогда)';
COMMENT ON COLUMN users.balance IS 'Старое поле, используется для обратной совместимости';

