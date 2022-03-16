class Evm:
    def __init__(self, reef):
        self.reef = reef

    def get_evm_address(self, substrate_address):
        address = self.reef.query(
            "EvmAccounts",
            "EvmAddresses",
            [substrate_address],
        )

        return address.value

    def is_address_claimed(self, substrate_address):
        return self.get_evm_address(substrate_address) != None
