import requests

from test import agent_code


def main():
    print(requests.get("http://localhost/fix", headers={"agent": agent_code, "field": "PASSPORT"}).text)

if __name__ == '__main__':
    main()