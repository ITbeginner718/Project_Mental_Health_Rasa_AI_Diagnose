# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from rasa.shared.core.events import ActiveLoop


import sys
import os
import yaml
import actions.function as function


# 현재 파일의 디렉토리 경로를 얻기(절대 경로)
current_dir = os.path.dirname("..\\actions")

# 현재 디렉토리의 상위 디렉토리 경로를 얻기
parent_dir = os.path.dirname(current_dir)

# YAML 파일 로드(진단 쿼리)
with open('actions\\diagnose_query.yml', 'r', encoding='utf-8') as file:
    yaml_diagnose_query_data = yaml.safe_load(file)


# 상위 디렉토리 경로를 sys.path 에 추가
sys.path.append(parent_dir)

import function.func as func

# 우울증 진단 결과 배열 선언
diagnose_response = [] 

REQUEST = "request"
RESPONSE_NUMBER = "response_number"
RESPONSE_TEXT = "response_text"
RESULT = "result"       


# 처음 시작 인삿말
class ActionStartDiagnose(Action):
    def name(self):
        return "action_start_diagnose"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # 사용자 이름
        username = tracker.get_slot('username')
        
        parts = [
            "안녕하세요 AI 챗봇 마음이이에요.",
            "지금부터 몇 가지 질문을 드릴께요. 편안한 마음으로 솔직하게 답변 해주시면 됩니다. ",
            "첫 번째 질문입니다.",]

        # # 1. 사용자 질의 가져오기 
        # uesrMessage=tracker.latest_message.get('text')
        # print(f"Received Message:{uesrMessage}")

        # 각 부분을 순차적으로 전송
        print(f"Send Message to NodeJs:")
        for part in parts:
            print(part)
            dispatcher.utter_message(text=part)
        
        firstQuery = yaml_diagnose_query_data['diagnose_query']['0']
        
        message= f"{username}님은 {firstQuery}"

        dispatcher.utter_message(text=message)

        # 저장할 진단 데이터 전송(질의)
        message= f"{REQUEST}\n{firstQuery}\n{0}"
        dispatcher.utter_message(text=message)  

        # 진단 질의 응답 배열 초기화
        diagnose_response.clear()   

        # 진단 질문 수 및 리스트 슬롯 초기화 
        return [SlotSet("count", int(0)), SlotSet("diagnoseResponseNumberList", None)]

