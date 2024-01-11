class KauderwelschError(Exception):
    pass


class ParsingError(KauderwelschError):
    pass


class TokenizationError(KauderwelschError):
    pass


class TranspilationError(KauderwelschError):
    pass
