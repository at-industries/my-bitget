from logging import Logger
from typing import Optional, Union, Tuple
from httpx import Client, AsyncClient, Response

import hmac
import time
import json
import httpx
import base64
import inspect

from .utils import afh


class MyBitget:
    name = 'Bitget'
    host = 'https://api.bitget.com'

    withdraw_native_chains = {
        'Arbitrum': 'ArbitrumOne',
        'Avalanche': 'C-Chain',
        'Base': 'BASE',
        'BSC': 'BEP20',
        'Fantom': 'Fantom',
        'Optimism': 'Optimism',
        'Polygon': 'Polygon',
        'zkSync': 'zkSyncEra',
    }

    def __init__(
            self,
            api_key: str,
            secret_key: str,
            passphrase: str,
            proxy: Optional[str] = None,
            logger: Optional[Logger] = None,
            asynchrony: Optional[bool] = False,
    ):
        """
        MyBitget is a convenient library for interacting with Bitget API.
        For more details about Bitget API, refer to the Bitget Documentation: https://www.bitget.com/api-doc/common/intro

        Almost all class methods (except utility functions) return tuples, with an integer status as the first element:
        - `0`: Success status (indicates the method completed successfully; the second element in the tuple contains the result)
        - `-1`: Error status (indicates the method failed; the second element in the tuple contains an error message)

        :param api_key: API Key (generated on the Bitget website).
        :param secret_key: Secret Key (generated on the Bitget website).
        :param passphrase: Passphrase (created by the user during API key generation on Bitget).
        :param proxy: HTTP/HTTPS proxy (e.g., user12345:abcdef@12.345.67.890:1234).
        :param logger: Logger object (used to log received responses).
        :param asynchrony: Enables asynchronous operations.
        """
        self._api_key = api_key
        self._secret_key = secret_key
        self._passphrase = passphrase
        self._proxy = proxy
        self._logger = logger
        self._asynchrony = asynchrony
        self._httpx_client = self._get_httpx_client()

    async def PUBLIC_get_coin_info(self, ticker: str) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets information about all coin chains (e.g., contract_address, withdraw_fee, min_withdraw_amount) by its ticker (e.g., BTC, ETH).
        Endpoint: https://www.bitget.com/api-doc/spot/market/Get-Coin-List
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/public/coins'
            method = f'GET'
            body = f'?coin={ticker}'
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                return 0, dict(json)
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def PUBLIC_get_chain_info(self, ticker: str, chain: str) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets information about specific coin's chain (e.g., contract_address, withdraw_fee, min_withdraw_amount)
        by its ticker (e.g., BTC, ETH) and chain name (e.g., ArbitrumOne, BEP20).
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.PUBLIC_get_coin_info(ticker=ticker)
            if status == 0:
                for chain_info in result['data'][0]['chains']:
                    if str(chain_info['chain']) == chain:
                        return 0, dict(chain_info)
                return -1, Exception(f'{log_process} | No such a chain!')
            else:
                return -1, Exception(f'{log_process} | {result}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def PUBLIC_get_symbol_info(self, ticker: str) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets common information about coin USDT pair trading on spot market (e.g., min_trade_amount, price_precision, min_trade_usdt).
        Endpoint: https://www.bitget.com/api-doc/spot/market/Get-Symbols
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/public/symbols'
            method = f'GET'
            body = f'?symbol={ticker}USDT'
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                return 0, dict(json)
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def PUBLIC_get_ticker_info(self, ticker: str) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets market information about coin USDT pair trading on spot market (e.g., open_price, quote_volume, change_24h).
        Endpoint: https://www.bitget.com/api-doc/spot/market/Get-Tickers
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/market/tickers'
            method = f'GET'
            body = f'?symbol={ticker}USDT'
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                return 0, dict(json)
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def PUBLIC_get_price(self, ticker: str) -> Tuple[int, Union[float, Exception]]:
        """Gets the price (in USDT) of a specific coin by its ticker (e.g., BTC, ETH)"""
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.PUBLIC_get_ticker_info(ticker=ticker)
            if status == 0:
                return 0, float(result['data'][0]['lastPr'])
            else:
                return -1, Exception(f'{log_process} | {result}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SPOT_is_connected(self, ) -> Tuple[int, Union[bool, Exception]]:
        """
        Checks the connection to the spot account.
        Endpoint: https://www.bitget.com/api-doc/spot/account/Get-Account-Assets
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/account/assets'
            method = f'GET'
            body = f''
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            if response.status_code == 200:
                return 0, True
            else:
                json = response.json()
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SPOT_get_account_info(self, ) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets common information about main account (e.g., user_id, ips, regis_time).
        Endpoint: https://www.bitget.com/api-doc/spot/account/Get-Account-Info
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/account/info'
            method = f'GET'
            body = ''
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                return 0, dict(json)
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SPOT_get_balance(self, ticker: Optional[str] = None) -> Tuple[int, Union[dict, Exception]]:
        """
        Gets the balance for a specific coin (or for all coins).
        Endpoint: https://www.bitget.com/api-doc/spot/account/Get-Account-Assets
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/account/assets'
            method = f'GET'
            body = f'' if (ticker is None) else f'?coin={ticker}'
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                return 0, dict(json)
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SPOT_convert_usd_to_native(self, amount: float, ticker: str, chain: str) -> Tuple[int, Union[float, Exception]]:
        """
        Converts USD amount to the native chain coin amount, rounded to the chain's tick_size value
        (e.g., 100 USD converts to 0.02857143 ETH for an ETH price of 3500 USD).
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.PUBLIC_get_price(ticker=ticker)
            if status == 0:
                price: float = result
                status, result = await self.PUBLIC_get_chain_info(ticker=ticker, chain=chain)
                if status == 0:
                    precision = int(result['withdrawMinScale'])
                    return 0, round(amount / price, precision)
                else:
                    return -1, Exception(f'{log_process} | {result}')
            else:
                return -1, Exception(f'{log_process} | {result}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SPOT_post_withdrawal(self, ticker: str, chain: str, address: str, amount: float) -> Tuple[int, Union[Tuple[str, str], Exception]]:
        """
        Posts a withdrawal on the chain for a specific ticker and chain (withdrawals must be available for created API keys).
        Endpoint: https://www.bitget.com/api-doc/spot/account/Wallet-Withdrawal
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/wallet/withdrawal'
            method = f'POST'
            body = {
                'coin': ticker,
                'transferType': 'on_chain',
                'address': address,
                'chain': chain,
                'size': amount,
            }
            withdrawal_timestamp = self.time
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                return 0, (withdrawal_timestamp, json['data']['orderId'])
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SPOT_check_withdrawal(self, time_start: str, order_id: str) -> Tuple[int, Union[bool, Exception]]:
        """
        Checks if the withdrawal is completed by its withdrawal_id (the withdrawal_id is returned after posting the withdrawal on the chain).
        Endpoint: https://www.bitget.com/api-doc/spot/account/Get-Withdraw-Record
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/wallet/withdrawal-records'
            method = f'GET'
            body = f'?startTime={time_start}&endTime={self.time}&orderId={order_id}'
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                status = json['data'][0]['status']
                if status in ['success']:
                    return 0, True
                elif status in ['pending']:
                    return 0, False
                else:
                    return -1, Exception(f'{log_process} | Wrong status!')
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SUBACCOUNT_get_subaccounts(self, ) -> Tuple[int, Union[list, Exception]]:
        """
        Gets the names of all subaccounts created under the main Bitget account.
        Endpoint: https://www.bitget.com/api-doc/common/vsubaccount/Get-Virtual-Subaccount-List
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/user/virtual-subaccount-list'
            method = f'GET'
            body = f''
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                subaccounts = []
                for subaccount in json['data']['subAccountList']:
                    subaccounts.append(subaccount['subAccountUid'])
                if subaccounts:
                    return 0, subaccounts
                else:
                    return -1, Exception(f'{log_process} | Empty subaccounts list!')
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SUBACCOUNT_get_balance(self, subaccount_name: str, ticker: Optional[str] = None) -> Tuple[int, Union[list, Exception]]:
        """
        Gets the balance for a specific coin (or for all coins) in a specific subaccount.
        Endpoint: https://www.bitget.com/api-doc/spot/account/Get-Subaccount-Assets
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = f'/api/v2/spot/account/subaccount-assets'
            method = f'GET'
            body = f''
            response = await self._httpx_request(
                endpoint=endpoint,
                method=method,
                body=body,
            )
            json = response.json()
            if response.status_code == 200:
                for subaccount in json['data']:
                    if str(subaccount['userId']) == subaccount_name:
                        assets: list = subaccount['assetsList']
                        if ticker is None:
                            return 0, assets
                        else:
                            for asset in assets:
                                if asset['coin'] == ticker:
                                    return 0, [asset]
                return -1, Exception(f'{log_process} | No such data in response!')
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | {json}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def SUBACCOUNT_transfer_to_main(self, subaccount_name: str, ticker: str, amount: float) -> Tuple[int, Union[str, Exception]]:
        """
        Transfers coins from a subaccount to the main account for a specific coin from a specific subaccount.
        Endpoint: https://www.bitget.com/api-doc/spot/account/Sub-Transfer
        """
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.SPOT_get_account_info()
            if status == 0:
                endpoint = f'/api/v2/spot/wallet/subaccount-transfer'
                method = f'POST'
                body = {
                    'fromType': 'spot',
                    'toType': 'spot',
                    'amount': amount,
                    'coin': ticker,
                    'fromUserId': int(subaccount_name),
                    'toUserId': result['data']['userId'],
                }
                response = await self._httpx_request(
                    endpoint=endpoint,
                    method=method,
                    body=body,
                )
                json = response.json()
                if response.status_code == 200:
                    return 0, json['data']['transferId']
                else:
                    if 'msg' in json:
                        return -1, Exception(f'{log_process} | {json["msg"]}')
                    else:
                        return -1, Exception(f'{log_process} | {json}')
            else:
                return -1, Exception(f'{log_process} | {result}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    def _get_httpx_client(self, ) -> Union[Client, AsyncClient]:
        if self._asynchrony:
            httpx_client = httpx.AsyncClient(proxy=self.proxy)
        else:
            httpx_client = httpx.Client(proxy=self.proxy)
        return httpx_client

    async def _httpx_request(self, method: str, endpoint: str, body: Union[str, dict]) -> Response:
        timestamp = self.time
        signature = self._get_signature(timestamp, method, endpoint, body)
        headers = {
            'ACCESS-KEY': self._api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-PASSPHRASE': self._passphrase,
            'ACCESS-TIMESTAMP': timestamp,
            'locale': 'en-US',
            'Content-Type': 'application/json',
        }
        if isinstance(body, str):
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint + body), headers=headers,
            )
        else:
            response = await afh(
                self._httpx_client.request, self._asynchrony,
                method=method, url=(self.host + endpoint), headers=headers, json=body,
            )
        self._log_debug(response.json())
        return response

    def _get_signature(self, timestamp: str, method: str, endpoint: str, body: Union[str, dict]) -> str:
        message = str(timestamp) + str.upper(method) + endpoint + (json.dumps(body, separators=(',', ':')) if isinstance(body, dict) else body)
        mac = hmac.new(bytes(self._secret_key, encoding='utf-8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        signature = str(base64.b64encode(mac.digest()), 'utf8')
        return signature

    def _log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(f'{self.name} | {message}')

    @property
    def time(self, ) -> str:
        return str(int(time.time() * 1000))

    @property
    def proxy(self, ) -> Optional[str]:
        return f'http://{self._proxy}' if self._proxy else None
