from .chaininfo import ChainInfo


class CoinInfo:
    def __init__(
            self,
            coin_id: str,
            coin: str,
            transfer: str,
            chains: list[ChainInfo],
    ):
        self.coin_id = coin_id
        self.coin = coin
        self.transfer = transfer
        self.chains = chains
