import typing as t
import threading
import gpiod
import select


__all__ = [
    'GPIOMon'
]


class GPIOMon:

    def __init__(self, dev_name: str, lines: int | t.Iterable[int], handler: t.Callable | None = None,
                 args: tuple | None = None, kwargs: dict | None = None, settings: gpiod.LineSettings | None = None,
                 poll_timeout: float = 0.01) -> None:
        self.dev_name = dev_name
        self.lines = lines if isinstance(lines, t.Iterable) else [lines]
        self.settings = settings or gpiod.LineSettings(edge_detection=gpiod.line.Edge(gpiod.line.Edge.BOTH))
        self.settings.direction = gpiod.line.Direction(gpiod.line.Direction.INPUT)
        self._check_chip()
        self.handlers = [(args or (), kwargs or {}, handler)] if handler else []
        self.poll_timeout = poll_timeout
        self.running = False
        self.name = f'GPIOMon {self.dev_name}({self.lines})'
        self.thread = threading.Thread(target=self.monitor, name=self.name)

    def _check_chip(self) -> None:
        with gpiod.Chip(self.dev_name) as chip:
            info = chip.get_info()
            for line in self.lines:
                if line >= info.num_lines:
                    raise ValueError(f'Line {line} is out of range')

    def add_lines(self, lines: int | t.Iterable[int]) -> None:
        for line in (lines if isinstance(lines, t.Iterable) else [lines]):
            if line not in self.lines:
                self.lines.append(line)
        self._check_chip()

    def add_handler(self, handler: t.Callable, args: tuple | None = None, kwargs: dict | None = None) -> None:
        if not handler:
            raise ValueError('No handler specified')
        self.handlers.append((args or (), kwargs or {}, handler))

    def remove_handler(self, handler: t.Callable, args: tuple | None = None, kwargs: dict | None = None) -> None:
        args = args or ()
        kwargs = kwargs or {}
        self.handlers[:] = [(a, kw, h) for (a, kw, h) in self.handlers if a != args or kw != kwargs or h != handler]

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.running = False

    def join(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.stop()
        self.thread.join(*args, **kwargs)

    def monitor(self) -> None:
        self.running = True

        with gpiod.Chip(self.dev_name) as chip:
            with chip.request_lines(config={ tuple(self.lines): self.settings }) as request:
                with select.epoll() as ep:
                    ep.register(request.fd)

                    while self.running:
                        if ep.poll(self.poll_timeout):
                            for event in request.read_edge_events():
                                if not self.running:
                                    break
                                for args, kwargs, handler in self.handlers:
                                    handler(*([event] + list(args)), **kwargs)
                                    if not self.running:
                                        break

        self.running = False
