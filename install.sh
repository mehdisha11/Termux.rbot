#!/bin/bash

# 🤖 نصب و راه‌اندازی خودکار Termux Trading Bot

set -e

echo "╔════════════════════════════════════════╗"
echo "║  🤖 Termux Trading Bot - نصب کننده    ║"
echo "╚════════════════════════════════════════╝"
echo ""

# بررسی پایتون
echo "📋 بررسی پیش‌نیازها..."
if ! command -v python3 &> /dev/null; then
    echo "❌ پایتون 3 نصب نیست"
    echo "نصب کردن..."
    pkg install python3 -y
fi

echo "✅ پایتون نصب شده است"
python3 --version

# بروز رسانی pip
echo ""
echo "📦 بروز رسانی pip..."
python3 -m pip install --upgrade pip

# نصب وابستگی‌ها
echo ""
echo "📚 نصب وابستگی‌ها..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --no-cache-dir
else
    echo "❌ فایل requirements.txt پیدا نشد"
    exit 1
fi

# ایجاد فایل .env
echo ""
echo "⚙️  تنظیم محیط..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ فایل .env ایجاد شد"
        echo "⚠️  لطفا .env را تغییر دهید و API Keys را وارد کنید"
    fi
else
    echo "✅ فایل .env قبلا موجود است"
fi

# ایجاد پوشه‌های لازم
echo ""
echo "📁 ایجاد پوشه‌ها..."
mkdir -p data
mkdir -p logs
echo "✅ پوشه‌ها ایجاد شدند"

# نمایش پیام نهایی
echo ""
echo "╔════════════════════════════════════════╗"
echo "║       ✅ نصب موفق بود!                 ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📋 مراحل بعدی:"
echo ""
echo "1️⃣  فایل .env را تغییر دهید:"
echo "   nano .env"
echo ""
echo "2️⃣  API Keys Binance را وارد کنید:"
echo "   BINANCE_API_KEY=..."
echo "   BINANCE_API_SECRET=..."
echo ""
echo "3️⃣  API Keys Kucoin را وارد کنید:"
echo "   KUCOIN_API_KEY=..."
echo "   KUCOIN_API_SECRET=..."
echo "   KUCOIN_PASSPHRASE=..."
echo ""
echo "4️⃣  ربات را شروع کنید:"
echo "   python3 main.py"
echo ""
echo "📚 برای کمک بیشتر: README.md را بخوانید"
echo ""
