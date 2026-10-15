"""A local-only client; sends no request to an external host."""
import argparse
import http.client
import json


def request(port, topic, language="pt-BR", token="acme-demo"):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    body = json.dumps({"topic":topic, "language":language}).encode("utf-8")
    try:
        connection.request("POST", "/v1/answers", body,
            {"Content-Type":"application/json", "Authorization":"Bearer " + token})
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally: connection.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--topic", default="returns")
    p.add_argument("--language", choices=("pt-BR","en-US"), default="pt-BR")
    p.add_argument("--token", default="acme-demo")
    a = p.parse_args()
    status, result = request(a.port, a.topic, a.language, a.token)
    print(status)
    print(json.dumps(result, ensure_ascii=False, indent=2))
