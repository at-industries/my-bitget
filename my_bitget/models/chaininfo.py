class ChainInfo:
    def __init__(
            self,
            chain: str,
            need_tag: str,
            withdrawable: str,
            rechargeable: str,
            withdraw_fee: str,
            extra_withdraw_fee: str,
            deposit_confirm: str,
            withdraw_confirm: str,
            min_deposit_amount: str,
            min_withdraw_amount: str,
            browser_url: str,
            contract_address: str,
            withdraw_step: str,
            withdraw_min_scale: str,
            congestion: str,
    ):
        self.chain = chain
        self.need_tag = need_tag
        self.withdrawable = withdrawable
        self.rechargeable = rechargeable
        self.withdraw_fee = withdraw_fee
        self.extra_withdraw_fee = extra_withdraw_fee
        self.deposit_confirm = deposit_confirm
        self.withdraw_confirm = withdraw_confirm
        self.min_deposit_amount = min_deposit_amount
        self.min_withdraw_amount = min_withdraw_amount
        self.browser_url = browser_url
        self.contract_address = contract_address
        self.withdraw_step = withdraw_step
        self.withdraw_min_scale = withdraw_min_scale
        self.congestion = congestion
