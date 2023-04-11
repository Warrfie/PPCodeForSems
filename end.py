import requests

from test import agent_code


def main():
    print(requests.get("http://localhost/end", headers={"agent": agent_code}).text)

if __name__ == '__main__':
    main()