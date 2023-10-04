# Josh_Scripts

## a summary of all scripts developed in MDU PHL

- ChatGPT
  mdu_chatgpt.py (mdu_gpt)-- a trial app with free api from chatGPT (*free plan end --need to buy a plan*)

- CIVET
  - build_db.py -- create a consensus db for CIVET HAV analysis
  - create_civet_command.py -- output civet command
  - create_consensus.py -- **good command to create consensus for short sequence against with reference**
  - civet.yml -- conda yml file for civet environment

- compare_pipeline
  - mdu_compare.py -- using old version of bohra to compare two samples *use listeria conda env to run*
  - listeria.yml -- **conda env for old bohra and mdu-listeria**

- CPA_report -- some CPA report draft/template

- emmtyper
  - run_emm.py -- a command to run emmtyper with a list of contigs as input

- Genome_SIZE_research -- research scripts and tables on genome size threshold

- HAV -- scripts for HAV report
  - get_new_samples.py -- rename the tree leaves and get the new sample list for each serotype
  - hav_analysis.py -- **blastn analyis on HAV new samples and build the tree for each serotype**
  - hav_genotype.py -- typing hav sequences
  - hav_plot.r -- plot hav master tree and subtree with ggtree
  - QLD_hav.py -- clean up seqs shared from Queensland
  - hav.yml -- **conda environment to run HAV analysis**

- josh_cluster -- **a hierarchical clustering method with input matrix from Bohra**
  - josh_cluster.py -- **clustering script**
  - josh_pca.py -- **PCA plot and clustering**
  - LS_reporting.yml -- **conda environment with scikit-learn package**

- KMCP
  - mdu-kmcp-search.py -- **run KMCP on mdu servers**
  - result_summary.py -- summary results from KMCP
  - kmcp.yml -- **conda environment to run KMCP**

- kraken_db_download
  - db_download.py -- download fasta file with id
  - db_download.yml -- conda environment with efetch/esearch

- MTB -- **MTB report scripts**
  - add_PHESS.py -- add PHESS ID to amr table
  - make_change.py -- make change in the MTB cluster db
  - merge_cluster_db.py -- merge cluster names for different lineages
  - mtb_new_process.py -- cleptr analysis
  - MTB_new_report.py -- create report tree/files/pngs
  - remove_dup.py -- remove duplicates in MTB cluster db
  - remove_samples.py -- remove samples from MTB cluster db
  - templete_fit.py -- create doc report
  - MTB_reporting.yml -- conda environment for MTB_new_report.py and templete_fit.py

- nextflow_clean (**Danger**)
  - nextflow_clean.py -- clean up large files in nextflow folder **Do not use this -- will crush servers**

- ONT_research
  - mdu-ont.py -- same as `mdu ont`

- PTP -- scripts for Monkey pox virus PTP
  - create_consensus.py -- create consensus with reference
  - reads_stats.py -- **filter species/domain/human reads in metagenomics seqs using kraken2 and taxonkit**
  - run_abricate.py -- run abricate on reads
  - sep_ref.py -- break large refs to single contigs fasta

- salmonella
  - salmonella_report.py -- Original STE reporting code

- scripts -- collection of quick scripts
  - bad_symlink_cleaner.py -- clean up bad symlinks
  - copy_contigs_for_mashtree.py -- copy/symlink contigs for input of mashtree
  - cp_share.py -- copy reads for `mdu share`
  - find_the_close_samples.py -- **very useful to list number of samples to include in bohra analysis. need pandas in envronment**
  - json_to_csv.py -- quick tools to transfer json files to csv
  - nwktojson.py -- quick tools to transfer nwk files to json
  - remove_samples_from_cgmlst.py -- **remove samples from cgmlst db to rerun qc finalise step (with cgmlst)**
  - sra_download.py -- **download reads with SRA ids from NCBI**
  - which_run.py -- **search mdu id in the /home/mdu/instruments/**

- Shigella
  - create_shigs_input.py -- create input files for mdu_shigs.py
  - create_sonnei_summary.py -- create report summary
  - mdu_mykrobe.py -- run mykrobe
  - mdu_shigs.py -- shigella analysis with input from `create_shigs_input.py`
  - shigella.yml -- conda environment to run `mdu_shigs.py`
  - Sonnei_tree.Rmd -- R Markdown to build sonnei trees
  - sonneityping_with_shigs.py -- typing with shigs results

- SKA
  - run_ska.py -- **run SKA with a tab file as input**

- STE_report
  - cgT_db.py -- checking cgT db
  - STE_summary.py -- create summary on recent cgTs
  - run_bohra.py -- **run bohra analysis on each cgTs**
  - cp_bohra_links.py -- **publish bohra links**

- streptyping -- Strep pnemo typing with shore seqs
  - mdu-streptyping.py -- **typing Strep pnemo using blastn (fasta as input)**
  - strep_consensus.py -- **create consensus for typing**


##Author Jianshu Zhang
##Email: josh.zhang@unimelb.edu.au / zjs0317@gmail.com 
