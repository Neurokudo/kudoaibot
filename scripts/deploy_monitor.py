#!/usr/bin/env python3
"""
Автоматический мониторинг Railway деплоя с AI-анализом ошибок
"""

import asyncio
import os
import re
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import anthropic


class RailwayMonitor:
    """Монитор деплоя Railway с автоматическим обнаружением и анализом ошибок"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs" / "deploy"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # AI клиент для анализа ошибок
        self.anthropic_client = None
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        self.error_patterns = [
            r"Error:",
            r"Exception:",
            r"Traceback",
            r"FATAL",
            r"CRITICAL",
            r"failed",
            r"crash",
            r"\[ERROR\]",
        ]
    
    def check_railway_cli(self) -> bool:
        """Проверка установлен ли Railway CLI"""
        try:
            result = subprocess.run(
                ["railway", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_deployment_logs(self, lines: int = 500) -> str:
        """Получение логов Railway"""
        try:
            print("📥 Получаю логи Railway...")
            result = subprocess.run(
                ["railway", "logs", "--lines", str(lines)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"❌ Ошибка получения логов: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "⏱️ Таймаут при получении логов"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def get_deployment_status(self) -> Dict:
        """Получение статуса деплоя"""
        try:
            result = subprocess.run(
                ["railway", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root
            )
            
            status_info = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            return status_info
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def detect_errors_in_logs(self, logs: str) -> List[Dict]:
        """Обнаружение ошибок в логах"""
        errors = []
        lines = logs.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Собираем контекст вокруг ошибки
                    context_start = max(0, i - 5)
                    context_end = min(len(lines), i + 10)
                    context = '\n'.join(lines[context_start:context_end])
                    
                    errors.append({
                        "line_number": i + 1,
                        "error_line": line.strip(),
                        "context": context,
                        "pattern_matched": pattern
                    })
                    break  # Одна ошибка на строку
        
        return errors
    
    def extract_traceback(self, logs: str) -> Optional[str]:
        """Извлечение полного traceback из логов"""
        traceback_pattern = r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)"
        matches = re.findall(traceback_pattern, logs, re.DOTALL)
        
        if matches:
            return matches[-1]  # Возвращаем последний traceback
        return None
    
    async def analyze_error_with_ai(self, error_info: Dict, full_logs: str) -> Optional[Dict]:
        """Анализ ошибки с помощью Claude AI"""
        if not self.anthropic_client:
            return None
        
        traceback = self.extract_traceback(full_logs)
        
        prompt = f"""Проанализируй эту ошибку из Railway deployment логов:

ОШИБКА:
{error_info['error_line']}

КОНТЕКСТ:
{error_info['context']}

{f"ПОЛНЫЙ TRACEBACK:\n{traceback}\n" if traceback else ""}

Проект: Telegram бот на aiogram 3.x с интеграцией различных AI сервисов.

Предоставь:
1. Краткое описание проблемы
2. Вероятную причину
3. Конкретный путь к файлу где скорее всего ошибка
4. Код исправления (если возможно определить)
5. Рекомендации по предотвращению подобных ошибок

