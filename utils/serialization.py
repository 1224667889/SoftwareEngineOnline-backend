"""序列化输出"""
code_to_msg = {
    200: "Success",
    400: "Parameter Error",
    401: "Insufficient Authority",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Fail",

    40000: "Wrong Code",
    40001: "Has Joined A Team",
    40002: "Full Members",
    40003: "Repetitive Name",
    40004: "Did Not Join A Team",

    50000: "Token Error",
    50001: "Token Expiration",

}


def make_resp(data, code=200, msg=None):
    if msg is None:
        msg = code_to_msg.get(code, "Operate Successfully")
    resp = {
        "status": code,
        "message": msg,
        "data": data
    }
    return resp
