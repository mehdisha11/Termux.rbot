import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# بارگذاری متغیرهای محیط
load_dotenv()

class Config:
    """تنظیمات پروژه"""
    
    # Binance
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    
    # Kucoin
    KUCOIN_API_KEY = os.getenv('KUCOIN_API_KEY')
    KUCOIN_API_SECRET = os.getenv('KUCOIN_API_SECRET')
    KUCOIN_PASSPHRASE = os.getenv('KUCOIN_PASSPHRASE')
    
    # تنظیمات تریدینگ
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 50))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 2))
    LEVERAGE = int(os.getenv('LEVERAGE', 5))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 2))
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 1))
    TIME_FRAME = os.getenv('TIME_FRAME', '15m')
    
    # کوین‌های مورد نظر
    SYMBOLS = os.getenv('SYMBOLS', 'BTCUSDT,ETHUSDT').split(',')
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # مسیرهای فایل
    DATA_DIR = 'data'
    LOGS_DIR = 'logs'
    TRADES_FILE = os.path.join(DATA_DIR, 'trades.json')
    BALANCE_FILE = os.path.join(DATA_DIR, 'balance.json')
    
    # تنظیمات Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 60))


class Logger:
    """سیستم Logging"""
    
    @staticmethod
    def setup():
        """راه‌اندازی Logging"""
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        
        logger = logging.getLogger('TradingBot')
        logger.setLevel(Config.LOG_LEVEL)
        
        # فرمت
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File Handler
        fh = logging.FileHandler(os.path.join(Config.LOGS_DIR, 'trading.log'))
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        return logger


class DataManager:
    """مدیریت داده‌ها"""
    
    def __init__(self):
        self.logger = logging.getLogger('TradingBot')
        os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    def save_trade(self, trade_data):
        """ذخیره معامله"""
        trades = self.load_trades()
        trades.append({
            **trade_data,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(Config.TRADES_FILE, 'w') as f:
            json.dump(trades, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"معامله ذخیره شد: {trade_data}")
    
    def load_trades(self):
        """بارگذاری تمام معاملات"""
        if os.path.exists(Config.TRADES_FILE):
            with open(Config.TRADES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_balance(self, balance_data):
        """ذخیره موجودی"""
        with open(Config.BALANCE_FILE, 'w') as f:
            json.dump({
                'balance': balance_data,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_balance(self):
        """بارگذاری موجودی"""
        if os.path.exists(Config.BALANCE_FILE):
            with open(Config.BALANCE_FILE, 'r') as f:
                return json.load(f)
        return {'balance': Config.INITIAL_CAPITAL}
    
    def get_statistics(self):
        """آمار معاملات"""
        trades = self.load_trades()
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0
            }
        
        winning = [t for t in trades if t.get('pnl', 0) > 0]
        losing = [t for t in trades if t.get('pnl', 0) < 0]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(trades) * 100) if trades else 0,
            'total_profit': sum(t.get('pnl', 0) for t in trades)
        }
