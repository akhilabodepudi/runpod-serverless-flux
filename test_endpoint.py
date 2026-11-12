import json

from handler import handler


if __name__ == "__main__":
    with open("test_input.json", "r", encoding="utf-8") as file:
        payload = json.load(file)

    result = handler(payload)
    print(json.dumps(result, indent=2))
