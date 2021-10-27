# Python Substrate Interface Library
#
# Copyright 2018-2020 Stichting Polkascan (Polkascan Foundation).
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

import unittest

from reefinterface import ReefInterface, SubstrateInterface
from test import settings


class TestInit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reef = ReefInterface(url="mainnet")

    @classmethod
    def tearDownClass(cls):
        cls.reef.close()

    def test_chain(self):
        self.assertEqual("Reef Mainnet", self.reef.chain)

    def test_properties(self):
        self.assertDictEqual(
            {"ss58format": 42, "tokenDecimals": 18, "tokenSymbol": "REEF"},
            self.reef.properties,
        )

    def test_ss58_format(self):
        self.assertEqual(42, self.reef.ss58_format)

    def test_token_symbol(self):
        self.assertEqual("REEF", self.reef.token_symbol)

    def test_token_decimals(self):
        self.assertEqual(18, self.reef.token_decimals)

    def test_is_valid_ss58_address(self):
        self.assertTrue(
            self.reef.is_valid_ss58_address(
                "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
            )
        )
        self.assertFalse(
            self.reef.is_valid_ss58_address(
                "12gX42C4Fj1wgtfgoP624zeHrcPBqzhb4yAENyvFdGX6EUnN"
            )
        )

    def test_lru_cache_not_shared(self):
        block_number2 = self.reef.get_block_number(
            "0xa4d873095aeae6fc1f3953f0a0085ee216bf8629342aaa92bd53f841e1052e1c"
        )

        self.assertIsNone(block_number2)

    def test_context_manager(self):
        with ReefInterface(url="mainnet") as reef:
            self.assertTrue(reef.websocket.connected)
            self.assertEqual(42, reef.ss58_format)

        self.assertFalse(reef.websocket.connected)


if __name__ == "__main__":
    unittest.main()
