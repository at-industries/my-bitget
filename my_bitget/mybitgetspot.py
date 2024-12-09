from .data.constants import *
from .models.coininfo import *
from .models.chaininfo import *

from logging import Logger
from requests import Response
from typing import Optional, Union, Tuple

import time
import hmac
import base64
import inspect
import requests


class MyBitgetSpot:
    name = NAME_OKX
    net = NET_COM

    withdraw_native_chains_dict = {
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
            api_key: Optional[str] = None,
            secret_key: Optional[str] = None,
            passphrase: Optional[str] = None,
            proxy: Optional[str] = None,
            logger: Optional[Logger] = None,
    ):
        self._api_key = api_key
        self._api_secret = secret_key
        self._passphrase = passphrase
        self._proxy = proxy
        self._logger = logger
        self._httpClient = requests.Session()

    async def check_keys(self, ) -> Tuple[int, Union[bool, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/account/assets'
            method = 'GET'
            body = ''
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            status_code = str(response.status_code)
            json = response.json()
            if status_code == '200':
                return 0, True
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | No msg!')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_subaccount_names(self, ) -> Tuple[int, Union[list, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/user/virtual-subaccount-list'
            method = 'GET'
            body = ''
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data']
            subaccounts = []
            for subaccount in data['subAccountList']:
                subaccounts.append(int(subaccount['subAccountUid']))
            if subaccounts:
                return 0, subaccounts
            else:
                return -1, Exception(f'{log_process} | Subaccounts list is empty!')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def convert_usd_to_native(self, value: float, ticker: str) -> Tuple[int, Union[float, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.get_ticker_price(ticker=ticker)
            if status == 0:
                price: float = result
                status, result = await self.get_ticker_precision_quantity(ticker)
                if status == 0:
                    return 0, round(value / price, result)
                else:
                    return -1, Exception(f'{log_process} | {result}')
            else:
                return -1, Exception(f'{log_process} | {result}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def post_withdrawal_on_chain(self, ticker: str, chain: str, amount: float, address: str) -> Tuple[int, Union[Tuple[str, str], Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/wallet/withdrawal'
            method = 'POST'
            body = (
                f'{{'
                f'"coin":"{ticker}",'
                f'"transferType":"on_chain",'
                f'"address":"{address}",'
                f'"chain":"{chain}",'
                f'"size":"{amount}"'
                f'}}'
            )
            withdrawal_current_timestamp = self._get_time()
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            status_code = str(response.status_code)
            json = response.json()
            if status_code == '200':
                return 0, (withdrawal_current_timestamp, json['data']['orderId'])
            else:
                if 'msg' in json:
                    return -1, Exception(f'{log_process} | {json["msg"]}')
                else:
                    return -1, Exception(f'{log_process} | No msg!')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def check_withdrawal(self, time_start: str, order_id: str) -> Tuple[int, Union[bool, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/wallet/withdrawal-records'
            method = 'GET'
            body = f'?startTime={time_start}&endTime={self._get_time()}&orderId={order_id}'
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data'][0]
            status = data['status']
            if status == 'success':
                return 0, True
            elif status == 'pending':
                return 0, False
            else:
                return -1, Exception(f'{log_process} | Wrong status!')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_subaccount_balance(self, currency: str, subaccount_name: str) -> Tuple[int, Union[float, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/account/subaccount-assets'
            method = 'GET'
            body = ''
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data']
            subaccount_balance = 0.0
            for subacc_dict in data:
                if str(subacc_dict['userId']) == str(int(subaccount_name)):
                    for asset_dict in subacc_dict['assetsList']:
                        if asset_dict['coin'] == currency:
                            subaccount_balance = float(asset_dict['available'])
                            break
                    break
            return 0, subaccount_balance
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def transfer_from_subacc_to_main(self, subaccount_name: str, currency: str, amount: float) -> Tuple[int, Union[str, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.get_main_uid()
            if status == 0:
                endpoint = '/api/v2/spot/wallet/subaccount-transfer'
                method = 'POST'
                body = (
                    f'{{'
                    f'"fromType":"spot",'
                    f'"toType":"spot",'
                    f'"amount":"{amount}",'
                    f'"coin":"{currency}",'
                    f'"fromUserId":"{int(subaccount_name)}",'
                    f'"toUserId":"{result}"'
                    f'}}'
                )
                response = self._http_request(endpoint, method, body)
                self._log_debug(f'RESPONSE: {response.json()}')
                status_code = str(response.status_code)
                json = response.json()
                if status_code == '200':
                    return 0, json['data']['transferId']
                else:
                    if 'msg' in json:
                        return -1, Exception(f'{log_process} | {json["msg"]}')
                    else:
                        return -1, Exception(f'{log_process} | No msg!')
            else:
                return -1, Exception(f'{log_process} | {result}!')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_balance(self, currency: str) -> Tuple[int, Union[float, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/account/assets'
            method = 'GET'
            body = f'?coin={currency}'
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data'][0]
            balance = data['available']
            return 0, float(balance)
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_ticker_price(self, ticker: str) -> Tuple[int, Union[float, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/market/tickers'
            method = 'GET'
            body = f'?symbol={ticker}USDT'
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data'][0]
            return 0, float(data['lastPr'])
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_ticker_precision_quantity(self, ticker: str) -> Tuple[int, Union[int, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/public/symbols'
            method = 'GET'
            body = f'?symbol={ticker}USDT'
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data'][0]
            return 0, int(data['quantityPrecision'])
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_main_uid(self, ) -> Tuple[int, Union[str, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/account/info'
            method = 'GET'
            body = ''
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            uid = response.json()['data']['userId']
            return 0, str(uid)
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_coin_info(self, ticker: str) -> Tuple[int, Union[CoinInfo, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            endpoint = '/api/v2/spot/public/coins'
            method = 'GET'
            body = f'?coin={ticker}'
            response = self._http_request(endpoint, method, body)
            self._log_debug(f'RESPONSE: {response.json()}')
            data = response.json()['data'][0]
            coin_info = CoinInfo(
                coin_id=data['coinId'],
                coin=data['coin'],
                transfer=data['transfer'],
                chains=[],
            )
            for chain in data['chains']:
                chain_info = ChainInfo(
                    chain=chain['chain'],
                    need_tag=chain['needTag'],
                    withdrawable=chain['withdrawable'],
                    rechargeable=chain['rechargeable'],
                    withdraw_fee=chain['withdrawFee'],
                    extra_withdraw_fee=chain['extraWithdrawFee'],
                    deposit_confirm=chain['depositConfirm'],
                    withdraw_confirm=chain['withdrawConfirm'],
                    min_deposit_amount=chain['minDepositAmount'],
                    min_withdraw_amount=chain['minWithdrawAmount'],
                    browser_url=chain['browserUrl'],
                    contract_address=chain['contractAddress'],
                    withdraw_step=chain['withdrawStep'],
                    withdraw_min_scale=chain['withdrawMinScale'],
                    congestion=chain['congestion'],
                )
                coin_info.chains.append(chain_info)
            return 0, coin_info
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    async def get_chain_info(self, ticker: str, chain: str) -> Tuple[int, Union[ChainInfo, Exception]]:
        log_process = f'{inspect.currentframe().f_code.co_name}'
        try:
            status, result = await self.get_coin_info(ticker=ticker)
            if status == 0:
                coin_info: CoinInfo = result
                for chain_info in coin_info.chains:
                    if chain_info.chain == chain:
                        return 0, chain_info
                return -1, Exception(f'{log_process} | No such a chain!')
            else:
                return -1, Exception(f'{log_process} | {result}')
        except Exception as e:
            return -1, Exception(f'{log_process} | {e}')

    @staticmethod
    def _get_time() -> str:
        return str(int(time.time() * 1000))

    def _get_proxies(self, ) -> Union[dict, None]:
        if self._proxy is not None:
            return {
                'http': f'http://{self._proxy}',
                'https': f'http://{self._proxy}',
            }
        else:
            return None

    def _get_signature(self, timestamp: str, method: str, endpoint: str, body: Union[str, dict]) -> str:
        return self._generate_signature(timestamp, method, endpoint, body)

    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: Union[str, dict]) -> str:
        message = str(timestamp) + str.upper(method) + endpoint + str(body)
        mac = hmac.new(bytes(self._api_secret, encoding='utf-8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        signature = str(base64.b64encode(mac.digest()), 'utf8')
        return signature

    def _http_request(self, endpoint: str, method: str, body: Union[str, dict]) -> Response:
        url = (self.net + endpoint)
        timestamp = self._get_time()
        proxies = self._get_proxies()
        signature = self._get_signature(timestamp, method, endpoint, body)
        headers = {
            'ACCESS-KEY': self._api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-PASSPHRASE': self._passphrase,
            'ACCESS-TIMESTAMP': timestamp,
            'locale': 'en-US',
            'Content-Type': 'application/json',
        }
        if method == 'POST':
            return self._httpClient.post(url=url, headers=headers, data=body, proxies=proxies)
        else:
            return self._httpClient.request(method=method, url=(url + body), headers=headers, proxies=proxies)

    def _log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(f'{self.name} | {message}')
