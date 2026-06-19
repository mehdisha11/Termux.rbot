import requests
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

logger = logging.getLogger('TradingBot')


class BinanceDataFetcher:
    """دریافت داده‌های عمومی از Binance"""
    
    BASE_URL = 'https://api.binance.com/api/v3'
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_klines(self, symbol, interval='15m', limit=500):
        """
        دریافت کندل‌های تاریخی
        
        Args:
            symbol: نماد کوین (مثل BTCUSDT)
            interval: بازه زمانی (1m, 5m, 15m, 1h, etc.)
            limit: تعداد کندل‌ها (حداکثر 1000)
        
        Returns:
            DataFrame با OHLCV
        """
        try:
            endpoint = f'{self.BASE_URL}/klines'
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # تبدیل نوع داده‌ها
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            logger.info(f"دریافت {len(df)} کندل از {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"خطا در دریافت داده‌های {symbol}: {e}")
            return pd.DataFrame()
    
    def get_ticker(self, symbol):
        """دریافت قیمت فعلی"""
        try:
            endpoint = f'{self.BASE_URL}/ticker/price'
            params = {'symbol': symbol}
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            return float(response.json()['price'])
        
        except Exception as e:
            logger.error(f"خطا در دریافت قیمت {symbol}: {e}")
            return None
    
    def get_order_book(self, symbol, limit=5):
        """دریافت Order Book"""
        try:
            endpoint = f'{self.BASE_URL}/depth'
            params = {'symbol': symbol, 'limit': limit}
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'bids': [[float(p), float(q)] for p, q in data['bids']],
                'asks': [[float(p), float(q)] for p, q in data['asks']]
            }
        
        except Exception as e:
            logger.error(f"خطا در دریافت Order Book {symbol}: {e}")
            return None


class TechnicalAnalyzer:
    """تحلیل تکنیکی (Price Action + Elliott Wave)"""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_indicators(self, df):
        """محاسبه شاخص‌های تکنیکی"""
        try:
            # EMA
            df['ema_9'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
            df['ema_21'] = EMAIndicator(close=df['close'], window=21).ema_indicator()
            df['ema_50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
            
            # RSI
            df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
            
            # Bollinger Bands
            bb = BollingerBands(close=df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            
            # ADX
            adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
            df['adx'] = adx.adx()
            
            return df
        
        except Exception as e:
            self.logger.error(f"خطا در محاسبه شاخص‌ها: {e}")
            return df
    
    def detect_support_resistance(self, df, window=20):
        """تشخیص سطح‌های حمایت و مقاومت"""
        try:
            high = df['high'].rolling(window=window).max()
            low = df['low'].rolling(window=window).min()
            
            # آخرین سطح‌های تشخیص‌یافته
            last_resistance = high.iloc[-1]
            last_support = low.iloc[-1]
            
            return {
                'resistance': last_resistance,
                'support': last_support,
                'midpoint': (last_resistance + last_support) / 2
            }
        
        except Exception as e:
            self.logger.error(f"خطا در تشخیص Support/Resistance: {e}")
            return None
    
    def detect_price_action_signals(self, df):
        """تشخیص سیگنال‌های Price Action"""
        signals = {
            'bullish': False,
            'bearish': False,
            'strength': 0,
            'entry_type': None
        }
        
        try:
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Pin Bar (شمع‌های معکوس)
            if current['close'] > current['open']:  # بوم صعودی
                upper_wick = current['high'] - current['close']
                body = current['close'] - current['open']
                lower_wick = current['open'] - current['low']
                
                if upper_wick < body * 0.3 and lower_wick > body * 1.5:
                    signals['bullish'] = True
                    signals['entry_type'] = 'Pin Bar Bullish'
                    signals['strength'] = 8
            
            # EMA Crossover
            if current['ema_9'] > current['ema_21'] > current['ema_50']:
                signals['bullish'] = True
                signals['entry_type'] = 'EMA Bullish Alignment'
                signals['strength'] = 7
            elif current['ema_9'] < current['ema_21'] < current['ema_50']:
                signals['bearish'] = True
                signals['entry_type'] = 'EMA Bearish Alignment'
                signals['strength'] = 7
            
            # RSI Oversold/Overbought
            if current['rsi'] < 30 and signals['bullish']:
                signals['strength'] = min(10, signals['strength'] + 2)
            elif current['rsi'] > 70 and signals['bearish']:
                signals['strength'] = min(10, signals['strength'] + 2)
            
            return signals
        
        except Exception as e:
            self.logger.error(f"خطا در تشخیص Price Action: {e}")
            return signals
    
    def detect_elliott_waves(self, df):
        """تشخیص الگوهای Elliott Wave (ساده)"""
        try:
            recent = df.tail(20)
            
            # شمارش قله‌ها و دره‌ها
            highs = recent['high'].nlargest(3)
            lows = recent['low'].nsmallest(3)
            
            current_price = df.iloc[-1]['close']
            
            wave_info = {
                'pattern': 'Unknown',
                'position': None,
                'confidence': 0
            }
            
            # اگر قیمت بالاتر از قله‌های اخیر باشد = موج صعودی
            if current_price > highs.iloc[-1]:
                wave_info['pattern'] = 'Impulse Wave (Up)'
                wave_info['confidence'] = 6
            # اگر قیمت پایین‌تر از دره‌های اخیر باشد = موج نزولی
            elif current_price < lows.iloc[-1]:
                wave_info['pattern'] = 'Impulse Wave (Down)'
                wave_info['confidence'] = 6
            
            return wave_info
        
        except Exception as e:
            self.logger.error(f"خطا در تشخیص Elliott Waves: {e}")
            return {'pattern': 'Unknown', 'confidence': 0}
    
    def generate_signal(self, df):
        """تولید سیگنال معاملاتی"""
        try:
            df = self.calculate_indicators(df)
            
            price_action = self.detect_price_action_signals(df)
            elliott = self.detect_elliott_waves(df)
            support_res = self.detect_support_resistance(df)
            
            signal = {
                'timestamp': datetime.now().isoformat(),
                'price': df.iloc[-1]['close'],
                'price_action': price_action,
                'elliott_wave': elliott,
                'support_resistance': support_res,
                'should_trade': False,
                'trade_type': None,
                'confidence': 0
            }
            
            # تصمیم معاملاتی
            if price_action['bullish'] and price_action['strength'] >= 7:
                signal['should_trade'] = True
                signal['trade_type'] = 'LONG'
                signal['confidence'] = price_action['strength']
            
            elif price_action['bearish'] and price_action['strength'] >= 7:
                signal['should_trade'] = True
                signal['trade_type'] = 'SHORT'
                signal['confidence'] = price_action['strength']
            
            return signal
        
        except Exception as e:
            self.logger.error(f"خطا در تولید سیگنال: {e}")
            return None
