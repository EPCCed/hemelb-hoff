import os
import paramiko

path_to_hosts_file = os.path.join("~", ".ssh", "known_hosts")


def run_remote_command(server, username, passphrase, command):
    client = paramiko.SSHClient()
    client.load_host_keys(os.path.expanduser(path_to_hosts_file))
    client.connect(server, username=username, passphrase=passphrase)
    stdin, stdout, stderr = client.exec_command(command)

    stdout = stdout.readlines()
    stderr = stderr.readlines()

    client.close()

    return stdout, stderr



