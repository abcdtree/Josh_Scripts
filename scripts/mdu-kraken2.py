import os

def bash_command(cmd):
	p = subprocess.Popen(cmd, shell=True)
	while True:
		return_code = p.poll()
		if return_code is not None:
			break
	return

def load_db(db_type):
    db_path = ""
    if db_type == "r207":
        db_path = "/home/mdu/resources/kraken2/gtdb_r207"
    elif db_type == "r202":
        db_path = "/home/mdu/resources/kraken2/gtdb_r202"
    elif db_type == "pluspf"
        db_path = "/home/linuxbrew/db/kraken2/pluspf"
    else:
        db_type = "pluspf"
        db_path = "/home/linuxbrew/db/kraken2/pluspf"


def run_kraken2(args):
