-- Схема базы данных KudoAiBot

-- Добавляем столбцы для dual balance, если их нет (миграция)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='subscription_coins') THEN
        ALTER TABLE users ADD COLUMN subscription_coins INT DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='permanent_coins') THEN
        ALTER TABLE users ADD COLUMN permanent_coins INT DEFAULT 0;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT DEFAULT 'ru',
    
    -- НОВАЯ СИСТЕМА: Два типа монеток
    subscription_coins INT DEFAULT 0,  -- 🟢 Подписочные (сгорают через 30 дней)
    permanent_coins INT DEFAULT 0,     -- 🟣 Купленные (не сгорают никогда)
    
    -- Старые поля для обратной совместимости
    balance INT DEFAULT 0,
    plan TEXT DEFAULT 'free',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_blocked BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    plan TEXT NOT NULL,
    coins_granted INT NOT NULL,
    price_rub INT NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    transaction_type TEXT NOT NULL,
    feature TEXT,
    coins_delta INT NOT NULL,
    balance_before INT NOT NULL,
    balance_after INT NOT NULL,
    note TEXT,
    payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    feature TEXT NOT NULL,
    coins_spent INT NOT NULL,
    status TEXT DEFAULT 'processing',
    prompt TEXT,
    result_file_id TEXT,
    error_message TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    amount_rub INT NOT NULL,
    payment_type TEXT NOT NULL,
    plan_or_coins TEXT,
    status TEXT DEFAULT 'pending',
    confirmation_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
