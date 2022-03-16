# Python Substrate Interface Library
#
# Copyright 2021 Reef Finance.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest

from scalecodec import ScaleBytes
from reefinterface import (
    ReefInterface,
    Keypair,
)
from reefinterface.contracts import ContractEvent
from reefinterface.exceptions import ContractMetadataParseException
from reefinterface.utils.ss58 import ss58_encode
from test import settings


class EvmAddressClaimTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reef = ReefInterface(url="ws://127.0.0.1:9944")
        cls.evm = cls.reef.evm

    def test_is_not_claimed_address(self):
        keypair = Keypair.create_from_uri("//Alice")
        self.assertFalse(self.evm.is_address_claimed(keypair.ss58_address))


if __name__ == "__main__":
    unittest.main()
