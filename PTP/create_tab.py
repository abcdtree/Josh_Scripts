import os

sample_list = ["Sample-01-X-2023",
"Sample-02-X-2023","Sample-03-X-2023",
"Sample-04-X-2022","Sample-05-X-2022",
"Sample-07-Y-2023","Sample-08-Y-2023"
]

o_path = "/home/jianszhang/UNSGM_PTP"

with open("original.tab", 'w') as mytab:
    for mid in sample_list:
        mytab.write(f"{mid}\t{o_path}/{mid}_R1.fastq.gz\t{o_path}/{mid}_R2.fastq.gz\n")

with open("with_no_human.tab", 'w') as myno:
    for mid in sample_list:
        myno.write(f"{mid}\t{o_path}/data/{mid}/no_human_reads/{mid}_R1_filtered.fastq.gz\t{o_path}/data/{mid}/no_human_reads/{mid}_R2_filtered.fastq.gz\n")
