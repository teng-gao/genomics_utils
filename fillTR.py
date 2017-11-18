import re, pandas, biomart
import argparse
from multiprocessing import Pool
from collections import defaultdict

parser = argparse.ArgumentParser(description='Get best transcript id')
parser.add_argument('in_file', type=str,
                    help='Input file')
parser.add_argument('gene_col', type=str,
                    help='column name of gene names')
parser.add_argument('TR_col', type=str,
                    help='ID column that needs to be filled in')
parser.add_argument('-thread', type=int, default=4,
                    help='Number of threads')
parser.add_argument('--gene_model_dir', type=str,
                    help='Gene model directory')

# function for finding the best TR for one gene ID
def bioMartBestTR(gene_ID):
    print("Querying: %s" % gene_ID)
    response = ensembl.search({
      'filters': {
          'ensembl_gene_id': gene_ID
      },
      'attributes': [
          'ensembl_transcript_id'
      ]
    })

    if not response.text:
        return 'nan'

    TRs = response.text.rstrip('\n').split('\n')

    response = ensembl.search({
      'filters': {
          'ensembl_transcript_id': TRs
      },
      'attributes': [
          'ensembl_transcript_id', 'transcript_tsl'
      ]
    })

    if not response.text:
        return 'nan'

    TSLs = [item.split('\t') for item in response.text.rstrip('\n').split('\n')]
    TSL_dict = dict([(TSL[0],int(TSL[1][3])) if TSL[1] != 'tslNA' else (TSL[0],6) for TSL in TSLs])

    response = ensembl.search({
      'filters': {
          'ensembl_transcript_id': TRs
      },
      'attributes': [
          'ensembl_transcript_id', 'ensembl_exon_id'
      ]
    })

    exons = [item.split('\t') for item in response.text.rstrip('\n').split('\n')]
    exon_IDs = list(set([exon[1] for exon in exons]))

    response = ensembl.search({
      'filters': {
          'ensembl_exon_id': exon_IDs
      },
      'attributes': [
          'ensembl_exon_id', 'exon_chrom_start', 'exon_chrom_end'
      ]
    })

    exon_coords = [item.split('\t') for item in response.text.rstrip('\n').split('\n')]
    exon_length_dict = dict([(exon[0] ,int(exon[2]) - int(exon[1]) + 1) for exon in exon_coords])
    TR_lengths = defaultdict(int)
    for exon in exons:
        TR_lengths[exon[0]] += exon_length_dict[exon[1]]

    TR_list = list(zip(TRs, [TSL_dict[TR] for TR in TRs], [TR_lengths[TR] for TR in TRs]))
    TR_list.sort(key = lambda x: (x[1], -x[2]))
    print("Found best TR: %s -> %s" % (gene_ID,TR_list[0][0]))
    return TR_list[0][0]

if __name__ == '__main__':
    args = parser.parse_args()

    #gene_col = "ceRNA_ID"; TR_col = "ceRNA_TR";gene_model_dir = "./Homo_sapiens.GRCh38.85.gtf";in_file = "miRsponge_filtered.csv"

    # read in arguments
    in_file = args.in_file
    gene_col = args.gene_col
    TR_col = args.TR_col
    gene_model_dir = args.gene_model_dir

    # set up ensembl server
    server = biomart.BiomartServer( "http://useast.ensembl.org/biomart" )
    ensembl = server.datasets['hsapiens_gene_ensembl']

    # read in input table
    table = pandas.read_csv(in_file)
    table[TR_col] = table[TR_col].astype(str)

    # get list of genes that needs to be filled out
    gene_list = [gene for gene in list(set(table.loc[table[TR_col].isin(['NaN', 'nan', ''])][gene_col].tolist())) if str(gene) != "nan"]

    # query for transcript metrics in paralell
    p = Pool(args.thread)
    best_TRs = p.map(bioMartBestTR, gene_list)
    TR_dict = dict(list(zip(gene_list, best_TRs)))

    # fill in empty cells in table
    for i in range(table.shape[0]):
        gene_ID = table[gene_col][i]
        if gene_ID in TR_dict.keys():
            table.at[i,TR_col] = TR_dict[gene_ID]

    # overwrite old table
    table.to_csv(in_file, index = False)
