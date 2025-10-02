# 21 Questions Game - Azure OpenAI Version

## Project Overview

This is a Flask application implementing the classic "21 Questions" game using Azure OpenAI. The AI thinks of a secret word, and players have up to 21 questions to guess it.

## Differences from AWS version

- **Azure OpenAI instead of AWS Bedrock**: Uses Azure OpenAI Service instead of AWS Bedrock
- **GPT-4/GPT-3.5 models**: Support for modern OpenAI models
- **Improved error handling**: More detailed problem diagnostics
- **Environment variables**: Using .env files for configuration

## Features

- **AI-Powered Word Generation**: Uses Azure OpenAI to generate random secret words
- **Smart Answer System**: AI referee provides "yes", "no", or "unclear" responses
- **Multiple Guess Formats**: Supports various question formats
- **Game State Management**: Tracks question count and game progress
- **Reveal Command**: Players can reveal the word at any time
- **Health Check**: Endpoint for checking application status

## Prerequisites

### 1. Azure OpenAI Setup
- Azure subscription with access to Azure OpenAI Service
- Created Azure OpenAI resource
- Deployed model (GPT-4 or GPT-3.5-turbo)
- API key and endpoint URL

### 2. Python Environment
- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

### 1. Clone/Download the Project
```bash
git clone <your-repository-url>
cd twentyonebe
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## Azure OpenAI Configuration

### 1. Creating Azure OpenAI Resource

1. Sign in to [Azure Portal](https://portal.azure.com)
2. Create new "Azure OpenAI" resource
3. Select region and pricing tier
4. After creation, navigate to the resource

### 2. Model Deployment

1. In Azure Portal, open your Azure OpenAI resource
2. Go to "Model deployments" → "Manage Deployments"
3. Click "Create new deployment"
4. Select model (GPT-4 or GPT-3.5-turbo recommended)
5. Set deployment name (e.g., "gpt-4")

### 3. Getting Credentials

1. In Azure Portal, open your Azure OpenAI resource
2. Go to "Keys and Endpoint"
3. Copy:
   - **Endpoint**: URL like `https://your-resource.openai.azure.com/`
   - **Key 1** or **Key 2**: API key

### 4. Environment Variables Setup

Create `.env` file in project root:

```bash
cp azure_config_example.env .env
```

Edit `.env` file:

```env
# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_MODEL_NAME=gpt-4

# Additional settings
MAX_QUESTIONS=21
PORT=5000
DEBUG=false
```

## Running the Application

### 1. Connection Testing

First, test the Azure OpenAI connection:

```bash
python azure_test.py
```

If the test passes successfully, you'll see:
```
✅ SUCCESS! Azure OpenAI is working correctly!
🎉 ALL TESTS PASSED SUCCESSFULLY!
```

### 2. Local Development

```bash
python main_azure.py
```

Сервер запустится на `http://localhost:5000`

### 3. Production Deployment

Для продакшена используйте WSGI сервер, например Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main_azure:app
```

## API Endpoints

### 1. Health Check
**GET** `/health`

**Response:**
```json
{
    "status": "healthy",
    "service": "21 Questions Game - Azure OpenAI",
    "model": "gpt-4"
}
```

### 2. Start New Game
**POST** `/start_game`

**Response:**
```json
{
    "message": "Game started!",
    "secret_word_length": 5
}
```

### 3. Ask Question
**POST** `/ask`

**Request Body:**
```json
{
    "question": "Is it an animal?"
}
```

**Response:**
```json
{
    "answer": "yes"
}
```

**Possible Answers:**
- `"yes"` - Ответ утвердительный
- `"no"` - Ответ отрицательный
- `"unclear"` - ИИ не может определить ответ
- `"You won!"` - Правильная догадка
- `"You lose!"` - Превышено 21 вопрос
- `"The word I thought of is 'word'."` - Слово раскрыто

## Game Rules

### Question Types
1. **Regular Questions**: "Is it alive?", "Can you eat it?"
2. **Guess Attempts**: "dog", "is it a dog?", "is the word elephant?"
3. **Reveal Commands**: "reveal", "what is the word?", "tell me the word"

### Winning Conditions
- **Win**: Угадать правильное слово за 21 вопрос
- **Lose**: Превысить 21 вопрос без правильной догадки
- **Reveal**: Использовать команду раскрытия (завершает игру)

### Supported Guess Formats
- Прямое слово: `"dog"`
- Формат вопроса: `"is it dog"`
- Формальный вопрос: `"is the word dog"`
- С артиклями: `"is it a dog"`, `"is it an elephant"`

## Testing

### Test Azure OpenAI Connection
```bash
python azure_test.py
```

### Manual API Testing
Используйте curl или Postman:

```bash
# Health check
curl http://localhost:5000/health

