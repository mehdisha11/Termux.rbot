import requests
import json
import hmac
import hashlib
import time
import base64
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger('TradingBot')


class KuCoinTrader:
    """معاملات واقعی در Kucoin Futures"""
    
    BASE_URL = 'https://api-futures.kucoin.com'
    
    def __init__(self):
        self.api_key = Config.KUCOIN_API_KEY
        self.api_secret = Config.KUCOIN_API_SECRET
        self.api_passphrase = Config.KUCOIN_PASSPHRASE
        self.session = requests.Session()
    
    def _get_headers(self, method, path, body=''):
        """ایجاد headers با امضا"""
        now = int(time.time() * 1000)
        
        message = f"{now}{method}{path}{body}"
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        return {
            'KC-API-KEY': self.api_key,
            'KC-API-SIGN': signature,
            'KC-API-TIMESTAMP': str(now),
            'KC-API-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_account_balance(self):
        """دریافت موجودی حساب"""
        try:
            method = 'GET'
            path = '/api/v1/account-overview'
            
            headers = self._get_headers(method, path)
            response = self.session.get(
                f'{self.BASE_URL}{path}',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data['code'] == '200000':
                return float(data['data']['availableBalance'])
            else:
                logger.error(f"خطا در دریافت موجودی: {data}")
                return None
        
        except Exception as e:
            logger.error(f"خطا در دریافت موجودی: {e}")
            return None
    
    def create_order(self, symbol, order_type, side, size, price=None, stop_loss=None, take_profit=None):
        """ایجاد معامله"""
        try:
            method = 'POST'
            path = '/api/v1/orders'
            
            body = {
                'symbol': f'{symbol}M',  # BTCUSDTM برای Kucoin Futures
                'type': order_type,  # market یا limit
                'side': side,  # buy یا sell
                'size': size,
                'leverage': Config.LEVERAGE
            }
            
            if order_type == 'limit' and price:
                body['price'] = price
            
            # Stop Loss و Take Profit
            if stop_loss:
                body['stop'] = 'down'
                body['stopPrice'] = stop_loss
            
            if take_profit:
                body['takeProfitPrice'] = take_profit
            
            body_str = json.dumps(body)
            headers = self._get_headers(method, path, body_str)
            
            response = self.session.post(
                f'{self.BASE_URL}{path}',
                headers=headers,
                data=body_str,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == '200000':
                order_id = data['data']['orderId']
                logger.info(f"معامله ایجاد شد: {order_id}")
                return {
                    'order_id': order_id,
                    'symbol': symbol,
                    'side': side,
                    'size': size,
                    'price': price,
                    'status': 'OPEN',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"خطا در ایجاد معامله: {data}")
                return None
        
        except Exception as e:
            logger.error(f"خطا در ایجاد معامله: {e}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """لغو معامله"""
        try:
            method = 'DELETE'
            path = f'/api/v1/orders/{order_id}'
            
            headers = self._get_headers(method, path)
            response = self.session.delete(
                f'{self.BASE_URL}{path}',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == '200000':
                logger.info(f"معامله لغو شد: {order_id}")
                return True
            else:
                logger.error(f"خطا در لغو معامله: {data}")
                return False
        
        except Exception as e:
            logger.error(f"خطا در لغو معامله: {e}")
            return False
    
    def get_open_orders(self, symbol=None):
        """دریافت معاملات باز"""
        try:
            method = 'GET'
            path = '/api/v1/orders'
            
            params = {'status': 'active'}
            if symbol:
                params['symbol'] = f'{symbol}M'
            
            headers = self._get_headers(method, path)
            response = self.session.get(
                f'{self.BASE_URL}{path}',
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == '200000':
                return data['data']['items']
            else:
                logger.error(f"خطا در دریافت معاملات باز: {data}")
                return []
        
        except Exception as e:
            logger.error(f"خطا در دریافت معاملات باز: {e}")
            return []
    
    def get_order_status(self, order_id):
        """دریافت وضعیت معامله"""
        try:
            method = 'GET'
            path = f'/api/v1/orders/{order_id}'
            
            headers = self._get_headers(method, path)
            response = self.session.get(
                f'{self.BASE_URL}{path}',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == '200000':
                order = data['data']
                return {
                    'order_id': order['id'],
                    'status': order['status'],
                    'filled_size': float(order['filledSize']),
                    'size': float(order['size']),
                    'filled_price': float(order.get('filledPrice', 0))
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"خطا در دریافت وضعیت معامله: {e}")
            return None
    
    def calculate_position_size(self, account_balance, entry_price, stop_loss_price):
        """محاسبه اندازه پوزیشن بر اساس ریسک"""
        try:
            # ریسک به دلار
            risk_amount = account_balance * (Config.RISK_PER_TRADE / 100)
            
            # تفاوت قیمت
            price_diff = abs(entry_price - stop_loss_price)
            
            if price_diff == 0:
                return 0
            
            # اندازه پوزیشن
            position_size = risk_amount / price_diff
            
            # با Leverage
            position_size = position_size / Config.LEVERAGE
            
            return round(position_size, 4)
        
        except Exception as e:
            logger.error(f"خطا در محاسبه اندازه پوزیشن: {e}")
            return 0
    
    def place_trade(self, signal, current_price):
        """قرار دادن معامله بر اساس سیگنال"""
        try:
            balance = self.get_account_balance()
            if not balance:
                logger.error("نمی‌توان موجودی را دریافت کرد")
                return None
            
            # محاسبه اندازه پوزیشن
            stop_loss = current_price * (1 - Config.STOP_LOSS_PERCENT / 100) if signal['trade_type'] == 'LONG' else current_price * (1 + Config.STOP_LOSS_PERCENT / 100)
            take_profit = current_price * (1 + Config.TAKE_PROFIT_PERCENT / 100) if signal['trade_type'] == 'LONG' else current_price * (1 - Config.TAKE_PROFIT_PERCENT / 100)
            
            size = self.calculate_position_size(balance, current_price, stop_loss)
            
            if size == 0:
                logger.warning("اندازه پوزیشن صفر است")
                return None
            
            # نوع معامله
            side = 'buy' if signal['trade_type'] == 'LONG' else 'sell'
            
            # ایجاد معامله
            order = self.create_order(
                symbol='BTCUSDT',
                order_type='market',
                side=side,
                size=size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            return order
        
        except Exception as e:
            logger.error(f"خطا در قرار دادن معامله: {e}")
            return None
