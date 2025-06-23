import threading
import time
import win32file
import pywintypes


class KrkrHasher:
    _instance = None
    _lock     = threading.Lock()

    PIPE_NAME = r"\\.\pipe\KrkrDump-Hasher"

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._pipe = None
                cls._instance._pipe_lock = threading.Lock()
            return cls._instance

    def compute(self, text: str, salt: str = "xp3hnp") -> str:
        if not text:
            raise ValueError("text must not be empty")

        for _ in range(2):
            try:
                pipe = self._get_pipe()
                win32file.WriteFile(pipe, f"{text}|{salt}\n".encode("utf-8"))
                _, raw = win32file.ReadFile(pipe, 80)
                return raw.decode("utf-8").strip()

            except pywintypes.error as e:
                # 233=ERROR_NO_DATA, 232=PIPE_NOT_CONNECTED, 109=BROKEN_PIPE, 2=FILE_NOT_FOUND
                if e.winerror in (233, 232, 109, 2):
                    self._close_pipe()
                    time.sleep(0.01)
                    continue
                raise
        raise RuntimeError("cannot communicate with KrkrDump-Hasher named pipe")

    def _get_pipe(self):
        if self._pipe:
            return self._pipe

        with self._pipe_lock:
            if self._pipe:
                return self._pipe

            while True:
                self._pipe = win32file.CreateFile(
                    self.PIPE_NAME,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None, win32file.OPEN_EXISTING, 0, None)
                return self._pipe


    def _close_pipe(self):
        with self._pipe_lock:
            if self._pipe:
                try:
                    self._pipe.Close()
                except Exception:
                    pass
                self._pipe = None


if __name__ == "__main__":
    for _ in range(5):
        print("helloworld =", KrkrHasher().compute("helloworld"))
    print("startup.tjs =", KrkrHasher().compute(r"startup.tjs"))
    print("startup.tjs =", KrkrHasher().compute(r"startup.tjs", ""))
    print(KrkrHasher().compute("天音a_7553.tlg"))
    print(KrkrHasher().compute("ama_002_0033.ogg"))
