-- Миграция 001: Добавление двойной системы баланса
-- Дата: 2025-10-20
-- Описание: Добавляет столбцы subscription_coins и permanent_coins для двойной системы монет

DO $$ 
BEGIN
    -- Добавляем subscription_coins если его нет
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'subscription_coins'
    ) THEN
        ALTER TABLE users ADD COLUMN subscription_coins INT DEFAULT 0;
        RAISE NOTICE 'Добавлен столбец subscription_coins';
    ELSE
        RAISE NOTICE 'Столбец subscription_coins уже существует';
    END IF;
    
    -- Добавляем permanent_coins если его нет
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'permanent_coins'
    ) THEN
        ALTER TABLE users ADD COLUMN permanent_coins INT DEFAULT 0;
        RAISE NOTICE 'Добавлен столбец permanent_coins';
    ELSE
        RAISE NOTICE 'Столбец permanent_coins уже существует';
    END IF;
    
    -- Мигрируем старые балансы в permanent_coins если они есть
    UPDATE users 
    SET permanent_coins = balance 
    WHERE balance > 0 AND permanent_coins = 0;
    
    RAISE NOTICE 'Миграция dual_balance завершена успешно';
END $$;

