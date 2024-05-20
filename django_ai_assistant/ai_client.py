from openai import AsyncOpenAI


def init_openai(*, request, **kwargs):
    return AsyncOpenAI(**kwargs)
