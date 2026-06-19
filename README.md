# 🤖 Termux Trading Bot

ربات تریدینگ خودکار برای Termux | دریافت داده‌های عمومی از Binance و معامله در Kucoin Futures

## ✨ ویژگی‌ها

✅ **دریافت داده‌ها از Binance** (عمومی - بدون نیاز به API Key)
✅ **معاملات واقعی در Kucoin Futures**
✅ **تحلیل Price Action و Elliott Wave**
✅ **مدیریت ریسک هوشمند** (2% ریسک به ازای هر معامله)
✅ **Leverage خودکار** (5x پیش‌فرض)
✅ **Stop Loss و Take Profit خودکار**
✅ **اطلاع‌رسانی Telegram**
✅ **ثبت تمام معاملات** (CSV و JSON)
✅ **نمایش آمار و پیشرفت**
✅ **قابل اجرا در Termux**

## 📋 نیازمندی‌ها

- **Termux** یا هر محیط Linux دیگری
- **Python 3.8+**
- **pip** (Package Manager)
- **اتصال اینترنت پایدار**

## 🚀 نصب و راه‌اندازی

### 1️⃣ نصب در Termux

```bash
# بروز رسانی Termux
pkg update && pkg upgrade

# نصب Python
pkg install python

# Clone مخزن
git clone https://github.com/mehdisha11/Termux.rbot.git
cd Termux.rbot
```

### 2️⃣ نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

اگر مشکل داشتید، این را امتحان کنید:

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### 3️⃣ تنظیم API Keys

**الف) API Key Binance** (برای دریافت داده‌ها):
- برو به: https://www.binance.com/en/account/api-management
- یک API Key جدید ایجاد کن
- فقط بخش **Read** را فعال کن (برای امنیت)

**ب) API Keys Kucoin** (برای معاملات):
- برو به: https://www.kucoin.com/account/api
- یک API Key جدید ایجاد کن
- Permissions: **Trade** و **General**
- یادداشت کن: `API Key`, `Secret`, و `Passphrase`

### 4️⃣ تنظیم فایل `.env`

```bash
# تغییر نام فایل مثال
cp .env.example .env

# باز کردن فایل برای ویرایش
nano .env
```

پر کن این اطلاعات:

```env
# Binance API (فقط خواندن)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_secret_key

# Kucoin API (برای معاملات)
KUCOIN_API_KEY=your_kucoin_api_key
KUCOIN_API_SECRET=your_kucoin_api_secret
KUCOIN_PASSPHRASE=your_kucoin_passphrase

# تنظیمات تریدینگ
INITIAL_CAPITAL=50
RISK_PER_TRADE=2
LEVERAGE=5
TAKE_PROFIT_PERCENT=2
STOP_LOSS_PERCENT=1
TIME_FRAME=15m

# کوین‌های مورد نظر
SYMBOLS=BTCUSDT,ETHUSDT

# Telegram (اختیاری)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# دیگر تنظیمات
LOG_LEVEL=INFO
UPDATE_INTERVAL=60
```

**نحوه دریافت Telegram Token:**
1. از `@BotFather` در تلگرام صحبت کن
2. `/newbot` را وارد کن
3. نام و username را بده
4. Token رو کپی کن

### 5️⃣ اجرای ربات

```bash
python main.py
```

## 📊 نحوه کار

```
┌─────────────────────────────┐
│  دریافت داده‌های Binance    │ (هر 15 دقیقه)
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  تحلیل Price Action          │
│  + Elliott Wave              │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  تولید سیگنال معاملاتی       │
│  (LONG یا SHORT)             │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  قرار دادن معامله در Kucoin  │
│  + Stop Loss + Take Profit   │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  اطلاع‌رسانی Telegram        │
│  + ثبت داده‌ها              │
└─────────────────────────────┘
```

## 📁 ساختار پروژه

```
Termux.rbot/
├── main.py                 # فایل اصلی (ربات)
├── analysis.py             # تحلیل تکنیکی
├── kucoin_trader.py        # معاملات Kucoin
├── config.py               # تنظیمات و Logger
├── notifier.py             # اطلاع‌رسانی Telegram
├── requirements.txt        # پکیج‌های لازم
├── .env.example            # مثال فایل تنظیمات
├── .gitignore              # فایل‌های نادیده‌گرفته
└── README.md               # این فایل
```

## 🎯 تنظیمات پیشنهادی

| تنظیم | مقدار | توضیح |
|------|------|-------|
| **INITIAL_CAPITAL** | $50 | سرمایه شروع |
| **RISK_PER_TRADE** | 2% | ریسک به ازای هر معامله |
| **LEVERAGE** | 5x | اهرم معامله |
| **TIME_FRAME** | 15m | بازه زمانی (15 دقیقه) |
| **TAKE_PROFIT** | 2% | سود هدف |
| **STOP_LOSS** | 1% | متوقف‌کننده ضرر |
| **UPDATE_INTERVAL** | 60s | بازه بررسی (60 ثانیه) |

## 📊 خروجی و ثبت

ربات تمام اطلاعات را در این مسیرها ذخیره می‌کند:

```
data/
├── trades.json          # تمام معاملات
└── balance.json         # موجودی فعلی

logs/
└── trading.log          # لاگ‌های تفصیلی
```

## ⚠️ هشدارهای مهم

🔴 **هیچگاه API Secret را با کسی به اشتراک نگذارید!**
🔴 **پیش از معاملات واقعی، در حالت Demo تست کنید**
🔴 **سرمایه کمی از سرمایه اصلی شروع کنید**
🔴 **ربات را کنترل نکنید، اعتماد داشته باشید**

## 🛠️ عیب‌یابی

### ❌ خطا: `ModuleNotFoundError`

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### ❌ خطا: `Connection timeout`

```bash
# بررسی اتصال اینترنت
ping 8.8.8.8

# اگر مشکل بود، proxy استفاده کن یا VPN فعال کن
```

### ❌ خطا: `Invalid API Key`

- API Keys را دوبارה چک کن
- API Secret رو درست تایپ کن
- اطمینان حاصل کن که API Keys فعال هستند

### ❌ ربات داده دریافت نمی‌کند

```bash
# Test کن که آیا Binance در دسترس است
curl https://api.binance.com/api/v3/ping

# اگر جواب نداد، Binance ممکن محدود باشد
```

## 📈 نمایش معاملات

معاملات در فایل `data/trades.json` ذخیره می‌شوند:

```json
[
  {
    "order_id": "abc123",
    "symbol": "BTCUSDT",
    "side": "buy",
    "entry_price": 45000,
    "exit_price": 45900,
    "size": 0.1,
    "pnl": 90,
    "pnl_percent": 0.2,
    "timestamp": "2026-06-19T16:30:00"
  }
]
```

## 🤝 مشارکت

اگر اشکالی پیدا کردید یا بهبودی دارید:

```bash
git push origin feature/new-feature
```

## 📜 لایسنس

MIT License - آزادانه استفاده کنید!

## 👨‍💻 نویسنده

**Mehdi Sha** - https://github.com/mehdisha11

## 🙏 تشکر

- Binance برای API عمومی
- Kucoin برای Futures API
- TA-Lib برای شاخص‌های تکنیکی

---

**⭐ اگر این پروژه مفید بود، ستاره بدهید!**

**برای سوالات و پشتیبانی: [Issues](https://github.com/mehdisha11/Termux.rbot/issues)**

**آخرین بروز رسانی: 2026-06-19**
