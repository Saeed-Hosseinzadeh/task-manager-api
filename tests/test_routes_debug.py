def test_debug_routes(client):
    routes = []

    for route in client.app.routes:
        routes.append(getattr(route, "path", str(route)))

    assert False, routes
