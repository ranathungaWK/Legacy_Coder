import subprocess
import tempfile
import os 
from typing import Optional
from app.schemas.verifyExecution import ExecutionResult

def run_pytest_in_docker(
    solution_code: str,
    test_code: str,
    image: str = "sandbox-python:3.11",
    timeout: int = 120,
    requirements_text: Optional[str] = None,
    pip_cache_path: Optional[str] = None,
) -> ExecutionResult:
    """
    Run pytest in a Docker container to test the solution code.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        import pathlib
        tmpdir = str(pathlib.Path(tmpdir).resolve())
        solution_path = os.path.join(tmpdir, "solution.py")
        test_path = os.path.join(tmpdir, "test_solution.py")
        requirements_path = os.path.join(tmpdir, "requirements.txt")

        with open(solution_path, "w", encoding="utf-8") as f :
            f.write(solution_code)
        
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        if requirements_text and requirements_text.strip():
            with open(requirements_path, "w", encoding="utf-8") as f:
                f.write(requirements_text)

        # Build docker create command
        import uuid
        container_name = f"sandbox_{uuid.uuid4().hex}"
        cmd_create = ["docker", "create", "--name", container_name]

        # optionally mount pip cache to speed up installs
        if pip_cache_path:
            # only attempt to mount if the path exists on host
            try:
                if os.path.exists(pip_cache_path):
                    cmd_create.extend(["-v", f"{pip_cache_path}:/root/.cache/pip"])
            except Exception:
                pass
        else:
            # Optionally mount a named docker volume for pip cache if requested.
            # This is useful in CI where a host path may not be available.
            try:
                # Default to True unless explicitly disabled
                use_volume = os.getenv("SANDBOX_USE_PIP_VOLUME", "true").lower() in ("1", "true", "yes")
            except Exception:
                use_volume = True

            if use_volume:
                cmd_create.extend(["-v", "pip_cache:/root/.cache/pip"])

        # set workdir
        cmd_create.extend(["-w", "/workspace"])

        # Enforce size limit
        try:
            size_limit_mb = int(os.getenv("SANDBOX_SIZE_LIMIT_MB", "250"))
        except ValueError:
            size_limit_mb = 250

        # use sh entrypoint to perform optional install then run pytest
        cmd_create.extend([
            "--entrypoint", "sh",
            image,
            "-lc",
            f"set -e; "
            f"if [ -f requirements.txt ]; then "
            f"  pip install --no-cache-dir -r requirements.txt; "
            f"  SIZE=$(du -sm /usr/local/lib | cut -f1 || echo 0); "
            f"  if [ \"$SIZE\" -gt {size_limit_mb} ]; then "
            f"    echo 'Error: Installed libraries exceed the {size_limit_mb}MB size limit.' >&2; "
            f"    exit 1; "
            f"  fi; "
            f"fi; "
            f"pytest -vv",
        ])

        try:
            # 1. Create the container
            subprocess.run(cmd_create, check=True, capture_output=True)

            # 2. Copy the files into the container. 
            # Note: <src>/. copies the contents of the directory into the target directory.
            subprocess.run(["docker", "cp", f"{tmpdir}/.", f"{container_name}:/workspace/"], check=True, capture_output=True)

            # 3. Start the container and capture output
            cmd_start = ["docker", "start", "-a", container_name]
            result = subprocess.run(cmd_start, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)

            # If the container exited with non-zero, examine stderr for pip-related failures
            stderr = result.stderr or ""
            stdout = result.stdout or ""

            if result.returncode != 0:
                guidance = []
                lower = (stderr + stdout).lower()
                
                if "installed libraries exceed the" in lower or "size limit" in lower:
                    guidance.append(
                        f"The sandbox execution failed because the downloaded libraries exceeded the {size_limit_mb}MB size limit."
                    )
                    guidance.append(
                        "Please optimize your requirements to reduce the download size, or increase the SANDBOX_SIZE_LIMIT_MB environment variable."
                    )
                elif "pip" in lower or "wheel" in lower or "building wheel" in lower or "could not find a version" in lower or "connection" in lower or "timed out" in lower:
                    guidance.append(
                        "Dependency installation failed inside sandbox. This may be due to network problems, missing system libraries, or very large/compiled packages."
                    )
                    guidance.append(
                        "Options: (1) provide a prebuilt sandbox image with the heavy deps preinstalled, (2) set SANDBOX_PIP_CACHE to a host pip cache path, (3) enable a named Docker pip cache volume via SANDBOX_USE_PIP_VOLUME=1, or (4) increase SANDBOX_TIMEOUT to allow more time for builds."
                    )

                if guidance:
                    stderr = stderr + "\n\n" + "\n".join(guidance)

            return ExecutionResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=stdout,
                stderr=stderr,
                timed_out=False
            )

        except subprocess.TimeoutExpired as e:
            guidance = (
                "The sandbox run timed out before completing. This commonly happens when installing large packages or when network/downloads are slow. "
                "Retry options: increase SANDBOX_TIMEOUT, mount a pip cache via SANDBOX_PIP_CACHE, or use a prebuilt sandbox image containing the heavy dependencies."
            )

            stderr = (e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else (e.stderr or "")) + "\n\n" + guidance
            stdout = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or "")

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout=stdout,
                stderr=stderr,
                timed_out=True
            )
            
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else (e.stderr or "")
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Failed to setup sandbox container: {stderr}",
                timed_out=False
            )
        finally:
            # Ensure the container is forcefully removed, even if it timed out and is still running in the background.
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)