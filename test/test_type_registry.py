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

from scalecodec.base import ScaleBytes

from reefinterface import SubstrateInterface, ReefInterface
from test import settings


class ReefTypeRegistryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reef = ReefInterface(
            url=settings.REEF_NODE_URL,
        )

    @classmethod
    def tearDownClass(cls):
        cls.reef.close()

    # def test_type_registry_compatibility(self):

    # for scale_type in self.reef.get_type_registry():

    # obj = self.reef.runtime_config.get_decoder_class(scale_type)

    # self.assertIsNotNone(obj, "{} not supported".format(scale_type))


class ReloadTypeRegistryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.reef = SubstrateInterface(
            url="dummy", ss58_format=42, type_registry_preset="test"
        )

    def test_initial_correct_type_local(self):
        decoding_class = self.reef.runtime_config.type_registry["types"]["blocknumber"]
        self.assertEqual(
            self.reef.runtime_config.get_decoder_class("u64"), decoding_class
        )

    def test_reloading_use_remote_preset(self):

        # Intentionally overwrite type in local preset
        u32_cls = self.reef.runtime_config.get_decoder_class("u32")
        u64_cls = self.reef.runtime_config.get_decoder_class("u64")

        self.reef.runtime_config.type_registry["types"]["blocknumber"] = u32_cls

        self.assertEqual(
            u32_cls, self.reef.runtime_config.get_decoder_class("BlockNumber")
        )

        # Reload type registry
        self.reef.reload_type_registry()

        self.assertEqual(
            u64_cls, self.reef.runtime_config.get_decoder_class("BlockNumber")
        )

    def test_reloading_use_local_preset(self):

        # Intentionally overwrite type in local preset
        u32_cls = self.reef.runtime_config.get_decoder_class("u32")
        u64_cls = self.reef.runtime_config.get_decoder_class("u64")

        self.reef.runtime_config.type_registry["types"]["blocknumber"] = u32_cls

        self.assertEqual(
            u32_cls, self.reef.runtime_config.get_decoder_class("BlockNumber")
        )

        # Reload type registry
        self.reef.reload_type_registry(use_remote_preset=False)

        self.assertEqual(
            u64_cls, self.reef.runtime_config.get_decoder_class("BlockNumber")
        )


if __name__ == "__main__":
    unittest.main()
