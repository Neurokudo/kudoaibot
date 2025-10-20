"""
Основной модуль для подключения к базе данных
"""
import os
import logging
import asyncpg
from typing import Optional, List, Dict, Any

log = logging.getLogger("database")

# Глобальный пул подключений
_db_pool: Optional[asyncpg.Pool] = None

async def init_db() -> bool:
    """Инициализация базы данных и создание таблиц"""
    global _db_pool
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        log.error("DATABASE_URL не установлен")
        return False
    
    try:
        log.info("Подключение к базе данных...")
        _db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=30
        )
        log.info("✅ Подключение к базе данных установлено")
        
        # Создание таблиц из схемы
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            async with _db_pool.acquire() as conn:
                await conn.execute(schema_sql)
            log.info("✅ Таблицы базы данных созданы/обновлены")
        
        # Применение миграций
        migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
        if os.path.exists(migrations_dir):
            migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
            for migration_file in migration_files:
                migration_path = os.path.join(migrations_dir, migration_file)
                try:
                    with open(migration_path, 'r', encoding='utf-8') as f:
                        migration_sql = f.read()
                    
                    async with _db_pool.acquire() as conn:
                        await conn.execute(migration_sql)
                    log.info(f"✅ Миграция применена: {migration_file}")
                except Exception as e:
                    log.warning(f"⚠️ Ошибка применения миграции {migration_file}: {e}")
        
        return True
        
    except Exception as e:
        log.error(f"❌ Ошибка инициализации базы данных: {e}")
        _db_pool = None
        return False

def get_db_pool() -> Optional[asyncpg.Pool]:
    """Получить пул подключений к БД"""
    return _db_pool

async def close_db():
    """Закрыть подключение к БД"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        log.info("✅ Подключение к базе данных закрыто")

async def execute_query(query: str, *args) -> str:
    """Выполнить запрос без возврата результата"""
    if not _db_pool:
        raise RuntimeError("База данных не инициализирована")
    
    async with _db_pool.acquire() as conn:
        return await conn.execute(query, *args)

async def fetch_one(query: str, *args) -> Optional[Dict[str, Any]]:
    """Выполнить запрос и вернуть одну строку"""
    if not _db_pool:
        raise RuntimeError("База данных не инициализирована")
    
    async with _db_pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None

async def fetch_all(query: str, *args) -> List[Dict[str, Any]]:
    """Выполнить запрос и вернуть все строки"""
    if not _db_pool:
        raise RuntimeError("База данных не инициализирована")
    
    async with _db_pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]
