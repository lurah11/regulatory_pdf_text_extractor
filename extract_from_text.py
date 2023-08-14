import fitz
import re
import pandas as pd
import argparse

from custom_utils.utils1 import *

#untuk melakukan parsing terhadap argument yang dimasukkan user , contoh extract_from_text.py --data 'uu.pdf' -csv --output 'nama prefix untuk file'
parser = argparse.ArgumentParser("Parsing pdf digital")
parser.add_argument("--input",action="store",help="Masukkan lokasi pdf nya")
parser.add_argument("-csv",action="store_true",help="Untuk menentukan apakah hasilnya akan disimpan dalam csv atau tidak")
parser.add_argument("--namafile",action="store",help="Memberikan nama file , akan ada 2 csv yang dihasilkan yaitu namafile_pasal.csv dan namafile_ayat.csv")
args = parser.parse_args()
file_path = args.input
is_csv = args.csv
output = args.namafile 

if output : 
    filename = output 
else : 
    filename = "result"

# inisialisasi fitz object ( nama object dari pymupdf yang digunakan untuk parsing )
doc = fitz.open(file_path)


# gunakan struktur data "blocks" dan disimpan dalam list result 
result = []
for i,d in enumerate(doc):
  if i == 0 :
    result = d.get_text("blocks")
  else :
    result.extend(d.get_text("blocks"))
  


#masukkan semua langkah preprocessing , penjelasan langkah2 ini lihat di bagian utils.py
res_1 = delete_before_pasal_1(result)
res_2 = delete_penerangan_pasal(res_1)
res_3 = delete_bab(res_2)
res_4 = get_content_pasal(res_3)
pasal_list,ayat_list =construct_pasal_ayat_list(res_4)
df_pasal,df_ayat = construct_dataframe(pasal_list,ayat_list)

if is_csv: 
    df_pasal.to_csv(f"{filename}_pasal.csv",index=False)
    df_ayat.to_csv(f"{filename}_ayat.csv",index=False)
    print("Coba cek file CSV di folder yang sama")
else : 
    print("Berikut adalah dataframe dari pasal:")
    print(df_pasal)
    print("Berikut adalah dataframe dari ayat")
    print(df_ayat)