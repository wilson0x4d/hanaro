---
name: hanaro
description: Non-invasive logging configurator — configure, filter, queue, and format logs via unified config. Use when working with hanaro, configure_logging, get_logger, ConfigFilter, ContextInjectionFilter, QueuedHandler, BidiFormatter, or patch_logging.
user-invocable: true
disable-model-invocation: false
---

# hanaro Library Reference

A **non-invasive logging configurator** for Python. Configure, filter, queue, and format logs via unified config (JSON/YAML/TOML/env vars/CLI).

**Source:** [github.com/wilson0x4d/hanaro](https://github.com/wilson0x4d/hanaro) — **Docs:** [hanaro.readthedocs.io](https://hanaro.readthedocs.io)

---

## Quick Start

```python
import hanaro

hanaro.configure_logging()           # apply defaults (or pass a config dict)
logger = hanaro.get_logger()         # auto-resolves calling module name
logger.info('Hello, World!')
# → [2025-12-31T12:34:56] Hello, World! level=INFO source=__main__
```

All config is optional. `configure_logging()` applies sensible defaults: a console handler using a `logfmt`-friendly format with bidirectional (RTL/LTR) text support.

---

## Configuration

hanaro uses **`appsettings2`** for a single unified config surface — JSON, YAML, TOML, environment variables, and CLI args.

### Top-level key

All logging config lives under the `logging` key:

```jsonc
{
  "logging": {
    "level":      "DEBUG",               // root level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
    "format":     "[%(asctime)s] %(message)s",
    "datefmt":    "%Y-%m-%dT%H:%M:%S",
    "bidi":       true,                  // enable BidiFormatter on console handlers (default: true)
    "handlers":   [],                    // optional — omit for default console handler
    "filters":    {}                     // optional — see ConfigFilter
  }
}
```

Environment variable equivalent: `LOGGING__LEVEL=WARNING`

### Handler types

Three handler `type` values are supported:

| type     | required fields                    | optional fields                        |
|----------|------------------------------------|----------------------------------------|
| `console`| —                                  | `level`, `format`                      |
| `file`   | —                                  | `path`, `name`, `max_size`, `max_count`|
| `custom` | `class` (fully-qualified classname)| `level`, `format`, `args`              |

**Console handler** — writes to `sys.stdout`.

**File handler** — `RotatingFileHandler` with auto-rotation.

```jsonc
{
  "type": "file",
  "path": "logs/",                      // default: "logs"
  "name": "debug.log",                  // default: "<level>_<date>.log"
  "max_size": "4KiB",                   // default: 4MiB; supports KiB/MiB/GiB suffix
  "max_count": 10,                      // default: 10
  "level": "DEBUG",
  "format": "[%(asctime)s] %(message)s"
}
```

**Custom handler** — import any `logging.Handler` subclass.

```jsonc
{
  "type": "custom",
  "class": "myapp.handlers.WebhookHandler",  // myapp/handlers.py: WebhookHandler(logging.Handler)
  "level": "ERROR",
  "format": "%(message)s",
  "args": { "url": "https://hooks.example.com" }  // passed as kwargs to the constructor
}
```

### Filters

The `filters` object specifies logger-name patterns and minimum levels. Each key is a logger name (regex by default, case-insensitive).

```jsonc
{
  "logging": {
    "filters": {
      "asyncio":      { "level": "WARNING" },
      "mysql\\..*":   { "level": "ERROR" },      // exact string match
      "urllib3\\..*": { "level": "WARNING", "regex": false }
    }
  }
}
```

- `level` — minimum level to **allow** through (default `DEBUG`).
- `regex` — treat the key as a regex pattern (default `true`). Regex is auto-anchored (`^pattern$`).

---

## Public API

### `configure_logging(configuration=None, force=False) → list[Handler]`

Apply logging configuration. Pass a dict or an `appsettings2.Configuration` object. `force=True` re-configures even if handlers already exist.

```python
# With defaults
hanaro.configure_logging()

# With explicit config
hanaro.configure_logging({'logging': {'level': 'WARNING', 'handlers': [{'type': 'console'}]}})

# With appsettings2
import appsettings2
hanaro.configure_logging(appsettings2.get_configuration())
```

### `get_logger(name=None, level=NOTSET, allow_queued_logger=True) → Logger`

Like `logging.getLogger()` but **auto-resolves** the calling module's `__name__`. Also auto-returns a queued logger when called from non-main threads.

```python
logger = hanaro.get_logger()                    # → resolves to calling module
logger = hanaro.get_logger('my.app', level='INFO')
```

### `get_queued_logger(name=None, level=NOTSET) → Logger`

A bare-bones `Logger` that forwards records to a thread-safe `QueuedHandler`. Use in background threads/tasks before draining records on the main thread.

```python
logger = hanaro.get_queued_logger('worker')
logger.info('message from background thread')
```

### `handle_queued_log_records()`

On the **main thread only**, drain and emit all queued records to the root logger.

```python
while not done:
    do_work()
    hanaro.handle_queued_log_records()
    await asyncio.sleep(0.1)
```

### `patch_logging()`

Monkey-patches `logging.getLogger` → `hanaro.get_logger` so that third-party code unaware of hanaro automatically gets module-name auto-resolution and queued-logger logic.

```python
import hanaro
hanaro.patch_logging()
logging.getLogger(__name__).info('this now resolves the caller')
```

---

## Components

### `ConfigFilter(logging.Filter)`

Filters log records by logger name pattern and minimum level. Used internally by `configure_logging` based on the `filters` config.

```python
from hanaro import ConfigFilter
f = ConfigFilter('my_filter', {'mysql\\..*': {'level': 'ERROR'}, 'test.*': {'level': 'INFO', 'regex': False}})
```

### `ContextInjectionFilter(logging.Filter)`

Injects key-value context data into log records. Supports two modes:

**Normal mode** — sets each key directly on the `LogRecord` (usable in format strings as `%(key)s`).

```python
ctx = ContextInjectionFilter({'request_id': 'abc-123'})
```

**Metadata mode** (`is_metadata=True`) — aggregates all context into a single `metadata` attribute for downstream indexing/search systems (ELK, Splunk, etc.).

```python
ctx = ContextInjectionFilter(is_metadata=True)       # → "{ key="val" }" in output
ctx['user_id'] = '42'                                 # → dict-like API
ctx['request_id'] = 'xyz'
del ctx['request_id']                                 # removes key
print(ctx['user_id'])                                 # → '42'
```

### `QueuedHandler(logging.Handler)`

Thread-safe queue for log records. Collects records from background threads and exposes them via static methods for the main thread to drain.

```python
from hanaro import QueuedHandler

# Records are collected in emit()
record = QueuedHandler.get_log_record()   # → LogRecord | None (non-blocking)
```

### `BidiFormatter(logging.Formatter)`

Formats log records with bidirectional text support via `python-bidi`. Applied automatically to console handlers when `python-bidi` is installed and `bidi` is not disabled in config.

```python
from hanaro.formatters import BidiFormatter
handler = logging.StreamHandler()
handler.formatter = BidiFormatter('[%(asctime)s] %(message)s', '%Y-%m-%dT%H:%M:%S')
```

Install optional bidi support: `pip install hanaro[bidi]`

---

## Import Map

```
hanaro
├── configure_logging        # utils.py — main entry point
├── get_logger               # utils.py — module-name auto-resolution
├── get_queued_logger        # utils.py — background-thread logger
├── handle_queued_log_records # utils.py — drain queue on main thread
├── patch_logging            # utils.py — monkey-patch logging.getLogger
├── ConfigFilter             # ConfigFilter.py — config-driven log filtering
├── ContextInjectionFilter   # ContextInjectionFilter.py — inject context/metadata
├── QueuedHandler            # QueuedHandler.py — thread-safe log queue
└── formatters
    └── BidiFormatter        # formatters/BidiFormatter.py — RTL/LTR text
```

---

## Deprecation Notes

| Old (deprecated since 1.0.0) | New                |
|------------------------------|--------------------|
| `configureLogging`           | `configure_logging`|
| `getLogger`                  | `get_logger`       |
| `getQueuedLogger`            | `get_queued_logger`|
| `handleQueuedLogRecords`     | `handle_queued_log_records` |

---

## Defaults Summary

| Setting          | Default                         |
|------------------|---------------------------------|
| Root level       | `DEBUG`                         |
| Format           | Python's `BASIC_FORMAT`         |
| Date format      | `%Y-%m-%dT%H:%M:%S`            |
| Console handler  | Yes (if no handlers configured) |
| Bidi support     | `True` (if `python-bidi` installed) |
| File max_size    | `4MiB`                          |
| File max_count   | `10`                            |
| File path        | `logs/`                         |
| File name        | `\<level\>\<date\>.log`         |
