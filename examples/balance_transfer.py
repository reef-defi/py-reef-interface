from reefinterface import Keypair, ReefInterface
from reefinterface.exceptions import SubstrateRequestException

try:
    reef = ReefInterface(url="testnet")
except ConnectionRefusedError:
    print("Reef node could not be reached")
    exit()

# Test account
keypair = Keypair.create_from_uri("//Alice")

# From mnemonic
# keypair = Keypair.create_from_mnemonic(
# "12 words mnemonic"
# )

call = reef.compose_call(
    call_module="Balances",
    call_function="transfer",
    call_params={
        "dest": "5E9wUiZwxSSjL6phrr7tc6UznqPRg2cbeWTE4WUUrprP738t",
        "value": 1 * 10 ** 18,
    },
)

# Get payment info
payment_info = reef.get_payment_info(call=call, keypair=keypair)

print("Payment info: ", payment_info)

extrinsic = reef.create_signed_extrinsic(call=call, keypair=keypair, era={"period": 64})


try:
    receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)

    print(
        'Extrinsic "{}" included in block "{}"'.format(
            receipt.extrinsic_hash, receipt.block_hash
        )
    )

    if receipt.is_success:
        print("✅ Success, triggered events:")
        for event in receipt.triggered_events:
            print(f"* {event.value}")

    else:
        print("⚠️ Extrinsic Failed: ", receipt.error_message)


except SubstrateRequestException as e:
    print("Failed to send: {}".format(e))
