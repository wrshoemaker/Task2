from __future__ import division
import os, re
import pandas as pd
import numpy as np
from Bio import SeqIO

mydir = os.path.expanduser("~/GitHub/Task2/PoolPopSeq/data/")


def module_to_KO(strain):
    kaas_directory = mydir + 'reference_assemblies_task2/MAPLE/' + strain + '_MAPLE/KAAS'
    data = [['KEGG_Orthology', 'Pathway_ID']]
    bad_chars = '()-+,-'
    rgx = re.compile('[%s]' % bad_chars)
    for filename in os.listdir(kaas_directory):
        if filename.endswith("_matrix.txt"):
            for line in open((os.path.join(kaas_directory, filename)), 'r'):
                line_strip_split = line.strip().split()
                if len(line_strip_split) > 2 and 'M' in line_strip_split[0]:
                    if '_' in line_strip_split[0]:
                        pathway = line_strip_split[0].split('_')[0]
                    else:
                        pathway = line_strip_split[0]
                    ko_genes = line_strip_split[2:]
                    for ko_gene in ko_genes:
                        test_set_member = [bad_char for bad_char in bad_chars if bad_char in ko_gene]
                        if len(test_set_member) > 0:
                            ko_gene_clean = rgx.sub('', ko_gene)
                            ko_gene_clean_split =  ['K' + e for e in ko_gene_clean.split('K') if e]
                            for split_gene in ko_gene_clean_split:
                                if 'M' in split_gene:
                                    continue
                                data.append([split_gene, pathway])
                        else:
                            if 'K' in ko_gene:
                                data.append([ko_gene, pathway])

    df = pd.DataFrame(data[1:],columns=data[0])
    OUT_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
            + strain + '_MAPLE_modules/' + strain + '_KO_to_M.txt'
    df.to_csv(OUT_path, sep = '\t', index = False)


def clean_kaas(strain):
    IN_kaas_path = mydir + 'reference_assemblies_task2/KAAS/' + strain + '_KAAS'
    IN_kaas = pd.read_csv(IN_kaas_path, sep = '\t',
        names = ['protein_id', 'KO', 'species', 'phylum_genus', 'num'])
    IN_kaas_subset = IN_kaas.loc[IN_kaas['KO'] != 'K_NA']
    OUT_path = mydir + 'reference_assemblies_task2/KAAS/' + strain + '_KAAS_clean.txt'
    OUT = open(OUT_path, 'w')
    print>> OUT, 'protein_id', 'KEGG_Orthology', 'species', 'phylum', 'genus', 'num'
    count = 0
    for index, row in IN_kaas_subset.iterrows():
        KO_split =  row['KO'].split(',')
        phylum_genus_split =  row['phylum_genus'].strip().split('-')
        for KO in KO_split:
            if len(phylum_genus_split) == 1:
                # KEGG used 'Others' to for unknown genus
                genus = 'Others'
                if 'Other 'in phylum_genus_split[0]:
                    phylum = phylum_genus_split[0].replace(' ', '-')
                else:
                    phylum = phylum_genus_split[0].strip()
                    print>> OUT, row['protein_id'], KO, row['species'], \
                            phylum_genus_split[0].strip(), 'Others', str(int(row['num']))
            else:
                genus = phylum_genus_split[1].strip()
                phylum = phylum_genus_split[0].strip()
            print>> OUT, row['protein_id'], KO, row['species'], \
                    phylum, genus, str(int(row['num']))
            count += 1
    OUT.close()


def categorize_genes(strain):
    IN_kaas_path = mydir + 'reference_assemblies_task2/KAAS/' + strain + '_KAAS_clean.txt'
    IN_kaas = pd.read_csv(IN_kaas_path, sep = ' ', header = 0)
    #IN_kaas = IN_kaas.reset_index(drop=False)
    IN_maple_sign_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
                        + strain + '_MAPLE_modules/' + strain + '.module.signature.txt'
    IN_maple_sign = pd.read_csv(IN_maple_sign_path, sep = '\t')
    IN_maple_cmplx_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
                        + strain + '_MAPLE_modules/' + strain + '.module.complex.txt'
    IN_maple_cmplx = pd.read_csv(IN_maple_cmplx_path, sep = '\t')
    IN_maple_pthwy_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
                        + strain + '_MAPLE_modules/' + strain + '.module.pathway.txt'
    IN_maple_pthwy = pd.read_csv(IN_maple_pthwy_path, sep = '\t')
    IN_maple_fxn_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
                        + strain + '_MAPLE_modules/' + strain + '.module.function.txt'
    IN_maple_fxn = pd.read_csv(IN_maple_fxn_path, sep = '\t')

    IN_maple_fxn_MCR75 = IN_maple_fxn.loc[IN_maple_fxn['MCR % (ITR)'] > 0.75]
    IN_maple_pthwy_MCR75 = IN_maple_pthwy.loc[IN_maple_pthwy['MCR % (ITR)'] > 0.75]
    IN_maple_cmplx_MCR75 = IN_maple_cmplx.loc[IN_maple_cmplx['MCR % (ITR)'] > 0.75]
    IN_maple_sign_MCR75 = IN_maple_sign.loc[IN_maple_sign['MCR % (ITR)'] > 0.75]

    to_keep = ['Large category', 'Small category', 'ID', 'Type', 'Name(abbreviation)', 'Components #']
    IN_maple_fxn_MCR75_subset = IN_maple_fxn_MCR75[to_keep]
    IN_maple_cmplx_MCR75_subset = IN_maple_cmplx_MCR75[to_keep]
    IN_maple_pthwy_MCR75_subset = IN_maple_pthwy_MCR75[to_keep]
    IN_maple_sign_MCR75_subset = IN_maple_sign_MCR75[to_keep]
    df_list = [IN_maple_fxn_MCR75_subset, IN_maple_cmplx_MCR75_subset, \
                IN_maple_pthwy_MCR75_subset, IN_maple_sign_MCR75_subset]
    df_list1 = [IN_maple_cmplx_MCR75_subset, \
                IN_maple_pthwy_MCR75_subset, IN_maple_sign_MCR75_subset]
    df_merged = IN_maple_fxn_MCR75_subset.append(df_list1)
    df_merged.columns = ['Large_category', 'Small_category', 'Pathway_ID' , \
                    'Pathway_Type', 'Pathway_Name', 'Components_#']
    KO_to_M_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
            + strain + '_MAPLE_modules/' + strain + '_KO_to_M.txt'
    KO_to_M = pd.read_csv(KO_to_M_path, sep = '\t', header = 'infer')
    KO_M_merged = pd.merge(KO_to_M, df_merged, on='Pathway_ID', how='outer')
    KO_M_protein_merged = pd.merge(KO_M_merged, IN_kaas, on='KEGG_Orthology', how='outer')
    OUT_path = mydir + 'reference_assemblies_task2/MAPLE/MAPLE_modules/' \
            + strain + '_MAPLE_modules/' + strain + '_KO_M_protein.txt'
    KO_M_protein_merged.to_csv(OUT_path, sep = '\t', index = False)



strains = ['B', 'C', 'D', 'F', 'J', 'P']
#for strain in strains:
#    print strain
#    module_to_KO(strain)
#    clean_kaas(strain)
#    categorize_genes(strain)

#clean_kaas('P')
#module_to_KO('P')
#categorize_genes('P')