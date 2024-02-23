class Client:
    def send(self, command : str | bytes) -> None:
        pass

    def read_line(self) -> bytes:
        pass

    def read_bytes(self, size : int) -> bytes:
        pass

    def read_until(self, value: str | bytes) -> bytes:
        pass

    def read_all(self) -> bytes:
        pass

    def get_username(self) -> str:
        pass

    def change_timeout(self, value : int | float):
        pass

    def restore_timeout(self):
        pass