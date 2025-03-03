import argparse
import subprocess
from pathlib import Path

from syncer.snapshot_sync import sync_snapshots

from .types import ResticRepo, SshServer


def get_repos(server: SshServer) -> list[str]:
    command = "ls -1 repos"
    process = subprocess.run(
        [
            "ssh",
            "-p",
            str(server.port),
            "-i",
            server.private_key,
            f"{server.user}@{server.server}",
            command,
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
        timeout=10,
    )
    repos = process.stdout.splitlines()
    return repos


def parse_args():
    parser = argparse.ArgumentParser(
        description="Parse SSH connection details and backup directories."
    )

    # SSH connection details
    parser.add_argument("--user", required=True, help="SSH username")
    parser.add_argument("--server-address", required=True, help="SSH server address")
    parser.add_argument(
        "--private-key-path", required=True, type=Path, help="Path to private SSH key"
    )
    parser.add_argument(
        "--port", type=int, default=22, help="SSH server port (default: 22)"
    )

    # Mandatory backup directory
    parser.add_argument(
        "--backup-dir", required=True, type=Path, help="Path to backup directory"
    )

    # Optional password directory
    parser.add_argument(
        "--password-dir", required=True, type=Path, help="Path to password directory"
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = SshServer(
        user=args.user,
        server=args.server,
        private_key=args.private_key_path,
        port=args.port,
    )
    password_dir = args.password_dir
    backup_dir = args.backup_dir
    repos = get_repos(server)
    for repo in repos:
        if not (backup_dir / repo).exists():
            subprocess.run(
                [
                    "restic",
                    "--repo",
                    str(backup_dir / repo),
                    "--password-file",
                    password_dir / "local",
                    "init",
                ]
            )
        sync_snapshots(
            server,
            remote_repo=ResticRepo(
                path=f"repos/{repo}", password_file=password_dir / repo
            ),
            local_repo=ResticRepo(
                path=str(backup_dir / repo), password_file=password_dir / "local"
            ),
        )


if __name__ == "__main__":
    main()
