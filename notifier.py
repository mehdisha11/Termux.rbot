import requests
import logging
from config import Config
from datetime import datetime

logger = logging.getLogger('TradingBot')


class TelegramNotifier:
    """اطلاع‌رسانی از طریق Telegram"""
    
    BASE_URL = 'https://api.telegram.org/bot'
    
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)
    
    def send_message(self, message):
        """ارسال پیام"""
        if not self.enabled:
            logger.warning("Telegram فعال نیست")
            return False
        
        try:
            url = f'{self.BASE_URL}{self.token}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("پیام Telegram ارسال شد")
            return True
        
        except Exception as e:
            logger.error(f"خطا در ارسال پیام Telegram: {e}")
            return False
    
    def notify_trade_opened(self, trade_info):
        """اطلاع‌رسانی باز شدن معامله"""
        message = f"""
🤖 <b>معامله جدید باز شد!</b>

📊 نماد: <code>{trade_info['symbol']}</code>
📈 نوع: <b>{trade_info['side'].upper()}</b>
💰 قیمت ورود: <b>${trade_info['price']:.2f}</b>
📦 اندازه: <b>{trade_info['size']}</b>

🎯 Take Profit: ${trade_info.get('take_profit', 'N/A')}
⛔ Stop Loss: ${trade_info.get('stop_loss', 'N/A')}

⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)
    
    def notify_trade_closed(self, trade_result):
        """اطلاع‌رسانی بسته‌شدن معامله"""
        pnl = trade_result.get('pnl', 0)
        pnl_percent = trade_result.get('pnl_percent', 0)
        
        emoji = "✅" if pnl > 0 else "❌"
        
        message = f"""
{emoji} <b>معامله بسته شد!</b>

📊 نماد: <code>{trade_result['symbol']}</code>
💰 قیمت ورود: ${trade_result['entry_price']:.2f}
💰 قیمت خروج: ${trade_result['exit_price']:.2f}

💵 سود/ضرر: <b>${pnl:.2f}</b> ({pnl_percent:.2f}%)
⏰ مدت: {trade_result.get('duration', 'N/A')}

📈 کل معاملات: {trade_result.get('total_trades', 0)}
🎯 درصد برد: {trade_result.get('win_rate', 0):.1f}%
"""
        self.send_message(message)
    
    def notify_error(self, error_message):
        """اطلاع‌رسانی خطا"""
        message = f"""
⚠️ <b>خطا در ربات!</b>

{error_message}

⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)
    
    def notify_balance(self, balance):
        """اطلاع‌رسانی موجودی"""
        message = f"""
💼 <b>وضعیت حساب</b>

💰 موجودی: <b>${balance:.2f}</b>
⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)
    
    def notify_signal(self, signal):
        """اطلاع‌رسانی سیگنال"""
        if not signal['should_trade']:
            return
        
        message = f"""
🎯 <b>سیگنال معاملاتی جدید!</b>

📊 نماد: <code>{signal.get('symbol', 'BTCUSDT')}</code>
📈 نوع: <b>{signal['trade_type']}</b>
💰 قیمت: <b>${signal['price']:.2f}</b>
💪 قوت سیگنال: <b>{signal['confidence']}/10</b>

🔍 Price Action: {signal['price_action']['entry_type']}
🌊 Elliott Wave: {signal['elliott_wave']['pattern']}

⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)
