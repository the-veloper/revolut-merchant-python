class RevolutHttpError(Exception):
    def __init__(self, response_status_code, error_id):
        self.response_status_code = response_status_code
        self.error_id = error_id


def raise_error(status_code, error_id):
    raise RevolutHttpError(status_code, error_id)