# Start game
curl -X POST http://localhost:5000/start_game

# Ask question
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is it alive?"}'
```

## Troubleshooting

### Common Issues

1. **Azure OpenAI Credentials Error**
   - Проверьте правильность AZURE_OPENAI_ENDPOINT
   - Убедитесь, что AZURE_OPENAI_API_KEY корректный
   - Проверьте, что ресурс активен в Azure Portal

2. **Model Not Found Error**
   - Убедитесь, что модель развернута в Azure OpenAI Studio
   - Проверьте правильность AZURE_OPENAI_MODEL_NAME
   - Модель должна быть в статусе "Succeeded"

3. **Rate Limiting**
   - Проверьте квоты в Azure Portal
   - Уменьшите частоту запросов
   - Рассмотрите увеличение лимитов

4. **Import Errors**
   - Убедитесь, что виртуальное окружение активировано
   - Переустановите зависимости: `pip install -r requirements.txt`

5. **Port Already in Use**
   - Измените порт в `.env`: `PORT=5001`
   - Или завершите процесс, использующий порт 5000

### Debug Mode
Для разработки включите debug режим в `.env`:
```env
DEBUG=true
```

## Azure Deployment

### Azure App Service

1. Создайте Azure App Service
2. Настройте переменные окружения в Configuration
3. Разверните код через Git или VS Code
4. Убедитесь, что используется `main_azure.py`

### Azure Container Instances

Создайте Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "main_azure.py"]
```

## File Structure
```
twentyonebe/
├── main_azure.py              # Основное Flask приложение (Azure версия)
├── main.py                    # Оригинальная AWS версия
├── azure_test.py              # Тест подключения Azure OpenAI
├── bedrock_test.py           # Тест подключения AWS Bedrock
├── requirements.txt          # Python зависимости (обновлено для Azure)
├── azure_config_example.env  # Пример конфигурации
├── INSTRUCTIONS_AZURE.md     # Эта инструкция
├── INSTRUCTIONS.md           # Оригинальная инструкция для AWS
└── venv/                     # Виртуальное окружение
```

## Security Notes

- Никогда не коммитьте `.env` файл в систему контроля версий
- Используйте Azure Key Vault для продакшена
- Отключите debug режим в продакшене
- Рассмотрите rate limiting для публичных развертываний
- Регулярно ротируйте API ключи

## Cost Optimization

- Используйте GPT-3.5-turbo для экономии (дешевле GPT-4)
- Настройте лимиты токенов
- Мониторьте использование в Azure Portal
- Рассмотрите использование Azure Cost Management

## Monitoring

- Используйте Azure Application Insights для мониторинга
- Настройте алерты на превышение лимитов
- Логируйте ошибки и производительность

## Migration from AWS

Если мигрируете с AWS Bedrock:

1. Установите новые зависимости: `pip install -r requirements.txt`
2. Создайте ресурс Azure OpenAI и разверните модель
3. Настройте переменные окружения в `.env`
4. Протестируйте подключение: `python azure_test.py`
5. Запустите новую версию: `python main_azure.py`

Основные отличия:
- Другой API (OpenAI вместо Bedrock)
- Другая структура запросов (chat completions вместо text completion)
- Другая аутентификация (API key вместо AWS credentials)

## Support

При возникновении проблем:
1. Запустите `python azure_test.py` для диагностики
2. Проверьте статус Azure OpenAI Service
3. Проверьте логи приложения
4. Убедитесь в корректности переменных окружения

## License

[Add your license information here]
