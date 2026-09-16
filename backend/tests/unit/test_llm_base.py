import pytest

from app.llm.base import LLMProvider


def test_cannot_instantiate_base():
    with pytest.raises(TypeError):
        LLMProvider("key")


def test_subclass_must_implement_all():
    class Incomplete(LLMProvider):
        def __init__(self, api_key):
            pass

    with pytest.raises(TypeError):
        Incomplete("key")
