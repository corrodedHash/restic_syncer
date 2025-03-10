import logging
import subprocess
from syncer.snapshot_list import get_local_snapshots, get_remote_snapshots
from syncer.types import ResticRepo, SshServer


def sync_snapshots(
    server: SshServer, remote_repo: ResticRepo, local_repo: ResticRepo
) -> None:
    s = get_remote_snapshots(remote_repo, server)
    ls = get_local_snapshots(local_repo)
    if not ls:
        unsynced_remote = s
    else:
        most_recent_local = max(ls, key=lambda x: x.date)
        unsynced_remote = [
            snapshot for snapshot in s if snapshot.date > most_recent_local.date
        ]
    logger = logging.getLogger()
    logger.info(f"Syncing [{len(unsynced_remote)}] snapshots for {local_repo.path}")

    remote_repo_path = f"sftp:{server.user}@{server.server}:{remote_repo.path}"
    subprocess.run(
        [
            "restic",
            "--no-lock",
            "--option",
            f"sftp.args=-p {server.port} -i {server.private_key}",
            "--password-file",
            str(local_repo.password_file),
            "--from-password-file",
            str(remote_repo.password_file),
            "--from-repo",
            remote_repo_path,
            "--repo",
            str(local_repo.path),
            "copy",
            *[s.id for s in unsynced_remote],
        ],
        shell=False,
        check=True,
    )
