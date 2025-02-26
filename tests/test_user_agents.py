import unittest
from user_agent_manager import UserAgentManager

class TestUserAgentManager(unittest.TestCase):

    def setUp(self):
        self.ua_manager = UserAgentManager()

    def test_load_user_agents(self):
        self.assertIsInstance(self.ua_manager.user_agents, list)

    def test_get_random_user_agent(self):
        ua = self.ua_manager.get_random_user_agent()
        self.assertIn(ua, self.ua_manager.user_agents)

if __name__ == '__main__':
    unittest.main()