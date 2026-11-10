import subprocess


def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def count_files(directory):
    out = run_command("ls " + directory + " | wc -l")
    return int(out)
