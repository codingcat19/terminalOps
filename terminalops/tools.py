"""Reusable tools for TerminalOps agents."""

from __future__ import annotations

import datetime
import os
import shlex
import subprocess
from typing import Callable, Iterable

from terminalops.safety import needs_confirmation

try:
    import psutil
except ImportError:  # pragma: no cover - dependency is optional at import time
    psutil = None

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


ConfirmationCallback = Callable[[str], bool]


def _run_command(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    output = output.strip() or "(no output)"
    if result.returncode != 0:
        return f"Command failed with exit code {result.returncode}.\n{output}"
    return output


def list_repo_files(base_path: str = ".", max_depth: int = 4) -> str:
    """Return a simple file tree for the repository path."""
    root = os.path.abspath(base_path)
    if not os.path.isdir(root):
        return f"Path not found: {base_path}"

    output = []
    for current_root, dirs, files in os.walk(root):
        rel_root = os.path.relpath(current_root, root)
        depth = 0 if rel_root == "." else rel_root.count(os.sep) + 1
        if depth > max_depth:
            dirs[:] = []
            continue

        if ".git" in dirs:
            dirs.remove(".git")

        for file_name in sorted(files):
            rel_path = os.path.join(rel_root, file_name) if rel_root != "." else file_name
            output.append(rel_path)

    return "\n".join(sorted(output)) or "(no files found)"


def read_file_text(file_path: str, max_lines: int = 200) -> str:
    """Return the requested file content with line numbers."""
    normalized_path = os.path.normpath(os.path.join(os.getcwd(), file_path))
    if not normalized_path.startswith(os.getcwd()):
        return "Invalid file path."
    if not os.path.isfile(normalized_path):
        return f"File not found: {file_path}"

    try:
        with open(normalized_path, "r", encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError as exc:
        return f"Unable to read file: {exc}"

    selected_lines = lines[:max_lines]
    formatted = [f"{idx + 1}: {line.rstrip()}" for idx, line in enumerate(selected_lines)]
    if len(lines) > max_lines:
        formatted.append(f"...truncated after {max_lines} lines")
    return "\n".join(formatted)


def search_code_text(query: str, base_path: str = ".", max_results: int = 50) -> str:
    """Search source files for a query string."""
    root = os.path.abspath(base_path)
    if not os.path.isdir(root):
        return f"Path not found: {base_path}"

    results = []
    for current_root, dirs, files in os.walk(root):
        if ".git" in dirs:
            dirs.remove(".git")

        for file_name in sorted(files):
            if not file_name.lower().endswith((
                ".py", ".md", ".txt", ".yaml", ".yml", ".json", ".sh", ".js", ".ts", ".cfg", ".ini"
            )):
                continue
            file_path = os.path.join(current_root, file_name)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        if query.lower() in line.lower():
                            rel_path = os.path.relpath(file_path, root)
                            results.append(f"{rel_path}:{line_number}: {line.strip()}")
                            if len(results) >= max_results:
                                return "\n".join(results)
            except OSError:
                continue

    return "\n".join(results) if results else f"No matches found for: {query}"


def get_system_time_text() -> str:
    """Return the current system date and time."""
    now = datetime.datetime.now()
    return now.strftime("%A, %b %d, %Y - %H:%M")


def get_system_resources_text() -> str:
    """Return concrete CPU, memory, and disk usage for the local machine."""
    if psutil is None:
        return "psutil is not installed. Install project dependencies to use system resource checks."

    cpu = psutil.cpu_percent(interval=0.2)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return "\n".join(
        [
            f"CPU Usage: {cpu}%",
            f"RAM Usage: {memory.percent}% ({_format_bytes(memory.used)} used / {_format_bytes(memory.total)} total)",
            f"Disk Usage: {disk.percent}% ({_format_bytes(disk.used)} used / {_format_bytes(disk.total)} total)",
        ]
    )


def get_git_status_text() -> str:
    """Return the current git status."""
    return _run_command("git status -s -b")


def get_repo_files_text() -> str:
    """Return a concise listing of repository files."""
    return list_repo_files()


def get_docker_containers_text() -> str:
    """Return running Docker containers."""
    return _run_command("docker ps")


def get_docker_images_text() -> str:
    """Return available Docker images."""
    return _run_command("docker images")


def _format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def build_tools(confirm_callback: ConfirmationCallback | None = None) -> list:
    """Build the tool list for a TerminalOps agent."""

    def should_run(command: str) -> bool:
        if not needs_confirmation(command):
            return True
        if confirm_callback is None:
            return False
        return confirm_callback(command)

    @tool
    def shell_command(command: str) -> str:
        """
        Executes a shell command in the current working directory.
        Use this for general terminal, file system, git, and DevOps tasks.
        """
        if not should_run(command):
            return f"Shell command was not approved: {command}"
        return _run_command(command)

    @tool
    def list_containers() -> str:
        """Executes 'docker ps' and returns running containers."""
        return get_docker_containers_text()

    @tool
    def get_container_logs(container_name: str) -> str:
        """Fetches the last 20 lines of logs for a specific container."""
        return _run_command(f"docker logs --tail 20 {shlex.quote(container_name)}")

    @tool
    def run_container(image_name: str) -> str:
        """Starts a Docker container in detached mode from the provided image."""
        command = f"docker run -d -p 127.0.0.1:3000:3000 {shlex.quote(image_name)}"
        if not should_run(command):
            return f"Container start was not approved for image: {image_name}"
        return _run_command(command)

    @tool
    def stop_container(container_id: str) -> str:
        """Stops a running Docker container using its ID or name."""
        command = f"docker stop {shlex.quote(container_id)}"
        if not should_run(command):
            return f"Container stop was not approved for: {container_id}"
        return _run_command(command)

    @tool
    def list_images() -> str:
        """Returns available Docker images."""
        return get_docker_images_text()

    @tool
    def inspect_container(container_name: str) -> str:
        """Inspect a Docker container or image."""
        return _run_command(f"docker inspect {shlex.quote(container_name)}")

    @tool
    def exec_container(container_name: str, command: str) -> str:
        """Executes a command inside a running Docker container."""
        docker_command = f"docker exec {shlex.quote(container_name)} {shlex.quote(command)}"
        if not should_run(docker_command):
            return f"Execution inside container was not approved for: {container_name}"
        return _run_command(docker_command)

    @tool
    def get_git_status() -> str:
        """Returns the current git status including the current branch."""
        return get_git_status_text()

    @tool
    def list_repo_files_tool() -> str:
        """Lists repository files for the current working directory."""
        return get_repo_files_text()

    @tool
    def read_file(file_path: str) -> str:
        """Returns the content of a file in the repository."""
        return read_file_text(file_path)

    @tool
    def search_code(query: str) -> str:
        """Searches repository files for the given query."""
        return search_code_text(query)

    @tool
    def get_system_time() -> str:
        """Returns the current system date and time."""
        return get_system_time_text()

    @tool
    def check_system_resources() -> str:
        """Checks the current CPU and RAM usage."""
        return get_system_resources_text()

    return [
        shell_command,
        list_containers,
        get_container_logs,
        run_container,
        stop_container,
        list_images,
        inspect_container,
        exec_container,
        get_git_status,
        list_repo_files_tool,
        read_file,
        search_code,
        get_system_time,
        check_system_resources,
    ]


def describe_tools(tools: Iterable) -> list[str]:
    """Return human-readable tool names for the CLI."""
    names = []
    for item in tools:
        names.append(getattr(item, "__name__", str(item)))
    return names
