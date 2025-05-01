import subprocess
import json
import platform
import shutil
import sys
from utils.log import logger


async def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

async def install_packages():
    """Install required system packages based on the operating system."""
    os_name = platform.system().lower()
    packages = ["tcpdump", "iperf3"]
    dns_package = "dnsutils"

    if os_name == "linux":
        distro = platform.freedesktop_os_release().get("ID", "").lower()
        if distro in ["ubuntu", "debian"]:
            logger.info("Detected Ubuntu/Debian. Installing packages with apt...")
            logger.info(run_command("sudo apt update"))
            logger.info(run_command(f"sudo apt install -y traceroute {dns_package} {' '.join(packages)}"))
        elif distro in ["centos", "rhel", "fedora"]:
            logger.info("Detected CentOS/RHEL/Fedora. Installing packages with yum/dnf...")
            logger.info(run_command("sudo yum install -y epel-release"))
            logger.info(run_command(f"sudo yum install -y traceroute bind-utils {' '.join(packages)}"))
        else:
            logger.info("Unsupported Linux distribution. Please install packages manually.")
            sys.exit(1)
    elif os_name == "darwin":
        logger.info("Detected macOS. Installing packages with Homebrew...")
        if not shutil.which("brew"):
            logger.info("Installing Homebrew...")
            logger.info(run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'))
        logger.info(run_command(f"brew install {' '.join(packages)}"))
    else:
        logger.info("Unsupported OS. For Windows, use WSL or install tools manually.")
        sys.exit(1)

async def check_tools():
    """Check if required tools are installed."""
    tools = ["ping", "traceroute", "nslookup", "tcpdump", "iperf3"]
    missing = [tool for tool in tools if not shutil.which(tool)]
    if missing:
        logger.info(f"Missing tools: {', '.join(missing)}. Installing...")
        install_packages()
    else:
        logger.info("All required tools are installed.")

async def run_network_diagnostics(target: str) -> str:
    """Execute ping, traceroute, and nslookup for the target."""
    try:
        ping_result = subprocess.run(["ping", "-c", "4", target], capture_output=True, text=True, check=True).stdout
        logger.info(f"Ping result is ready.")
        # max hops set to 15
        traceroute_result = subprocess.run(["traceroute", "-m", "15", target], capture_output=True, text=True, check=True).stdout
        logger.info(f"Traceroute result is ready.")
        nslookup_result = subprocess.run(["nslookup", target], capture_output=True, text=True, check=True).stdout
        logger.info(f"Nslookup result is ready.")
        result = {
            "ping": ping_result,
            "traceroute": traceroute_result,
            "nslookup": nslookup_result
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Command failed: {e.stderr}"}, ensure_ascii=False)
    except FileNotFoundError as e:
        return json.dumps({"error": f"Command not found: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

async def main():
    await check_tools()
    target = "google.com"
    print(f"\nRunning network diagnostics for: {target}")
    result = await run_network_diagnostics(target)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())