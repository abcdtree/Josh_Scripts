import os
import subprocess
import toml

def bash_command(cmd):
    p = subprocess.Popen(cmd, shell=True)
    while True:
        return_code = p.poll()
        if return_code is not None:
            break
    return

def clean_up():
    with open("all_isolates_20210325.txt", 'r') as myids:
        for mp in myids:
            mid = mp.strip()
            if os.path.exists(mid):
                if not os.path.exists(os.path.join(mid, "tbprofiler.snpit_results.json")):
                    print(mid)
                    #cmd = f"rm -rf {mid}"
                    #bash_command(cmd)
clean_up()
