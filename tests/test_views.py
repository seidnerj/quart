from __future__ import annotations

from typing import Any
from typing import Callable

import pytest

from quart import Quart
from quart import request
from quart import ResponseReturnValue
from quart.views import MethodView
from quart.views import View


@pytest.fixture
def app() -> Quart:
    app = Quart(__name__)
    return app


async def test_view(app: Quart) -> None:
    class Views(View):
        methods = ["GET", "POST"]

        async def dispatch_request(
            self, *args: Any, **kwargs: Any
        ) -> ResponseReturnValue:
            return request.method

    app.add_url_rule("/", view_func=Views.as_view("simple"))

    test_client = app.test_client()
    response = await test_client.get("/")
    assert "GET" == (await response.get_data(as_text=True))
    response = await test_client.put("/")
    assert response.status_code == 405


async def test_method_view(app: Quart) -> None:
    class Views(MethodView):
        async def get(self) -> ResponseReturnValue:
            return "GET"

        async def post(self) -> ResponseReturnValue:
            return "POST"

    app.add_url_rule("/", view_func=Views.as_view("simple"))

    test_client = app.test_client()
    response = await test_client.get("/")
    assert "GET" == (await response.get_data(as_text=True))
    response = await test_client.post("/")
    assert "POST" == (await response.get_data(as_text=True))


async def test_view_decorators(app: Quart) -> None:
    def decorate_status_code(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> ResponseReturnValue:
            response = await func(*args, **kwargs)
            return response, 201

        return wrapper

    class Views(View):
        decorators = [decorate_status_code]
        methods = ["GET"]

        async def dispatch_request(
            self, *args: Any, **kwargs: Any
        ) -> ResponseReturnValue:
            return request.method

    app.add_url_rule("/", view_func=Views.as_view("simple"))

    test_client = app.test_client()
    response = await test_client.get("/")
    assert response.status_code == 201
