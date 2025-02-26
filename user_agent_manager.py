import random
import json
from config import USER_AGENT_FILE

class UserAgentManager:
    def __init__(self):
        self.user_agents = self.load_user_agents()

    @staticmethod
    def load_user_agents():
        try:
            with open(USER_AGENT_FILE, "r", encoding="utf-8") as file:
                agents = json.load(file)
                return [agent["ua"] for agent in agents]
        except Exception as e:
            raise Exception(f"Ошибка загрузки User-Agent: {e}")

    def get_random_user_agent(self):
        return random.choice(self.user_agents)