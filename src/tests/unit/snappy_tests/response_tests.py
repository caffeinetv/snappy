"""Response Testing"""

import unittest

from snappy import response


class ResponseTests(unittest.TestCase):
    """Response Testing"""

    def test_generic(self):
        res = response.generic(123, "Hello from test")
        self.assertEquals(res["statusCode"], 123)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(res["body"], "Hello from test")

    def test_ok(self):
        res = response.ok("Happy")
        self.assertEquals(res["statusCode"], 200)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(res["body"], "Happy")

    def test_error(self):
        res = response.error(666, {"x": 987})
        self.assertEquals(res["statusCode"], 666)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(res["body"], """{"errors": {"x": 987}}""")

    def test_bad_request(self):
        res = response.bad_request()
        self.assertEquals(res["statusCode"], 400)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(
            res["body"], """{"errors": {"_request": ["bad request"]}}""")

    def test_unauthorized(self):
        res = response.unauthorized()
        self.assertEquals(res["statusCode"], 401)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(
            res["body"],
            """{"errors": {"_token": ["the access token is invalid"]}}""")

    def test_not_found(self):
        res = response.not_found()
        self.assertEquals(res["statusCode"], 404)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(
            res["body"], """{"errors": {"_resource": ["not found"]}}""")

    def test_unprocessable(self):
        res = response.unprocessable({"xyz": 123})
        self.assertEquals(res["statusCode"], 422)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(
            res["body"], """{"errors": {"xyz": 123}}""")

    def test_internal_server_error(self):
        res = response.internal_server_error()
        self.assertEquals(res["statusCode"], 500)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(
            res["body"],
            """{"errors": {"_internal": "Internal server error"}}""")

    def test_method_not_allowed(self):
        res = response.method_not_allowed()
        self.assertEquals(res["statusCode"], 405)
        self.assertEquals(res["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEquals(
            res["headers"]["Access-Control-Allow-Headers"],
            (
                "Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,"
                "X-Amz-Security-Token,x-client-type,x-client-version"
            )
        )
        self.assertEquals(
            res["body"],
            """{"errors": {"_internal": "Method Not Allowed"}}""")
