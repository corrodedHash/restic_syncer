from pathlib import Path
import datetime
from dataclasses import dataclass


@dataclass
class SshServer:
    user: str
    server: str
    private_key: Path
    port: int


@dataclass
class Snapshot:
    id: str
    date: datetime.datetime


@dataclass
class ResticRepo:
    path: str
    password_file: Path
