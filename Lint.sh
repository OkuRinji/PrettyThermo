echo "🔍 Запуск линтера и исправление ошибок..."
ruff check --fix .

echo "🎨 Форматирование кода..."
ruff format .

echo "✅ Готово!"