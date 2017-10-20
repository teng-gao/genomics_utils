# genomics_utils

Gene Name to ID
---------------

fillID.py: given a column of gene names, fills in a column of corresponding ensembl IDs.

Dependencies: biomart, pandas, argparse
```
Usage: python fillID.py <File name> <Column name of gene names> <Column name of gene IDs>
```
Example:

Original file: geneTable.tsv

| Gene_Name     | Gene_ID        |
| ------------- |:-------------:|
| CDC42      |  |
| HULC     |      |
| HOTAIR |      |

```
python fillID.py geneTable.tsv Gene_Name Gene_ID
```

| Gene_Name     | Gene_ID      |
| ------------- |:-------------:|
| CDC42      | ENSG00000070831 |
| HULC       |  ENSG00000251164  |
| HOTAIR     |  ENSG00000228630    |

Gene ID to Transcript ID
------------------------

fillTR.py: given a column of ensemble gene IDs, fills in a column of corresponding cononical transcript IDs.

Dependencies: biomart, pandas, argparse, multiprocessing, collections, re
```
Usage: python fillTR.py <File name> <Column name of gene IDs> <Column name of transcript IDs>
```
Original file: geneTable.tsv

| Gene_ID     | Transcript_ID   |
| ------------- |:-------------:|
| ENSG00000070831      |  |
| ENSG00000251164     |      |
| ENSG00000228630 |      |
```
python fillTR.py geneTable.tsv Gene_ID Transcript_ID
```

| Gene_ID     | Transcript_ID      |
| ------------- |:-------------:|
| ENSG00000070831      | ENST00000344548 |
| ENSG00000251164       |  ENST00000503668  |
| ENSG00000228630     |  ENST00000414790    |

Process TCGA miRNASeq isoform quantifications
---------------------------------------------
process_isoform_quantification.py: get mature miRNA sequence expression from a folder of TCGA miRNASeq isoform quantification files (in tsv format).

Dependencies: glob, pandas, argparse, multiprocessing
```
Usage: python process_isoform_quantification.py
```
