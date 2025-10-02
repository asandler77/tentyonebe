# 🚀 Azure OpenAI Migration - Quick Guide

## 📋 What Changed

Your project has been successfully migrated from **AWS Bedrock** to **Azure OpenAI**!

### New files:
- `main_azure.py` - Main application with Azure OpenAI
- `azure_test.py` - Azure connection test
- `azure_config_example.env` - Configuration example
- `INSTRUCTIONS_AZURE.md` - Complete documentation
- `requirements.txt` - Updated dependencies

### Updated files:
- `requirements.txt` - Added `openai` and `python-dotenv`

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Azure OpenAI

In [Azure Portal](https://portal.azure.com):
1. Create "Azure OpenAI" resource
2. Deploy model (GPT-4 or GPT-3.5-turbo)
3. Get endpoint and API key

### 3. Create configuration
```bash
cp azure_config_example.env .env
```

Edit `.env`:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_MODEL_NAME=gpt-4
```

### 4. Test connection
```bash
python azure_test.py
```

### 5. Run application
```bash
python main_azure.py
```

## 🔄 Key Differences

| AWS Bedrock | Azure OpenAI |
|-------------|--------------|
| `boto3` | `openai` |
| Claude models | GPT-4/GPT-3.5 |
| AWS credentials | API key |
| `bedrock.invoke_model()` | `client.chat.completions.create()` |
| Text completion | Chat completion |

## 🧪 Testing

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

## 📚 Full Documentation

See `INSTRUCTIONS_AZURE.md` for detailed instructions on:
- Azure deployment
- Monitoring setup
- Cost optimization
- Troubleshooting

## 🆘 Help

If something doesn't work:
1. Run `python azure_test.py`
2. Check variables in `.env`
3. Make sure model is deployed in Azure
4. Check quotas and limits in Azure Portal

---
**Done! Your application now works with Azure OpenAI! 🎉**
