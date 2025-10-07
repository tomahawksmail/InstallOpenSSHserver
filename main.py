import winrm
import getpass

# --- Configuration ---
HOSTS_FILE = "hosts.txt"  # one hostname or IP per line
USERNAME = "domain name\\admin-name"
PASSWORD = "SuperMegaStrongPassword"

# --- PowerShell command to install & configure OpenSSH Server ---
PS_SCRIPT = r"""
Write-Output "Installing OpenSSH.Server if missing..."
$cap = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($cap.State -ne 'Installed') {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction Stop
}

Set-Service -Name sshd -StartupType Automatic
Start-Service sshd

# enable firewall rule
if (-not (Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (Inbound)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
}

Write-Output "OpenSSH.Server installation complete."
"""

# --- Read host list ---
with open(HOSTS_FILE) as f:
    hosts = [line.strip() for line in f if line.strip()]

# --- Loop over hosts ---
for host in hosts:
    print(f"\n=== {host} ===")
    try:
        session = winrm.Session(
            target=host,
            auth=(USERNAME, PASSWORD),
            transport='ntlm'
        )

        result = session.run_ps(PS_SCRIPT)

        if result.status_code == 0:
            print(result.std_out.decode('utf-8', errors='ignore'))
        else:
            print("Error:")
            print(result.std_err.decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"Failed to connect: {e}")
