import pandas as pd
import glob, argparse
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Process TCGA miRNASeq isoform quantification to get mature sequence expression')
parser.add_argument('-thread', type=int, default=4,
                    help='Number of threads')
parser.add_argument('-out', type=str, default="./mature_mir_exp.tsv",
                    help='output directory and filename')


if __name__ == '__main__':
    args = parser.parse_args()

    # read in all file in current folder
    original_tables_dict = {filename: pd.read_csv(filename, sep = '\t') for filename in glob.glob("*.txt")}

    # construct union of all mature miRNA accessions
    all_miRNA_IDs = list(set([mir.replace('mature,', '') for table in original_tables_dict.values() for mir in table['miRNA_region'] if 'MIMAT' in mir]))

    # Parallel
    def get_exp(file_name):
        global original_tables_dict
        print("Prcessing %s" % file_name)
        # set of miRNA IDs for this file
        file_miRNA_IDs = list(set([item.replace('mature,', '') for item in list(original_tables_dict[file_name]['miRNA_region']) if 'MIMAT' in item]))
        # expression dict for this single file
        file_miRNA_exp_dict = {}
        for miRNA_ID in all_miRNA_IDs:
            if miRNA_ID in file_miRNA_IDs:
                file_miRNA_exp_dict[miRNA_ID] = max(original_tables_dict[file_name].loc[original_tables_dict[file_name]['miRNA_region'].str.contains(miRNA_ID)]["read_count"])
            else:
                file_miRNA_exp_dict[miRNA_ID] = 0
        return (file_name, file_miRNA_exp_dict)

    p = Pool(args.thread)
    new_tables_dict = dict(p.map(get_exp, original_tables_dict.keys())) # nested dict, outer key = file name, outer value = exp dict of that file

    file_names = glob.glob("*.txt")
    df = pd.DataFrame(index = sorted(all_miRNA_IDs), columns = file_names)
    for file_name in file_names:
        df[file_name] = [new_tables_dict[file_name][mir] for mir in sorted(all_miRNA_IDs)]

    df.to_csv(args.out, index = True, sep = '\t')
