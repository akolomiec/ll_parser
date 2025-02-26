from proxy_manager import ProxyManager
from user_agent_manager import UserAgentManager
from parser import Parser
from data_saver import save_to_csv

if __name__ == "__main__":
    proxy_manager = ProxyManager()
    user_agent_manager = UserAgentManager()
    parser = Parser(proxy_manager, user_agent_manager)

    print("🚀 Запуск парсера...")
    data = parser.parse_all_pages()
    save_to_csv(data)
    print("🏁 Парсинг завершён.")