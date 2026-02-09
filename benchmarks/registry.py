import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class Library(str, Enum):
    RAW = "raw"
    DATACLASSES_RAW = "dataclasses_raw"
    BEANIE = "beanie"
    MONGOENGINE = "mongoengine"


class OpType(str, Enum):
    READ = "read"
    WRITE = "write"


@dataclass
class BenchmarkInfo:
    name: str
    library: Library
    op_type: OpType
    collection: str
    description: str
    func: Callable
    is_async: bool


_registry: list[BenchmarkInfo] = []


def benchmark(
    name: str,
    library: Library,
    op_type: OpType,
    collection: str,
    description: str = "",
):
    def decorator(func):
        info = BenchmarkInfo(
            name=name,
            library=library,
            op_type=op_type,
            collection=collection,
            description=description,
            func=func,
            is_async=asyncio.iscoroutinefunction(func),
        )
        _registry.append(info)
        return func

    return decorator


def get_benchmarks(
    library: Library | None = None,
    op_type: OpType | None = None,
) -> list[BenchmarkInfo]:
    results = _registry
    if library:
        results = [b for b in results if b.library == library]
    if op_type:
        results = [b for b in results if b.op_type == op_type]
    return results
