class ScrapeError(RuntimeError):
    pass


class MissingCredentialsError(ScrapeError):
    pass


class EmptyResponseError(ScrapeError):
    pass