Формат ответа - JSON:
{{
    "summary": "краткое описание",
    "cause": "причина",
    "file_path": "путь/к/файлу.py",
    "line_number": число или null,
    "fix_code": "код исправления" или null,
    "recommendations": ["рекомендация 1", "рекомендация 2"]
}}
"""
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Парсим JSON из ответа
            response_text = message.content[0].text
            
            # Пытаемся извлечь JSON из ответа
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return {
                    "summary": response_text,
                    "cause": "Не удалось распарсить",
                    "file_path": None,
                    "line_number": None,
                    "fix_code": None,
                    "recommendations": []
                }
        except Exception as e:
            print(f"❌ Ошибка AI-анализа: {e}")
            return None
    
    def save_error_report(self, errors: List[Dict], analyses: List[Dict]) -> Path:
        """Сохранение отчета об ошибках"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.logs_dir / f"error_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors),
            "errors": errors,
            "ai_analyses": analyses
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Также создаем читаемый markdown отчет
        md_path = self.logs_dir / f"error_report_{timestamp}.md"
        self.create_markdown_report(md_path, errors, analyses)
        
        return report_path
    
    def create_markdown_report(self, path: Path, errors: List[Dict], analyses: List[Dict]):
        """Создание Markdown отчета"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# 🔍 Отчет об ошибках деплоя\n\n")
            f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Всего ошибок найдено:** {len(errors)}\n\n")
            f.write("---\n\n")
            
            for i, (error, analysis) in enumerate(zip(errors, analyses), 1):
                f.write(f"## ❌ Ошибка #{i}\n\n")
                f.write(f"**Строка лога:** {error['line_number']}\n\n")
                f.write(f"```\n{error['error_line']}\n```\n\n")
                
                if analysis:
                    f.write(f"### 🤖 AI Анализ\n\n")
                    f.write(f"**Описание:** {analysis.get('summary', 'N/A')}\n\n")
                    f.write(f"**Причина:** {analysis.get('cause', 'N/A')}\n\n")
                    
                    if analysis.get('file_path'):
                        f.write(f"**Файл:** `{analysis['file_path']}`")
                        if analysis.get('line_number'):
                            f.write(f" (строка {analysis['line_number']})")
                        f.write("\n\n")
                    
                    if analysis.get('fix_code'):
                        f.write(f"**Предложенное исправление:**\n\n")
                        f.write(f"```python\n{analysis['fix_code']}\n```\n\n")
                    
                    if analysis.get('recommendations'):
                        f.write(f"**Рекомендации:**\n\n")
                        for rec in analysis['recommendations']:
                            f.write(f"- {rec}\n")
                        f.write("\n")
                
                f.write(f"### 📝 Контекст из логов\n\n")
                f.write(f"```\n{error['context']}\n```\n\n")
                f.write("---\n\n")
    
    def create_auto_fix_file(self, analyses: List[Dict]) -> Optional[Path]:
        """Создание файла с автоматическими исправлениями"""
        fixes = [a for a in analyses if a and a.get('fix_code')]
        
        if not fixes:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fix_path = self.logs_dir / f"auto_fixes_{timestamp}.md"
        
        with open(fix_path, 'w', encoding='utf-8') as f:
            f.write("# 🔧 Автоматические исправления\n\n")
            f.write(f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("⚠️ **ВНИМАНИЕ:** Проверьте каждое исправление перед применением!\n\n")
            f.write("---\n\n")
            
            for i, fix in enumerate(fixes, 1):
                f.write(f"## Исправление #{i}\n\n")
                f.write(f"**Файл:** `{fix['file_path']}`\n\n")
                f.write(f"**Проблема:** {fix['summary']}\n\n")
                f.write(f"**Исправление:**\n\n")
                f.write(f"```python\n{fix['fix_code']}\n```\n\n")
                f.write("---\n\n")
        
        return fix_path
    
    async def monitor_deployment(self, watch: bool = False, interval: int = 30):
        """Основной метод мониторинга деплоя"""
        print("🚀 Запуск мониторинга Railway деплоя...\n")
        
        # Проверка Railway CLI
        if not self.check_railway_cli():
            print("❌ Railway CLI не установлен!")
            print("📥 Установите: npm i -g @railway/cli")
            return
        
        print("✅ Railway CLI найден\n")
        
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 Итерация #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*60}\n")
            
            # Получаем статус
            status = self.get_deployment_status()
            print(f"📊 Статус: {'✅ OK' if status['success'] else '❌ Ошибка'}")
            
            # Получаем логи
            logs = self.get_deployment_logs(lines=1000)
            
            # Сохраняем логи
            log_file = self.logs_dir / f"railway_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(logs)
            print(f"💾 Логи сохранены: {log_file.name}")
            
            # Обнаруживаем ошибки
            errors = self.detect_errors_in_logs(logs)
            
            if errors:
                print(f"\n⚠️  Обнаружено ошибок: {len(errors)}")
                
                # AI анализ каждой ошибки
                analyses = []
                for i, error in enumerate(errors[:5], 1):  # Анализируем до 5 ошибок
                    print(f"\n🤖 AI-анализ ошибки #{i}...")
                    analysis = await self.analyze_error_with_ai(error, logs)
                    analyses.append(analysis)
                    
                    if analysis:
                        print(f"   ✅ Анализ завершен")
                        if analysis.get('file_path'):
                            print(f"   📁 Файл: {analysis['file_path']}")
                        if analysis.get('summary'):
                            print(f"   💡 {analysis['summary'][:100]}...")
                
                # Сохраняем отчет
                report_path = self.save_error_report(errors, analyses)
                print(f"\n📊 Отчет сохранен: {report_path}")
                print(f"📊 Markdown отчет: {report_path.with_suffix('.md')}")
                
                # Создаем файл с исправлениями
                fix_file = self.create_auto_fix_file(analyses)
                if fix_file:
                    print(f"🔧 Файл исправлений: {fix_file}")
                
                print("\n" + "="*60)
                print("🎯 ДЕЙСТВИЯ:")
                print("="*60)
                print(f"1. Откройте отчет: {report_path.with_suffix('.md')}")
                print("2. Проверьте предложенные исправления")
                print("3. Примените необходимые изменения")
                print("4. Сделайте новый деплой")
                print("="*60)
                
            else:
                print("✅ Ошибок не обнаружено!")
            
            if not watch:
                break
            
            print(f"\n⏳ Следующая проверка через {interval} секунд...")
            print("   (Ctrl+C для остановки)")
            await asyncio.sleep(interval)


async def main():
    """Точка входа"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Автоматический мониторинг Railway деплоя с AI-анализом"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Непрерывный мониторинг (по умолчанию: одна проверка)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Интервал проверки в секундах (по умолчанию: 30)"
    )
    parser.add_argument(
        "--anthropic-key",
        type=str,
        default=os.getenv("ANTHROPIC_API_KEY"),
        help="Anthropic API ключ для AI-анализа"
    )
    
    args = parser.parse_args()
    
    if not args.anthropic_key:
        print("⚠️  ANTHROPIC_API_KEY не указан - AI-анализ будет отключен")
        print("   Укажите через --anthropic-key или переменную окружения")
        print()
    
    monitor = RailwayMonitor(anthropic_api_key=args.anthropic_key)
    
    try:
        await monitor.monitor_deployment(
            watch=args.watch,
            interval=args.interval
        )
    except KeyboardInterrupt:
        print("\n\n👋 Мониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


