import pytest
from dotenv import find_dotenv, load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    env_file = find_dotenv(".env.tests")
    load_dotenv(env_file)


def clear_response(response):
    headers = [
        ("CF-Cache-Status", None),
        ("CF-RAY", None),
        ("Date", "Sun, 09 Jun 2024 23:39:08 GMT"),
        ("Server", "DUMMY"),
        ("alt-svc", None),
        ("openai-organization", None),
        ("openai-processing-ms", None),
        ("openai-version", None),
        ("x-ratelimit-limit-requests", None),
        ("x-ratelimit-limit-tokens", None),
        ("x-ratelimit-remaining-requests", None),
        ("x-ratelimit-remaining-tokens", None),
        ("x-ratelimit-reset-requests", None),
        ("x-ratelimit-reset-tokens", None),
        ("x-request-id", None),
        ("Set-Cookie", None),
        ("strict-transport-security", None),
    ]
    for header, value in headers:
        if value is None:
            response["headers"].pop(header, None)
        else:
            response["headers"][header] = value
    return response


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("authorization", "DUMMY"),
            ("cookie", "DUMMY"),
            ("user-agent", "OpenAI/Python"),
            ("x-stainless-arch", None),
            ("x-stainless-async", None),
            ("x-stainless-lang", None),
            ("x-stainless-os", None),
            ("x-stainless-package-version", None),
            ("x-stainless-runtime", None),
            ("x-stainless-runtime-version", None),
            ("x-api-key", None),
        ],
        "before_record_response": clear_response,
        # Request must has the same body as the recorded request:
        "match_on": ["method", "scheme", "host", "port", "path", "query", "body"],
    }
