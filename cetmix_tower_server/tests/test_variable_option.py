from odoo.exceptions import ValidationError

from .common import TestTowerCommon


class TestTowerVariableOption(TestTowerCommon):
    """Test case class to validate the behavior of
    'cx.tower.variable.option' model.
    """

    def setUp(self):
        super().setUp()

        self.variable_odoo_versions = self.Variable.create(
            {
                "name": "odoo_versions",
                "variable_type": "o",
            }
        )

        self.variable_option_17_0 = self.VariableOption.create(
            {
                "name": "17.0",
                "value_char": "17.0",
                "variable_id": self.variable_odoo_versions.id,
            }
        )

        self.variable_option_18_0 = self.VariableOption.create(
            {
                "name": "18.0",
                "value_char": "18.0",
                "variable_id": self.variable_odoo_versions.id,
            }
        )

    def test_variable_value_set_from_option(self):
        """Test that a variable value can be set from an option."""

        variable_value = self.VariableValue.create(
            {
                "server_id": self.server_test_1.id,
                "variable_id": self.variable_odoo_versions.id,
            }
        )

        # -- 1 --
        # Set value_char to an existing option
        variable_value.value_char = "17.0"
        self.assertEqual(
            variable_value.option_id,
            self.variable_option_17_0,
        )

        # -- 2 --
        # Set value_char to a non-existing option
        with self.assertRaises(ValidationError):
            variable_value.value_char = "29.0"

    def test_access_level_consistency(self):
        """Test that variable option access level cannot be lower
        than variable access level."""

        # Create a variable with access level "2"
        variable_restricted = self.Variable.create(
            {
                "name": "restricted_variable",
                "variable_type": "o",
                "access_level": "2",
            }
        )

        # Should succeed: option with same access level as variable
        try:
            self.VariableOption.create(
                {
                    "name": "Option 1",
                    "value_char": "value1",
                    "variable_id": variable_restricted.id,
                    "access_level": "2",
                }
            )
        except ValidationError:
            self.fail("Should allow creating option with same access level as variable")

        # Should succeed: option with higher access level than variable
        try:
            self.VariableOption.create(
                {
                    "name": "Option 2",
                    "value_char": "value2",
                    "variable_id": variable_restricted.id,
                    "access_level": "3",
                }
            )
        except ValidationError:
            self.fail(
                "Should allow creating option with higher access level than variable"
            )

        # Should fail: option with lower access level than variable
        with self.assertRaises(
            ValidationError,
            msg="Should not allow creating option "
            "with lower access level than variable",
        ):
            self.VariableOption.create(
                {
                    "name": "Option 3",
                    "value_char": "value3",
                    "variable_id": variable_restricted.id,
                    "access_level": "1",
                }
            )

        # Test updating existing option's access level
        option = self.VariableOption.create(
            {
                "name": "Option 4",
                "value_char": "value4",
                "variable_id": variable_restricted.id,
                "access_level": "2",
            }
        )

        # Should fail: updating to lower access level than variable
        with self.assertRaises(
            ValidationError,
            msg="Should not allow updating option to lower access level than variable",
        ):
            option.write({"access_level": "1"})

        # Should succeed: updating to higher access level than variable
        try:
            option.write({"access_level": "3"})
        except ValidationError:
            self.fail(
                "Should allow updating option to higher access level than variable"
            )
