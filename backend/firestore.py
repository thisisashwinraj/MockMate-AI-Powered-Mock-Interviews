import time
import random
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore


class CandidateResumeCollection:
    def __init__(self):
        try:
            cred = credentials.Certificate("config/firebase_service_account_key.json")
            firebase_admin.initialize_app(cred)
        except: pass

        self.db = firestore.client(database_id='junefirestore')


    def store_candidate_resume_details(self, username, resume_summary, resume_url):
        try:
            resume_details = {
                "resume_summary": resume_summary, 
                "resume_url": resume_url
            }

            self.db.collection(username).document("resume").set(resume_details)
            return True

        except Exception as error:
            return False
    

    def fetch_candidate_resume_details(self, username):
        try:
            data = self.db.collection(username).document("resume").get(['resume_summary', 'resume_url'])
            return data.to_dict()

        except Exception as error:
            return False

    
    def update_candidate_resume_details(self, username, updated_resume_summary, updated_resume_url):
        try:
            resume_detals_ref = self.db.collection(username).document("resume")
            
            resume_detals_ref.update({
                "resume_summary": updated_resume_summary,
                "resume_url": updated_resume_url,
            })

            return True

        except Exception as error:
            return error



class InterviewCollection:
    def __init__(self):
        try:
            cred = credentials.Certificate("config/firebase_service_account_key.json")
            firebase_admin.initialize_app(cred)
        except: pass

        self.db = firestore.client(database_id='junefirestore')


    def store_candidate_interview_transcript(self, username, interview_type, interview_id, interview_transcript, job_title, interview_date, language, number_of_questions, difficulty):
        try:
            interview_transcript = {
                "interview_transcript": interview_transcript
            }

            self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).set(interview_transcript)

            interview_configs = {
                'job_title': job_title,
                'interview_date': interview_date,
                'language': language,
                'number_of_questions': number_of_questions,
                'difficulty': difficulty,
            }

            self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).update(interview_configs)
            return True

        except Exception as error:
            print(error)


    def store_candidate_overall_interview_analysis(self, username, interview_type, interview_id, overall_interview_analysis):
        try:
            overall_interview_analysis = {
                "overall_interview_analysis": overall_interview_analysis
            }

            self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).update(overall_interview_analysis)
            return True

        except Exception as error:
            print(error)

    
    def store_candidate_question_by_question_analysis(self, username, interview_type, interview_id, question_by_question_analysis):
        try:
            question_by_question_analysis = {
                "question_by_question_analysis": question_by_question_analysis
            }
            
            self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).update(question_by_question_analysis)
            return True

        except Exception as error:
            return False


    def fetch_interview_configs(self, username, interview_type, interview_id):
        try:
            interview_transcript = self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).get(['difficulty', 'language', 'number_of_questions'])
            result = interview_transcript.to_dict()
            return result['difficulty'], result['language'], result['number_of_questions']

        except Exception as error:
            return False


    def fetch_interview_date_and_role(self, username, interview_type, interview_id):
        try:
            interview_transcript = self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).get(['interview_date', 'job_title'])
            result = interview_transcript.to_dict()
            return result['interview_date'], result['job_title']

        except Exception as error:
            return False

        
    def fetch_candidate_interview_transcript(self, username, interview_type, interview_id):
        try:
            interview_transcript = self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).get(['interview_transcript'])
            result = interview_transcript.to_dict()
            return result['interview_transcript']

        except Exception as error:
            return False


    def fetch_candidate_overall_interview_analysis(self, username, interview_type, interview_id):
        try:
            overall_interview_analysis = self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).get(['overall_interview_analysis'])
            result = overall_interview_analysis.to_dict()
            return result['overall_interview_analysis']

        except Exception as error:
            return False

    
    def fetch_candidate_question_by_question_analysis(self, username, interview_type, interview_id):
        try:
            question_by_question_analysis = self.db.collection(username).document('interviews').collection(interview_type).document(interview_id).get(['question_by_question_analysis'])
            result = question_by_question_analysis.to_dict()
            return result['question_by_question_analysis']

        except Exception as error:
            return error


    def fetch_all_interview_ids_by_username(self, username, interview_type):
        try:
            docs = self.db.collection(username).document('interviews').collection(interview_type).stream()
            document_ids = [doc.id for doc in docs]

            return document_ids
        
        except Exception as error:
            return error



if __name__ == "__main__":
    candidate_resume_collection = CandidateResumeCollection()
    #print(candidate_resume_collection.store_candidate_resume_details('amritharaj', "This is a resume summary", "This is a resume url"))
    #print(candidate_resume_collection.fetch_candidate_resume_details('amritharaj'))
    #print(candidate_resume_collection.update_candidate_resume_details('amritharaj', "This is updated resume summary", "This is updated resume url"))

    interview_collection = InterviewCollection()
    #print(interview_collection.fetch_candidate_interview_transcript('amritharaj', 'tech_interview', '12345'))
    #print(interview_collection.fetch_candidate_overall_interview_analysis('amritharaj', 'technical_interview',  '1734458314'))
    #print(interview_collection.fetch_candidate_question_by_question_analysis('amritharaj', 'tech_interview', '12345'))

    print(interview_collection.fetch_interview_date_and_role('amritharaj', 'technical_interview', '1734458314'))

