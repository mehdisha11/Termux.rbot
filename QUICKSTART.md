# 🚀 راهنمای سریع

## نصب در 5 دقیقه

### 1️⃣ نصب کردن

```bash
git clone https://github.com/mehdisha11/Termux.rbot.git
cd Termux.rbot
bash install.sh
```

### 2️⃣ تنظیم API Keys

```bash
nano .env
```

**الف) Binance** (برای دریافت داده‌ها):
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

**ب) Kucoin** (برای معاملات):
```
KUCOIN_API_KEY=your_key_here
KUCOIN_API_SECRET=your_secret_here
KUCOIN_PASSPHRASE=your_passphrase_here
```

### 3️⃣ اجرا کردن

```bash
python3 main.py
```

## 📊 تنظیمات مهم

| تنظیم | معنی |
|------|------|
| `INITIAL_CAPITAL` | سرمایه شروع |
| `RISK_PER_TRADE` | ریسک به ازای هر معامله (%) |
| `LEVERAGE` | اهرم معامله |
| `TIME_FRAME` | بازه زمانی (15m, 1h, ...) |
| `UPDATE_INTERVAL` | بازه بررسی (ثانیه) |

## 🔍 نمایش معاملات

```bash
cat data/trades.json | python3 -m json.tool
```

## 📝 نمایش لاگ‌ها

```bash
tail -f logs/trading.log
```

## ⛔ متوقف کردن

```
Ctrl + C
```

## 🆘 کمک

- 📖 README.md را بخوانید
- 🐛 Issues را بررسی کنید
- 💬 یک Issue جدید ایجاد کنید

**موفق باشید! 🎯**
