__copyright__ = "Copyright (c) 2024-2025 Alex Laird"
__license__ = "MIT"

import json
import os

from bs4 import BeautifulSoup

from amazonorders.entity.order import Order
from amazonorders.entity.parsable import Parsable
from tests.unittestcase import UnitTestCase


class TestItem(UnitTestCase):
    def test_to_currency(self):
        # GIVEN
        html = "<html />"
        parsed = BeautifulSoup(html, self.test_config.bs4_parser)

        # WHEN
        parsable = Parsable(parsed, self.test_config)

        # THEN
        self.assertIsNone(parsable.to_currency(None))
        self.assertIsNone(parsable.to_currency(""))
        self.assertEqual(parsable.to_currency(1234.99), 1234.99)
        self.assertEqual(parsable.to_currency(1234), 1234)
        self.assertEqual(parsable.to_currency("1,234.99"), 1234.99)
        self.assertEqual(parsable.to_currency("$1,234.99"), 1234.99)
        self.assertIsNone(parsable.to_currency("not currency"))

    def test_to_dict_excludes_parsed_and_config(self):
        # GIVEN
        html = "<div>test</div>"
        parsed = BeautifulSoup(html, self.test_config.bs4_parser)
        parsable = Parsable(parsed, self.test_config)

        # WHEN
        result = parsable.to_dict()

        # THEN
        self.assertNotIn("parsed", result)
        self.assertNotIn("config", result)

    def test_to_dict_includes_all_public_attrs(self):
        # GIVEN
        with open(os.path.join(self.RESOURCES_DIR, "orders", "order-details-112-5939971-8962610.html"),
                  "r", encoding="utf-8") as f:
            parsed = BeautifulSoup(f.read(), self.test_config.bs4_parser)
        order = Order(parsed, self.test_config, full_details=True)

        # WHEN
        result = order.to_dict()

        # THEN
        public_attrs = {k for k in order.__dict__ if k not in ("parsed", "config")}
        self.assertEqual(set(result.keys()), public_attrs)

    def test_to_dict_converts_nested_parsables_to_dicts(self):
        # GIVEN
        with open(os.path.join(self.RESOURCES_DIR, "orders", "order-details-112-5939971-8962610.html"),
                  "r", encoding="utf-8") as f:
            parsed = BeautifulSoup(f.read(), self.test_config.bs4_parser)
        order = Order(parsed, self.test_config, full_details=True)

        # WHEN
        result = order.to_dict()

        # THEN
        self.assertIsInstance(result["items"][0], dict)
        self.assertIsInstance(result["recipient"], dict)

    def test_to_json_produces_valid_json(self):
        # GIVEN
        with open(os.path.join(self.RESOURCES_DIR, "orders", "order-details-112-5939971-8962610.html"),
                  "r", encoding="utf-8") as f:
            parsed = BeautifulSoup(f.read(), self.test_config.bs4_parser)
        order = Order(parsed, self.test_config, full_details=True)

        # WHEN
        json_str = order.to_json()

        # THEN
        data = json.loads(json_str)
        self.assertEqual(data["order_number"], order.order_number)
        self.assertIsInstance(data["order_placed_date"], str)
