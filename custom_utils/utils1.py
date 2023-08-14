import pandas as pd
import re

# Menghapus semua konten sebelum pasal 1 
def delete_before_pasal_1(result):
  for i,res in enumerate(result) :
    if "Pasal 1\n" in res[4]:
      return result[i:]

# Menghapus bagian PASAL DEMI PASAL setelah bagian pasal utama
def delete_penerangan_pasal(result):
  for i,res in enumerate(result):
    if "PASAL DEMI PASAL" in res[4]:
      return result[:i]

# Menghapus bagian BAB 
def delete_bab(result):
  final_res = []
  pat1 = "BAB [IVX]+"
  pat2 = "\s*[A-Z]{3,}"
  for i,res in enumerate(result):
    if i == len(result)-1 :
      break
    elif i == 0 :
      final_res.append(res)
    else:
      match_bab = re.match(pat1,res[4])
      match_bab_prev = re.match(pat1,result[i-1][4])
      match_bab_title = re.match(pat2,res[4])
      match_bab_2_prev = re.match(pat1,result[i-2][4])
      if match_bab or (match_bab_title and (match_bab_prev or match_bab_2_prev)) :
        continue
      else :
        final_res.append(res)
  return final_res

# Mendapatkan bagian konten utama dari pasal , masih dalam bentuk dictionary 
def get_content_pasal(result):
  final_result = []
  begin_pasal = "Pasal \d+\n"
  x_left = 270
  x_right = 450
  begin_ayat = "\(\d+\)"
  end_ayat = "\.\n"
  end_pasal_utama = "Disahkan di "
  i = 0
  final_res = []
  pasal_dict = {}
  ayat = ""

  ongoing_match = False
  pasal = ""

  for res in result :
    if i == len(result)-1:
      break
    curr_val = result[i][4]
    next_val = result[i+1][4]
    i += 1
    if ongoing_match :
        match_end_ayat = re.search(end_ayat,curr_val)
        match_end_pasal = re.search(begin_pasal,next_val)
        match_end_pasal_utama = re.search(end_pasal_utama,next_val)
        match_begin_ayat_next = re.match(begin_ayat,next_val)
        if match_end_ayat and match_begin_ayat_next:
          ayat += curr_val
          pasal_dict[pasal].append(ayat)
          ayat = ""
        else :
          ayat += curr_val
        if match_end_pasal or match_end_pasal_utama :
          pasal_dict[pasal].append(ayat)
          ayat = ""
          ongoing_match = False
          final_res.append(pasal_dict)
          pasal_dict = {}
          continue
    else :
        match_pasal = re.match(begin_pasal,curr_val)
        if match_pasal :
          pasal = match_pasal.group(0)
          pasal = pasal.replace("\n","")
          pasal_dict[pasal] = []
          ongoing_match = True
          ayat = ""

  return final_res

# Membuat list pasal dan list ayat yang lebih rapih dan siap dijadikan dataframe
def construct_pasal_ayat_list(result):
  pasal_list = []
  ayat_list = []
  temp_pasal = []
  for i,res in enumerate(result):
    no_pasal = list(res.items())[0][0]
    temp_pasal.append(i)
    temp_pasal.append(no_pasal)
    pasal_list.append(temp_pasal)
    temp_ayat = []
    for key,val in res.items():
      temp_ayat.append(i)
      temp_ayat.extend(val)
      ayat_list.append(temp_ayat)
      temp_ayat = []
    temp_pasal = []
  return pasal_list,ayat_list

# Membuat dataframe dari list pasal dan ayat
def construct_dataframe(pasal_list,ayat_list): 
  final_list = []
  index_counter = 0 
  pat_no_ayat = "\((\d+)\)"
  for ayat in ayat_list : 
    temp_list = []
    for i in range(len(ayat[1:])): 
      index_counter +=1 
      content = ayat[i+1].replace("\n","\t")
      matched = re.match(pat_no_ayat,content)
      if matched : 
        no_ayat = matched.group(1)
      else : 
        no_ayat = 0 
      content = re.sub(pat_no_ayat,"",content)
      content = content.strip()
      temp_list.append([index_counter,ayat[0],no_ayat,content])
    final_list.extend(temp_list)
    
  df_pasal = pd.DataFrame(pasal_list,columns=["id","pasal"])
  df_ayat = pd.DataFrame(final_list, columns=["ayat_id","pasal_id","no_ayat","content"])
  return df_pasal,df_ayat