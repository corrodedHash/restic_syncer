import subprocess
from pathlib import Path
import json
import datetime

from .types import ResticRepo, Snapshot, SshServer


def list_restic_snapshots(
    repo: str, password_file: Path, extra_args: list[str] = []
) -> list[Snapshot]:
    process = subprocess.run(
        [
            "restic",
            *extra_args,
            "--password-file",
            str(password_file),
            "--repo",
            repo,
            "snapshots",
            "--json",
        ],
        shell=False,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    v = process.stdout
    snapshots = json.loads(v)
    s = sorted(
        [
            Snapshot(
                id=snapshot["id"],
                date=datetime.datetime.fromisoformat(snapshot["time"]),
            )
            for snapshot in snapshots
        ],
        key=lambda x: x.date,
    )

    return s


def get_remote_snapshots(repo: ResticRepo, server: SshServer) -> list[Snapshot]:

    repo_path = f"sftp:{server.user}@{server.server}:{repo.path}"
    extra_args = [
        "--no-lock",
        "--option",
        f"sftp.args=-p {server.port} -i {server.private_key}",
    ]
    return list_restic_snapshots(repo_path, repo.password_file, extra_args)


def get_local_snapshots(repo: ResticRepo) -> list[Snapshot]:
    return list_restic_snapshots(repo.path, repo.password_file)
