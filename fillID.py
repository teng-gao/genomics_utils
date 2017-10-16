import biomart
import pandas
import argparse

parser = argparse.ArgumentParser(description='Get ensembl id')
parser.add_argument('inFile', type=str,
                    help='Input file')
parser.add_argument('nameCol', type=str,
                    help='column name of gene names')
parser.add_argument('IDCol', type=str,
                    help='ID column that needs to be filled in')


if __name__ == '__main__':
    args = parser.parse_args()

    inFile = args.inFile
    nameCol = args.nameCol
    IDCol = args.IDCol
    # set up ensembl server
    server = biomart.BiomartServer( "http://useast.ensembl.org/biomart" )
    ensembl = server.datasets['hsapiens_gene_ensembl']
    # read in table
    table = pandas.read_csv(inFile)
    table[IDCol] = table[IDCol].astype(str)
    # get list of genes that need to be filled in
    gene_list = list(set([name.upper() for name in table.loc[table[IDCol].isin(['NaN', 'nan', ''])][nameCol].tolist()]))
    # query ensembl for ID
    response = ensembl.search({
      'filters': {
          'external_gene_name': gene_list
      },
      'attributes': [
          'external_gene_name', 'ensembl_gene_id'
      ]
    })

    if response.text:
        id_list = response.text.rstrip("\n").split("\n")
        id_dict = dict([id.split('\t') for id in id_list])
        # fill in empty cells with ID
        for i in range(table.shape[0]):
            geneName = table[nameCol][i].upper()
            table.at[i,nameCol] = geneName
            if geneName in id_dict.keys():
                table.at[i,IDCol] = id_dict[geneName]
        # overwrite old table
        table.to_csv(inFile, index = False)
    else:
        print("Nothing I can fill!")