# 진단 검사 슬롯 검증(diagnoseResponseNumberList) 함수
class ValidateDiagnoseForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_diagnose_form"
    
    #이거 완전 중요함 해당 슬롯에 대한 검증을 할 때는
    #함수명을  validate_{slot_name} 이렇게 해야함
    def validate_diagnoseResponseNumberList(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate diagnoseResponseNumberList value."""
    
        #사용자 입력 값 가져오기    
        slot_value=str(slot_value)
        print("solt_value:", slot_value)

        isQuitText=slot_value

        if(isQuitText == "['진단검사중지']"):
            print("diagnoseForm중지")
            return [{"count": int(0) , "diagnoseResponseNumberList": None}, ActiveLoop(None)]

        # 진단 질의 질문 수
        count = tracker.get_slot('count')
        
        # 사용자 이름
        username = tracker.get_slot('username')

        print("진단 검사 질문 수:", int(count)+1)

        try:
            # 텍스트 사용자 
            query_response_text = slot_value

            # replace 함수를 이용해서 공백 제거
            uesrMessage = slot_value.replace(" " ,"")

            # 2. 사용자 데이터 수치화 
            query_response_keyword = function.get_query_response_Keyword(uesrMessage)

            # 예외 처리(이상한 텍스트 들어왔을 때)
            # 질병 키워드 있는지 확인
            if query_response_keyword is not None:
                # 아니다 0
                if(query_response_keyword==0):
                    query_response_number=str(query_response_keyword)
                   
                    print("아니다: 0")

                # 가끔 1
                elif(query_response_keyword==1):
                    query_response_number=str(query_response_keyword)
                    print("가끔 그렇다: 1")

                # 종종 2
                elif(query_response_keyword==2):
                    query_response_number=str(query_response_keyword)
                    print("종종 그렇다: 2")

                # 자주 3
                elif(query_response_keyword==3):
                    query_response_number=str(query_response_keyword)
                    print("자주 항상 그렇다: 3")

                diagnose_response.append(query_response_number)
                
                # 진단 저장 데이터 전송(응답_점수)
                message= f"{RESPONSE_NUMBER}\n{query_response_number}\n{count}"
                dispatcher.utter_message(text=message)
                
                # 진단 저장 데이터 전송(응답_텍스트)
                message= f"{RESPONSE_TEXT}\n{query_response_text}\n{count}"
                dispatcher.utter_message(text=message)

            else:
                # 아무것도 없다면
                message="죄송해요 제가 파악하지 못했어요ㅠ 조금 더 정확한 표현을 해주세요.."
                dispatcher.utter_message(text=message)
                return{"diagnoseResponseNumberList": None}
            
        except Exception as e:  
            print("에러 발생:", e)
            return{"diagnoseResponseNumberList": None}

        # # 1. 사용자 질의 가져오기 
        # uesrMessage=tracker.latest_message.get('text')
        
        # diagnose_response 길이가 10 이라면 
        print("응답 배열 길이:", len(diagnose_response))   

        try:
            # 질의 데이터 수 구하기
            query_count = 0
            for key in yaml_diagnose_query_data['diagnose_query'].items():
                 query_count = query_count+(len(key)-1)
                 

            if(len(diagnose_response)>=query_count):
                message="수고 했어요! 잠시만 기달려주세요. 곧 결과가 나와요!"
                dispatcher.utter_message(text=message)

            
            print("질의 데이터 수:", query_count) 
            # 배열 수가 채워지면 슬롯 값 등록 
            # 이거 꼭 바꾸기 
            if(len(diagnose_response)>=query_count):
                print("배열:", len(diagnose_response))
                # 슬롯 배열 등록
                return {"diagnoseResponseNumberList": diagnose_response}
            
            else:

                # 다음 질문 실행 
                count = str(int(count) + 1)
                
                # 마지막 질문
                if(int(count) == query_count-1):
                    dispatcher.utter_message(text="이제 마지막 질문이에요")
                
                # 진단 쿼리 yml파일 
                message = yaml_diagnose_query_data['diagnose_query'][str(count)]

                
                print("다음 질문 실행:", message)
                
                messageQuery=f"{username}님은 {message}"      
                dispatcher.utter_message(text=messageQuery)

                # 진단 저장 데이터 전송(질의)
                message= f"{REQUEST}\n{message}\n{count}"
                dispatcher.utter_message(text=message)

                return {"count": count , "diagnoseResponseNumberList": None}
            
        except Exception as e:
            print("에러 발생:", e)
            return {"diagnoseResponseNumberList": None}  # 에러 발생 시 빈 리스트 반환


# 진단 검사 결과
class ActionDiagnoseResult(Action):

  def name(self) -> Text:
      return "action_diagnose_result"

  async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
  ) -> List[Dict[Text, Any]]:
        
        result_number = 0

        # 진단 질의 질문 수
        username = tracker.get_slot('username')

        # custom behavior
        diagnose_result= tracker.get_slot('diagnoseResponseNumberList')
        

        # 예외 처리: 갑자기 중단된 경우( form 종료 )
        if(diagnose_result[0]=="진단검사중지"):
            print("폼 종료")        
            return[]
        
        for i in range(len(diagnose_result)):
            result_number = result_number + int(diagnose_result[i])    
            print(diagnose_result[i])

        # 최종 결과
        # 정상
        if(result_number < 10 ):
            result_text = "양호"
            message_feedback = f" 현재 {username}님의 우울증 상태는 대체적으로 좋습니다."
        elif(result_number >= 11 and result_number <= 22):
            result_text = "보통"
            message_feedback = f" 다행이도 현재 {username}님의 상태는 보통 상태으로 걱정할 상태는 아니에요."
        elif(result_number >=23 and result_number <= 34):   
            result_text = "경증" 
            message_feedback = f" 현재 {username}님의 상태는 약간의 우울감이 있는 수준입니다."    
        elif (result_number>35):
            message_feedback = f" 안타깝께도 {username}님의 상태는 우울증이 의심 되는 수준이에요ㅠ"  
            result_text = "심각"  
        
        message_result = f"우울증 진단 검사 결과: {result_number} 점으로 \'{result_text}\'으로 판단됩니다."
        
        dispatcher.utter_message(text=message_result)
        dispatcher.utter_message(text=message_feedback)


        # 저장할 진단 데이터 전송(결과)
        message= f"{RESULT}\n{result_number}\n{result_text}"
        dispatcher.utter_message(text=message)  
    
        # 배열 초기화
        diagnose_response.clear()

        # 슬롯 초기화 진단 리스트, 숫자
        return [SlotSet("diagnoseResponseNumberList", []), SlotSet("count",None)]

# 진단 중단 
# 처음 시작 인삿말
class ActionQuitDiagnose(Action):
    def name(self):
        return "action_quit_diagnose"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # 진단 질의 질문 수

        print("진단 중지 함수")

        # 배열 초기화
        diagnose_response.clear()

        # 슬롯 초기화 진단 리스트, 숫자
        return [SlotSet("diagnoseResponseNumberList", None), SlotSet("count",int(0))]
       
        # message = f"{cuisine} {number}인분 나왔다 우리 맛있게 먹자!"
        # dispatcher.utter_message(text=message)

        # return [SlotSet("cuisine", None), SlotSet("number",None)]
  

        
# class ValidateRestaurantForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_sample_form"

#     @staticmethod
#     def cuisine_db() -> List[Text]:
#         """Database of supported cuisines"""

#         return ["김치찌개", "보쌈", "삼겹살"]

#     #이거 완전 중요함 해당 슬롯에 대한 검증을 할 때는
#     #함수명을  validate_{slot_name} 이렇게 해야함
#     def validate_cuisine(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate cuisine value."""
#         slot_value=str(slot_value)

#         if slot_value.lower() in self.cuisine_db():
#             # validation succeeded, set the value of the "cuisine" slot to value
#             message = f"{slot_value} 좋았어"
#             dispatcher.utter_message(text=message)
#             return {"cuisine": slot_value}
        
#         else:
#             # validation failed, set this slot to None so that the
#             message=f"뭐~어~!? {slot_value}~? 다른거~"
#             dispatcher.utter_message(text=message)
#             return {"cuisine": None}

#     def validate_number(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,)-> Dict[Text, Any]:

#         """Validate cuisine value."""

#         slot_value= func.extractNumber(slot_value)
#         slot_value= int(slot_value)

#         print(slot_value)

#         if slot_value<3:
#             # validation succeeded, set the value of the "cuisine" slot to value
#             dispatcher.utter_message(text="좋아 딱 그 정도가 좋아")
#             return {"number": slot_value}
#         else:
#             # validation failed, set this slot to None so that the
#             message=f"{slot_value}인분? 안돼 너무 많아.. "
#             dispatcher.utter_message(text=message)
#             return {"number": None}

# class ActionRestart(Action):

#   def name(self) -> Text:
#       return "action_orderFood"

#   async def run(
#       self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#   ) -> List[Dict[Text, Any]]:


#         # custom behavior
#         cuisine= tracker.get_slot('cuisine')
#         number= tracker.get_slot('number')

#         print(number)

#         message = f"{cuisine} {number}인분 나왔다 우리 맛있게 먹자!"
#         dispatcher.utter_message(text=message)

#         return [SlotSet("cuisine", None), SlotSet("number",None)]

# class ActionRestart2(Action):

#   def name(self) -> Text:
#       return "action_reason_number"

#   async def run(
#       self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#   ) -> List[Dict[Text, Any]]:


#         # custom behavior

#         number_local= tracker.get_slot('number_local')
#         cuisine= tracker.get_slot('cuisine')

#         number_local= func.extractNumber(number_local)

#         message = f"야! 뭔소리야! 나 원래 조금 먹거든?;; {cuisine} {number_local}인분은 너무 많아!"
#         dispatcher.utter_message(text=message)

#         return []
