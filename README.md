# 🕌 Kitab Imam Mazhab RAG AI

Aplikasi RAG (Retrieval-Augmented Generation) Agentic AI untuk mempelajari kitab-kitab empat mazhab besar Islam melalui WhatsApp.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![WAHA](https://img.shields.io/badge/WAHA-Supported-brightgreen)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3-purple)

## 📋 Daftar Isi

- [Fitur](#-fitur)
- [Arsitektur](#-arsitektur)
- [Prasyarat](#-prasyarat)
- [Instalasi](#-instalasi)
- [Konfigurasi](#️-konfigurasi)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Penggunaan](#-penggunaan)
- [API Endpoints](#-api-endpoints)
- [Struktur Project](#-struktur-project)
- [Pengembangan](#-pengembangan)
- [Troubleshooting](#-troubleshooting)

## ✨ Fitur

### 🤖 AI Capabilities
- **RAG System**: Pencarian semantik dalam database pengetahuan mazhab
- **Agentic AI**: Multi-tool reasoning untuk menjawab berbagai jenis pertanyaan
- **Context-Aware**: Memahami konteks percakapan sebelumnya

### 📚 Knowledge Base
- **4 Mazhab Fiqih**: Hanafi, Maliki, Syafi'i, Hanbali
- **Biografi Imam**: Riwayat hidup, guru, dan murid para imam
- **Hukum Fiqih**: Thaharah, shalat, zakat, puasa, haji, nikah, muamalah
- **Kitab Rujukan**: Daftar kitab-kitab utama setiap mazhab
- **Perbandingan**: Perbedaan pendapat antar mazhab

### 📱 WhatsApp Integration
- **WAHA API**: Integrasi dengan WhatsApp HTTP API
- **Webhook**: Menerima dan membalas pesan secara real-time
- **Typing Indicator**: Indikator sedang mengetik
- **Reply**: Membalas pesan dengan quote

## 🏗 Arsitektur

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   WhatsApp      │────▶│   WAHA Server   │────▶│  Flask Webhook  │
│   User          │◀────│   (Docker)      │◀────│    Server       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────┼────────────────────────────────┐
                        │                                │                                │
                        ▼                                ▼                                ▼
                ┌───────────────┐              ┌─────────────────┐              ┌─────────────────┐
                │  RAG Engine   │              │  Agentic AI     │              │  Conversation   │
                │  (ChromaDB)   │◀────────────▶│  (Groq/Llama)   │◀────────────▶│    Manager      │
                └───────────────┘              └─────────────────┘              └─────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │  Knowledge    │
                │  Base (JSON)  │
                └───────────────┘
```

## 📋 Prasyarat

- **Python 3.10+**
- **Git Bash** (untuk Windows)
- **VS Code** (recommended)
- **WAHA Server** (running)
- **Groq API Key**

### Mendapatkan API Keys

1. **Groq API Key**:
   - Kunjungi [console.groq.com](https://console.groq.com)
   - Sign up atau login
   - Buat API key baru

2. **WAHA Server**:
   - Sudah terlihat dari screenshot: `https://waha-qikiufjwa2nh.cgk-max.sumopod.my.id`
   - Pastikan session WhatsApp aktif (WORKING)

## 🚀 Instalasi

### Windows (Git Bash)

```bash
# Clone atau buat direktori project
mkdir kitab-mazhab-ai
cd kitab-mazhab-ai

# Buat virtual environment
python -m venv venv
source venv/Scripts/activate  # Git Bash Windows

# Install dependencies
pip install -r requirements.txt

# Jalankan setup
python setup.py
```

### Linux/Mac

```bash
# Clone atau buat direktori project
mkdir kitab-mazhab-ai
cd kitab-mazhab-ai

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan setup
python setup.py
```

## ⚙️ Konfigurasi

### 1. Environment Variables

Copy `.env.example` ke `.env` dan edit:

```bash
cp .env.example .env
```

Edit file `.env`:

```env
# WAHA Configuration
WAHA_API_URL=https://waha-qikiufjwa2nh.cgk-max.sumopod.my.id
WAHA_SESSION=WBSBPKH230
WAHA_API_KEY=

# Groq API Configuration
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile

# Server Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
```

### 2. Setup Webhook di WAHA

Setelah server running, konfigurasi webhook di WAHA dashboard:

1. Buka WAHA Dashboard
2. Pilih session (WBSBPKH230)
3. Configure webhook URL: `http://YOUR_SERVER_IP:5000/webhook`
4. Enable events: `message`

Atau via API:
```bash
curl -X PUT "https://waha-qikiufjwa2nh.cgk-max.sumopod.my.id/api/sessions/WBSBPKH230/webhooks" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://YOUR_SERVER_IP:5000/webhook",
    "events": ["message"]
  }'
```

## 🎯 Menjalankan Aplikasi

### Development Mode

```bash
# Aktifkan virtual environment
source venv/Scripts/activate  # Windows Git Bash
# atau
source venv/bin/activate      # Linux/Mac

# Jalankan server
python app.py
```

### Production Mode

```bash
# Menggunakan Gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Atau dengan PM2 (Node.js process manager)
pm2 start "python app.py" --name kitab-mazhab-ai
```

### Dengan ngrok (untuk testing)

```bash
# Terminal 1: Jalankan server
python app.py

# Terminal 2: Expose dengan ngrok
ngrok http 5000
# Copy URL ngrok dan set sebagai webhook di WAHA
```

## 📱 Penggunaan

### Commands WhatsApp

| Command | Fungsi |
|---------|--------|
| `assalamualaikum` | Greeting dan pengenalan |
| `help` / `bantuan` | Panduan penggunaan |
| `reset` | Reset percakapan |

### Contoh Pertanyaan

```
👤 Siapa pendiri mazhab Syafi'i?
🤖 Imam Muhammad bin Idris al-Syafi'i lahir di Gaza tahun 150 H...

👤 Bagaimana cara wudhu menurut Hanafi?
🤖 Dalam mazhab Hanafi, rukun wudhu adalah...

👤 Apa perbedaan posisi tangan shalat antar mazhab?
🤖 Perbandingan posisi tangan saat shalat:
   - Hanafi: Di bawah pusar
   - Maliki: Dilepas di samping (sadl)
   - Syafi'i: Di dada
   - Hanbali: Di dada atau di bawah pusar

👤 Kitab apa saja yang menjadi rujukan mazhab Maliki?
🤖 Kitab-kitab utama mazhab Maliki:
   • Al-Muwaththa' karya Imam Malik
   • Al-Mudawwanah al-Kubra karya Sahnun...
```

## 🔌 API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "agent": true,
    "waha": true,
    "rag": true
  }
}
```

### Test Message (tanpa WAHA)
```http
POST /test
Content-Type: application/json

{
  "message": "Siapa Imam Syafi'i?",
  "phone": "test_user"
}
```

### Send Message
```http
POST /send
Content-Type: application/json

{
  "to": "6281234567890",
  "message": "Assalamualaikum"
}
```

### Webhook (untuk WAHA)
```http
POST /webhook
Content-Type: application/json

{
  "event": "message",
  "payload": {
    "from": "6281234567890@c.us",
    "body": "Pertanyaan user"
  }
}
```

## 📁 Struktur Project

```
kitab-mazhab-ai/
├── app.py                      # Main Flask application
├── setup.py                    # Setup script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .env                       # Environment variables (create this)
├── README.md                  # Documentation
│
├── core/
│   ├── __init__.py
│   ├── rag_engine.py          # RAG dengan ChromaDB
│   └── agent.py               # Agentic AI dengan Groq
│
├── integrations/
│   ├── __init__.py
│   └── waha_client.py         # WAHA API client
│
├── data/
│   ├── knowledge_base/
│   │   └── kitab_mazhab.json  # Knowledge base
│   └── chroma_db/             # Vector database (auto-generated)
│
└── logs/                      # Log files
```

## 🔧 Pengembangan

### Menambah Knowledge Base

Edit `data/knowledge_base/kitab_mazhab.json`:

```json
{
  "mazhab": {
    "syafii": {
      "hukum_fiqih": {
        "topik_baru": {
          "rukun": ["..."],
          "syarat": ["..."],
          "catatan": "..."
        }
      }
    }
  }
}
```

Setelah edit, reload RAG:
```bash
python -c "from core.rag_engine import get_rag_engine; rag = get_rag_engine(); rag.load_knowledge_base('./data/knowledge_base/kitab_mazhab.json')"
```

### Menambah Tools Baru

Edit `core/agent.py`:

```python
def _tool_new_function(self, param: str) -> str:
    """Deskripsi tool baru"""
    # Implementation
    return result

# Register di _initialize_tools()
ToolType.NEW_TOOL.value: Tool(
    name="new_tool",
    description="Deskripsi",
    parameters={"param": "description"},
    function=self._tool_new_function
)
```

## 🐛 Troubleshooting

### WAHA Connection Error
```
Error: WAHA_API_URL is required
```
**Solusi**: Pastikan `.env` file sudah dikonfigurasi dengan benar.

### Groq API Error
```
Error: GROQ_API_KEY is required
```
**Solusi**: 
1. Buat API key di [console.groq.com](https://console.groq.com)
2. Tambahkan ke `.env`

### ChromaDB Error
```
Error: sqlite3.OperationalError
```
**Solusi**: 
```bash
pip install pysqlite3-binary
```

Atau tambahkan di awal `app.py`:
```python
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

### Webhook Tidak Menerima Pesan
1. Pastikan URL webhook benar dan accessible dari internet
2. Gunakan ngrok untuk testing lokal
3. Cek WAHA dashboard untuk session status
4. Periksa log: `tail -f logs/app.log`

## 📝 License

MIT License - bebas digunakan untuk keperluan edukasi dan non-komersial.

## 🤝 Contributing

Kontribusi sangat diterima! Silakan buat Pull Request atau Issue.

## 🙏 Credits

- **Groq** - LLM API
- **WAHA** - WhatsApp HTTP API
- **ChromaDB** - Vector Database
- **Sentence Transformers** - Multilingual Embeddings

---

**Dibuat dengan ❤️ untuk kemudahan umat mempelajari ilmu fiqih**

```
"Barangsiapa yang dikehendaki Allah kebaikan padanya, 
maka Allah akan memahamkannya dalam urusan agama."
(HR. Bukhari & Muslim)
```
