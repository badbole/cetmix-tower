from odoo.exceptions import AccessError

from . import common


class TestTowerVariableValue(common.TestTowerCommon):
    """Testing variable values."""

    def setUp(self):
        super().setUp()

        # Create additional test users
        self.user2 = self.Users.create(
            {
                "name": "Test User 2",
                "login": "test_user2",
                "email": "test_user2@example.com",
                "groups_id": [(6, 0, [self.group_user.id])],
            }
        )

        self.manager2 = self.Users.create(
            {
                "name": "Test Manager 2",
                "login": "test_manager2",
                "email": "test_manager2@example.com",
                "groups_id": [(6, 0, [self.group_manager.id])],
            }
        )

        # Create variables with different access levels
        self.variable_level_1 = self.Variable.create(
            {
                "name": "Level 1 Variable",
                "access_level": "1",
            }
        )

        self.variable_level_2 = self.Variable.create(
            {
                "name": "Level 2 Variable",
                "access_level": "2",
            }
        )

        # Create servers
        self.server_1 = self.Server.create(
            {
                "name": "Test Server 1",
                "ip_v4_address": "localhost",
                "ssh_username": "admin",
                "ssh_password": "password",
                "os_id": self.os_debian_10.id,
                "user_ids": [(4, self.user.id)],
                "manager_ids": [(4, self.manager.id)],
            }
        )

        self.server_2 = self.Server.create(
            {
                "name": "Test Server 2",
                "ip_v4_address": "localhost",
                "ssh_username": "admin",
                "ssh_password": "password",
                "os_id": self.os_debian_10.id,
                "user_ids": [(4, self.user2.id)],
                "manager_ids": [(4, self.manager2.id)],
            }
        )

        # Create test command
        self.test_command = self.Command.create(
            {
                "name": "Test Command",
                "code": "echo 'test'",
            }
        )

        # Create flight plan and its components
        self.test_plan = self.Plan.create(
            {
                "name": "Test Plan",
                "user_ids": [(4, self.user.id)],
                "manager_ids": [(4, self.manager.id)],
            }
        )

        self.test_plan_line = self.plan_line.create(
            {
                "name": "Test Line",
                "plan_id": self.test_plan.id,
                "command_id": self.test_command.id,
            }
        )

        self.test_plan_line_action = self.plan_line_action.create(
            {
                "name": "Test Action",
                "line_id": self.test_plan_line.id,
                "condition": "==",
                "value_char": "0",
                "action": "n",
            }
        )

        # Create variable values
        self.global_value_1 = self.VariableValue.create(
            {
                "variable_id": self.variable_level_1.id,
                "value_char": "global_value_1",
            }
        )

        self.global_value_2 = self.VariableValue.create(
            {
                "variable_id": self.variable_level_2.id,
                "value_char": "global_value_2",
            }
        )

        self.server_value_1 = self.VariableValue.create(
            {
                "variable_id": self.variable_level_1.id,
                "value_char": "server_value_1",
                "server_id": self.server_1.id,
            }
        )

        self.server_value_2 = self.VariableValue.create(
            {
                "variable_id": self.variable_level_2.id,
                "value_char": "server_value_2",
                "server_id": self.server_1.id,
            }
        )

        self.plan_value_1 = self.VariableValue.create(
            {
                "variable_id": self.variable_level_1.id,
                "value_char": "plan_value_1",
                "plan_line_action_id": self.test_plan_line_action.id,
            }
        )

        self.plan_value_2 = self.VariableValue.create(
            {
                "variable_id": self.variable_level_2.id,
                "value_char": "plan_value_2",
                "plan_line_action_id": self.test_plan_line_action.id,
            }
        )

    def test_variable_value_access_rights(self):
        """
        Test access rights for variable values
        based on access levels and user roles.
        """

        # Test User Access
        # ---------------
        user_values = self.VariableValue.with_user(self.user).search(
            [
                (
                    "id",
                    "in",
                    [
                        self.global_value_1.id,
                        self.global_value_2.id,
                        self.server_value_1.id,
                        self.server_value_2.id,
                        self.plan_value_1.id,
                        self.plan_value_2.id,
                    ],
                )
            ]
        )

        # User should see level 1 global values and level 1 values
        #  from their server/plan
        self.assertEqual(len(user_values), 3)
        self.assertIn(self.global_value_1.id, user_values.ids)
        self.assertIn(self.server_value_1.id, user_values.ids)
        self.assertIn(self.plan_value_1.id, user_values.ids)

        # User should not be able to create/write/unlink values
        with self.assertRaises(AccessError):
            self.VariableValue.with_user(self.user).create(
                {
                    "variable_id": self.variable_level_1.id,
                    "value_char": "test",
                    "server_id": self.server_1.id,
                }
            )

        with self.assertRaises(AccessError):
            self.server_value_1.with_user(self.user).write({"value_char": "new_value"})

        with self.assertRaises(AccessError):
            self.server_value_1.with_user(self.user).unlink()

        # Test Manager Access
        # ------------------
        manager_values = self.VariableValue.with_user(self.manager).search(
            [
                (
                    "id",
                    "in",
                    [
                        self.global_value_1.id,
                        self.global_value_2.id,
                        self.server_value_1.id,
                        self.server_value_2.id,
                        self.plan_value_1.id,
                        self.plan_value_2.id,
                    ],
                )
            ]
        )

        # Manager should see all level 1 and 2 values from their server/plan
        self.assertEqual(len(manager_values), 6)

        # Manager should be able to create values for their server/plan
        test_variable = self.Variable.create(
            {
                "name": "Test Variable",
                "access_level": "2",
            }
        )
        try:
            new_value = self.VariableValue.with_user(self.manager).create(
                {
                    "variable_id": test_variable.id,
                    "value_char": "manager_value",
                    "server_id": self.server_1.id,
                }
            )
        except AccessError:
            self.fail("Manager should be able to create values for their server")

        # Manager should be able to modify values for their server/plan
        try:
            self.server_value_2.with_user(self.manager).write(
                {"value_char": "updated_value"}
            )
        except AccessError:
            self.fail("Manager should be able to modify values for their server")

        # Manager should be able to delete their own values
        try:
            new_value.with_user(self.manager).unlink()
        except AccessError:
            self.fail("Manager should be able to delete their own values")

        # Manager should not be able to modify other manager's values
        with self.assertRaises(AccessError):
            self.VariableValue.with_user(self.manager).create(
                {
                    "variable_id": self.variable_level_1.id,
                    "value_char": "test",
                    "server_id": self.server_2.id,
                }
            )

        # Test Root Access
        # ---------------
        root_values = self.VariableValue.with_user(self.root).search(
            [
                (
                    "id",
                    "in",
                    [
                        self.global_value_1.id,
                        self.global_value_2.id,
                        self.server_value_1.id,
                        self.server_value_2.id,
                        self.plan_value_1.id,
                        self.plan_value_2.id,
                    ],
                )
            ]
        )

        # Root should see all values
        self.assertEqual(len(root_values), 6)

        # Root should be able to create any value
        try:
            root_value = self.VariableValue.with_user(self.root).create(
                {
                    "variable_id": self.variable_level_2.id,
                    "value_char": "root_value",
                    "server_id": self.server_2.id,
                    "access_level": "2",
                }
            )
        except AccessError:
            self.fail("Root should be able to create any value")

        # Root should be able to modify any value
        try:
            self.server_value_2.with_user(self.root).write(
                {"value_char": "root_updated"}
            )
        except AccessError:
            self.fail("Root should be able to modify any value")

        # Root should be able to delete any value
        try:
            root_value.with_user(self.root).unlink()
        except AccessError:
            self.fail("Root should be able to delete any value")
