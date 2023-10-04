#!/usr/bin/env python3
import pathlib, csv, sys,  re, os, subprocess, json

sample_sheet = sys.argv[1]
runid = sys.argv[2]
nanopore_dir = sys.argv[3]
mdu_reads = os.environ.get('MDU_READS')
reads_db = f"{mdu_reads}/reads.json"
barcode_reg = re.compile(r'(?P<prep>[A-Z]{2})?(?P<barcode>.{1,2})?')
mduids = {}
print(f"Opening {sample_sheet}")
with open(sample_sheet, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        bc = barcode_reg.match(row['Barcode'])
        mduids[row['MDU ID']] = bc.group('barcode')

nanopore_dir = pathlib.Path(f'{nanopore_dir}', f'{runid}')
print(nanopore_dir)
# get barcode dirs
barcodes = {}
bcd = sorted(nanopore_dir.rglob('fastq_pass/barcode*'))
print('files')
print(bcd)
print(len(bcd))
# print(mduids)
for m in mduids:
    suff = mduids[m]
    print(suff)
    bc = []
    for b in bcd:
        # print(b)
        if suff in b.name:
            bc = b.name
            # break
    barcodes[m] = bc

out = ["MDU_ID,Barcode,ONT_result"]
reads = pathlib.Path(f'{mdu_reads}', f'{runid}')
print(barcodes)
print(reads)
for mdu in barcodes:
    print(barcodes[mdu])
    if barcodes[mdu]!= 'no_reads':
        out.append(f"{mdu},{barcodes[mdu]},reads_present")
        target = reads / f'{mdu}'
        cmd = f"mkdir -p {target} && gzip -c -d -f {nanopore_dir}/no_sample/*/fastq_pass/{barcodes[mdu]}/*.fastq* > {target}/{mdu}.fastq"
        print(f"Running : {cmd}")
        subprocess.run(cmd, shell = True)
         
    else:
        out.append(f"{mdu},,no_reads")
        print(f"No data found for {mdu}")
pathlib.Path(f"{runid}_nanopore.csv").write_text("\n".join(out))


