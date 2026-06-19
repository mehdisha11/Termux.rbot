#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
import sys
from datetime import datetime, timedelta
from config import Config, Logger, DataManager
from analysis import BinanceDataFetcher, TechnicalAnalyzer
from kucoin_trader import KuCoinTrader
from notifier import TelegramNotifier

# راه‌اندازی Logging
logger = Logger.setup()
logger = logging.getLogger('TradingBot')


class TradingBot:
    """ربات تریدینگ خودکار"""
    
    def __init__(self):
        logger.info("🤖 ربات تریدینگ در حال راه‌اندازی...")
        
        self.data_fetcher = BinanceDataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.trader = KuCoinTrader()
        self.notifier = TelegramNotifier()
        self.data_manager = DataManager()
        
        self.active_trades = {}
        self.last_check_time = {}
        
        logger.info("✅ ربات آماده است!")
    
    def check_and_close_trades(self):
        """بررسی و بسته‌کردن معاملات"""
        try:
            open_orders = self.trader.get_open_orders()
            
            for order in open_orders:
                order_id = order['id']
                
                # بررسی وضعیت
                status = self.trader.get_order_status(order_id)
                
                if status and status['filled_size'] > 0:
                    # محاسبه PnL
                    entry_price = float(order['price'])
                    current_price = status['filled_price']
                    pnl = (current_price - entry_price) * status['filled_size']
                    pnl_percent = ((current_price - entry_price) / entry_price * 100) if entry_price else 0
                    
                    # ثبت معامله
                    trade_record = {
                        'order_id': order_id,
                        'symbol': order['symbol'],
                        'side': order['side'],
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'size': status['filled_size'],
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'status': status['status']
                    }
                    
                    self.data_manager.save_trade(trade_record)
                    
                    if pnl > 0:
                        logger.info(f"✅ معامله برنده: {order_id} | PnL: ${pnl:.2f}")
                    else:
                        logger.warning(f"❌ معامله بازنده: {order_id} | PnL: ${pnl:.2f}")
                    
                    # اطلاع‌رسانی
                    self.notifier.notify_trade_closed(trade_record)
        
        except Exception as e:
            logger.error(f"خطا در بررسی معاملات: {e}")
    
    def analyze_symbol(self, symbol):
        """تحلیل یک کوین"""
        try:
            logger.info(f"📊 تحلیل {symbol}...")
            
            # دریافت داده‌ها از Binance
            df = self.data_fetcher.get_klines(symbol, interval=Config.TIME_FRAME)
            
            if df.empty:
                logger.warning(f"❌ نتوانستم داده‌های {symbol} را دریافت کنم")
                return None
            
            # تحلیل تکنیکی
            signal = self.analyzer.generate_signal(df)
            
            if not signal:
                logger.warning(f"❌ نتوانستم سیگنال {symbol} را تولید کنم")
                return None
            
            return signal
        
        except Exception as e:
            logger.error(f"خطا در تحلیل {symbol}: {e}")
            return None
    
    def execute_trade(self, symbol, signal):
        """اجرای معامله"""
        try:
            if not signal['should_trade']:
                return False
            
            logger.info(f"🎯 سیگنال معاملاتی برای {symbol}: {signal['trade_type']}")
            
            # اطلاع‌رسانی
            self.notifier.notify_signal(signal)
            
            # قرار دادن معامله
            order = self.trader.place_trade(signal, signal['price'])
            
            if order:
                logger.info(f"✅ معامله ثبت شد: {order['order_id']}")
                
                # اطلاع‌رسانی
                self.notifier.notify_trade_opened(order)
                
                self.active_trades[order['order_id']] = order
                return True
            else:
                logger.warning(f"❌ نتوانستم معامله را ثبت کنم")
                return False
        
        except Exception as e:
            logger.error(f"خطا در اجرای معامله: {e}")
            self.notifier.notify_error(f"خطا در اجرای معامله: {str(e)}")
            return False
    
    def run(self):
        """اجرای اصلی ربات"""
        logger.info("🚀 ربات شروع به کار کرد!")
        logger.info(f"📝 تنظیمات:")
        logger.info(f"   • سرمایه اولیه: ${Config.INITIAL_CAPITAL}")
        logger.info(f"   • ریسک به ازای هر معامله: {Config.RISK_PER_TRADE}%")
        logger.info(f"   • Leverage: {Config.LEVERAGE}x")
        logger.info(f"   • بازه زمانی: {Config.TIME_FRAME}")
        logger.info(f"   • کوین‌های مورد نظر: {', '.join(Config.SYMBOLS)}")
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                logger.info(f"\n{'='*50}")
                logger.info(f"🔄 سیکل #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*50}")
                
                # بررسی معاملات باز
                self.check_and_close_trades()
                
                # تحلیل تمام کوین‌ها
                for symbol in Config.SYMBOLS:
                    signal = self.analyze_symbol(symbol)
                    
                    if signal and signal['should_trade']:
                        self.execute_trade(symbol, signal)
                
                # دریافت موجودی
                balance = self.trader.get_account_balance()
                if balance:
                    logger.info(f"💰 موجودی فعلی: ${balance:.2f}")
                    self.data_manager.save_balance(balance)
                
                # آمار معاملات
                stats = self.data_manager.get_statistics()
                logger.info(f"📈 آمار:")
                logger.info(f"   • کل معاملات: {stats['total_trades']}")
                logger.info(f"   • معاملات برنده: {stats['winning_trades']}")
                logger.info(f"   • معاملات بازنده: {stats['losing_trades']}")
                logger.info(f"   • درصد برد: {stats['win_rate']:.1f}%")
                logger.info(f"   • کل سود/ضرر: ${stats['total_profit']:.2f}")
                
                # صبر کردن برای سیکل بعدی
                logger.info(f"⏳ منتظر {Config.UPDATE_INTERVAL} ثانیه...")
                time.sleep(Config.UPDATE_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("\n⛔ ربات متوقف شد (توسط کاربر)")
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {e}")
            self.notifier.notify_error(f"خطای غیرمنتظره: {str(e)}")


def main():
    """نقطه ورود برنامه"""
    try:
        bot = TradingBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n👋 خداحافظ!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
