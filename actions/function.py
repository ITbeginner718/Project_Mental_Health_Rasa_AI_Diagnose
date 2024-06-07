
word_qeury_response_list = [
    #0
    ["전혀", "아니","들지않아","적없어","그렇지않아","그렇진않아","없는것", "아니", "안그래", "안들어","거의","절대","못느꼈어","못느낀것같아","생각안해","그정도는아니야","그런생각은안"],
    #1
    [ "때로는","때때로","때로","때때로","가끔", "한달에한번", "한번씩","어쩌다","몇번","약간"],
    #2
    ["자주", "자꾸", "거의","종종" ,"요즘","어느정도"],
    #3
    ["항상", "매일", "맨날", "시도때도", "날마다",  "계속","한날이없어","그치","당연하지","주기적"],  
]   


response_number=[0, 1, 2, 3]


# 데이터 수치화
def get_query_response_Keyword(strInput):
  
  query_response_keyword = None

  # 단어 체크
  for index, word_list in enumerate(word_qeury_response_list):
      for word in word_list:
          if word in strInput:
            query_response_keyword=response_number[index]
            
  if query_response_keyword is None:
    return None
  
  else:
    keyword = query_response_keyword
    return keyword
  