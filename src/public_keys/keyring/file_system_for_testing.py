from public_keys.keyring.core import Keyring


class InMemoryTestingRing(dict, Keyring):
    def lock(self, password: str) -> None:
        pass

    def unlock(self, password: str, count: int) -> None:
        pass
