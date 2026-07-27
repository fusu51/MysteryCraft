"""统一日志配置 — 双输出（终端彩色 + 文件 JSON）"""
import logging
import logging.config
from pathlib import Path
import datetime


def setup_logging(log_dir: str = "logs") -> None:
    """初始化全局日志配置，在 api/server.py 启动时调用一次"""

    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    today = datetime.date.today().isoformat()
    json_log = log_path / f"{today}.log"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(message)s",   # trace.py 自己拼格式，不做二次加工
            },
            "json": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": str(json_log),
                "maxBytes": 10 * 1024 * 1024,   # 10MB
                "backupCount": 7,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "mysterycraft": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)


def get_logger(name: str = "mysterycraft") -> logging.Logger:
    """获取应用日志实例"""
    return logging.getLogger(name)
