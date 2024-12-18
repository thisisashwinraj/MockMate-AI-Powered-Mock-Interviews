import os
import time
import datetime
import json
import requests

import streamlit as st
import streamlit_antd_components as sac

import firebase_admin
from firebase_admin import auth, credentials

from google import genai
from google.genai import types

import genai_engine
from backend.cloud_storage import CandidateResumesBucket
from backend.firestore import CandidateResumeCollection, InterviewCollection



st.set_page_config(
    page_title="MockMate",
    page_icon="assets/favicon/logiq_favicon.png",
    initial_sidebar_state="expanded",
    layout="wide",
)


st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0.1rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)

st.markdown(
    """
        <style>
               .h1-ir-1 {
                    padding-top: 0.1rem;
                    padding-bottom: 1.75rem;
                }
                .p-ir-1 {
                    margin-bottom: 0.2rem;
                }
        </style>
    """,
    unsafe_allow_html=True,
)


if "username"not in st.session_state:
    st.session_state.username = None

if "cache_job_title" not in st.session_state:
    st.session_state.cache_job_title = None

if "cache_resume_details" not in st.session_state:
    st.session_state.cache_resume_details = None

if "cache_job_description" not in st.session_state:
    st.session_state.cache_job_description = None

if "cache_interview_type" not in st.session_state:
    st.session_state.cache_interview_type = None

if "cache_number_of_questions" not in st.session_state:
    st.session_state.cache_number_of_questions = None

if "cache_difficulty_level" not in st.session_state:
    st.session_state.cache_difficulty_level = None

if "cache_interview_language" not in st.session_state:
    st.session_state.cache_interview_language = None

if "cache_display_chat_interface" not in st.session_state:
    st.session_state.cache_display_chat_interface = False


def set_cache_display_chat_interface_to_true():
    st.session_state.cache_display_chat_interface = True

def set_cache_display_chat_interface_to_false():
    st.session_state.cache_display_chat_interface = False


@st.dialog('Create New Account', width='large')
def create_account():
    with st.form("_form_create_account", border=False, clear_on_submit=False):
        signup_form_section_1, signup_form_section_2 = st.columns(2)

        with signup_form_section_1:
            name = st.text_input(
                "Enter your Full Name:",
            )
            email = st.text_input(
                "Enter your E-Mail Id:",
            )

        with signup_form_section_2:
            username = st.text_input(
                "Enter your Username:",
                placeholder="Allowed characters: A-Z, 0-9, . & _",
            )
            phone_number = st.text_input(
                "Enter Phone Number:",
                placeholder="Include your Country Code (eg: +91)",
            )

        password = st.text_input(
            "Enter your Password:",
            type="password",
        )

        accept_terms_and_conditions = st.checkbox(
            "By creating an account, you confirm your acceptance to our Terms of Use and the Privacy Policy"
        )

        button_section_1, button_section_2, button_section_3 = st.columns(3)

        with button_section_1:
            button_submit_create_account = st.form_submit_button(
                "Create New Account", use_container_width=True
            )
        
        if button_submit_create_account:
            try:
                if not name:
                    st.warning("Please enter your full name")

                elif not email:
                    st.warning("Please enter your email id")

                elif not username:
                    st.warning("Please enter your username")

                elif not phone_number:
                    st.warning("Please enter your phone number")
                
                elif not password:
                    st.warning("Please enter your password")
                
                elif not accept_terms_and_conditions:
                    st.warning("Please accept our terms of use")

                else:
                    firebase_admin.auth.create_user(
                        uid=username.lower(),
                        display_name=name,
                        email=email,
                        phone_number=phone_number,
                        password=password,
                    )

                    alert_successful_account_creation = st.success(
                        "Your Account has been created successfully"
                    )

                    time.sleep(3)
                    alert_successful_account_creation.empty()

            except Exception as error:
                st.warning(error)


@st.dialog('Interview Report', width='large')
def view_interview_report(interview_type, interview_id):
    interview_collection = InterviewCollection()
    overall_interview_analysis = interview_collection.fetch_candidate_overall_interview_analysis(
        st.session_state.username, 
        interview_type, 
        interview_id
    )

    difficulty, language, number_of_questions = interview_collection.fetch_interview_configs(
        st.session_state.username, 
        interview_type, 
        interview_id
    )

    overall_interview_analysis = json.loads(overall_interview_analysis)

    if interview_type == 'technical_interview':
        interview_type_arg = 'Technical'
    elif interview_type == 'behavioural interview':
        interview_type_arg = 'Behavioural'
    else:
        interview_type_arg = 'Overall'

    st.markdown("""<P class="p-ir-1">December 12, 2024<BR></P><H1 class="h1-ir-1">Mock Interview for Consultant Role</H1>""", unsafe_allow_html=True)
    st.markdown(f"<B>Interview Type:</B> {interview_type_arg} &nbsp;&nbsp;&nbsp; <B>Difficulty:</B> {difficulty} &nbsp;&nbsp;&nbsp; <B>Language:</B> {language} &nbsp;&nbsp;&nbsp; <B>Number of Questions:</B> {number_of_questions}", unsafe_allow_html=True)

    st.write(" ")
    selected_tab = sac.tabs([
        sac.TabsItem(label='Interview Summary'),
        sac.TabsItem(label='Performance Analysis'),
        sac.TabsItem(label='Ques-by-Ques Analysis'),
    ], variant='outline')

    if selected_tab == "Interview Summary":
        cola, colb = st.columns([1, 2])
        with cola:
            st.markdown(f"**Overall Score:** {overall_interview_analysis['overall_interview_score']}")
        with colb:
            st.markdown(f"<P align='right'><B>Chances of Clearing:</B> {overall_interview_analysis['selection_probability'].capitalize()}&nbsp;</P>", unsafe_allow_html=True)

        st.markdown(overall_interview_analysis['report_snapshot'])

    elif selected_tab == "Performance Analysis":
        st.markdown(overall_interview_analysis['performance_analysis_brief'])

        st.markdown("<H4>Strengths Displayed</H4>", unsafe_allow_html=True)
        st.markdown(overall_interview_analysis['candidates_strengths'])
        st.markdown(f"<B>Skills: </B>{overall_interview_analysis['strong_skills']}", unsafe_allow_html=True)

        st.markdown("<H4>Comparitative Analysis</H4>", unsafe_allow_html=True)
        st.markdown(overall_interview_analysis['comparitive_analysis'])

        st.markdown("<H4>Quantitative Analysis</H4>", unsafe_allow_html=True)
        st.markdown(overall_interview_analysis['quantitative_analysis'])
        st.markdown(f"<B>Areas of Weakness: </B>{overall_interview_analysis['skill_gaps']}", unsafe_allow_html=True)

        st.markdown("<H4>Qualitative Analysis</H4>", unsafe_allow_html=True)
        st.markdown(overall_interview_analysis['qualitative_analysis'])

        st.markdown("<H4>Cultural Fit</H4>", unsafe_allow_html=True)
        st.markdown(overall_interview_analysis['cultural_fit'])

        st.markdown("<H4>Final Remarks</H4>", unsafe_allow_html=True)
        st.markdown(overall_interview_analysis['final_remarks'])

    else:
        ques_by_ques_analysis = interview_collection.fetch_candidate_question_by_question_analysis(
            st.session_state.username,
            interview_type,
            interview_id,
        )
        st.markdown("## Question by Question Analysis")

        st.markdown(ques_by_ques_analysis)


@st.dialog('Configure Your Interview', width='large')
def configure_interview_options():
    cola, colb = st.columns(2)

    with cola:
        st.session_state.cache_interview_type = st.selectbox(
            "Interview Type", 
            ['Technical Interview', 'Behavioural Interview', 'Overall Evaluation'], 
            placeholder='Interview Type', 
        )

        st.session_state.cache_difficulty_level = st.selectbox(
            "Difficulty Level",
            options=['Beginner ', 'Intermediate ', 'Experienced', 'Expert'],
            index=1,
        )

    with colb:
        st.session_state.cache_number_of_questions = st.number_input(
            "Number of Questions",
            placeholder='Number of Questions', 
            min_value=5,
            max_value=15
        )

        st.session_state.cache_interview_language = st.selectbox(
            "Language for Interview",
            options=['English ', 'Hindi ', 'French'],
        )

    user_resume = st.file_uploader("Upload your resume", type=['pdf'], accept_multiple_files=False)

    cola, colb, _ = st.columns([5, 0.9, 6])

    with cola:
        if st.button("💾 Save Settings", use_container_width=True):
            # TODO: Change local storage to cloud storage for resume reuse
            try:
                user_resume_filename = user_resume.name

                local_file_path = os.path.join(
                    "temp", user_resume_filename
                )

                try:
                    with open(local_file_path, "wb") as f:
                        f.write(user_resume.getbuffer())

                except Exception as error: pass

                try:
                    # Get resume summary
                    st.session_state.cache_resume_details = genai_engine.get_data_from_resume(local_file_path)

                    # Get the resume url
                    candidate_resume_bucket = CandidateResumesBucket()
                    user_resume_url = candidate_resume_bucket.upload_resume_to_cloud_storage(user_resume_filename, user_resume)

                    # Store to firestore
                    candidate_resume_collection = CandidateResumeCollection()
                    candidate_resume_collection.store_candidate_resume_details(
                        st.session_state.username, 
                        st.session_state.cache_resume_details, 
                        user_resume_url
                    )

                    st.rerun()

                except Exception as error: print(error)

            except Exception as error: print(error)


    with colb:
        if st.button('❌', use_container_width=True):
            del st.session_state.cache_interview_type
            del st.session_state.cache_difficulty_level
            del st.session_state.cache_number_of_questions
            del st.session_state.cache_interview_language
            del st.session_state.cache_resume_details
            
            st.rerun()



if __name__ == "__main__":
    if st.session_state.username:
        with st.sidebar:
            #st.write(list(st.session_state.keys()))
            selected_menu_item = sac.menu(
                [
                    sac.MenuItem(
                        "Practice Interview",
                        icon="grid",
                    ),
                    sac.MenuItem(
                        "Interview Reports",
                        icon="folder2",
                    ),
                    sac.MenuItem(
                        "Resume Analyzer",
                        icon="boxes",
                    ),
                    sac.MenuItem(" ", disabled=True),
                    sac.MenuItem(type="divider"),
                ],
                open_all=True,
            )

            sidebar_container = st.container(height=320, border=False)

        
        if selected_menu_item == 'Practice Interview':
            if st.session_state.cache_display_chat_interface:
                with st.sidebar:
                    with sidebar_container:
                        st.info("Be completely honest & take yor time")

                    cola, colb = st.columns([4, 1])

                    with cola:
                        button_end_interview = st.button("Conclude this Interview", use_container_width=True)
                    
                    with colb:
                            if st.button('❌', use_container_width=True):
                                del st.session_state.interview_id
                                del st.session_state.chat
                                del st.session_state.cache_interview_type
                                del st.session_state.cache_job_title
                                del st.session_state.cache_job_description
                                del st.session_state.cache_number_of_questions
                                del st.session_state.cache_difficulty_level
                                del st.session_state.cache_resume_details
                                del st.session_state.cache_interview_language
                                del st.session_state.messages
                                del st.session_state.cache_display_chat_interface

                                st.rerun()

                    if button_end_interview:
                        interview_collection = InterviewCollection()

                        if st.session_state.cache_interview_type == 'Technical Interview':
                            interview_type_code = 'technical_interview'

                        elif st.session_state.cache_interview_type == 'Behavioural Interview':
                            interview_type_code = 'behavioural_interview'
                        
                        else:
                            interview_type_code = 'overall_evaluation'                    

                        interview_collection.store_candidate_interview_transcript(
                            st.session_state.username, 
                            interview_type_code,
                            st.session_state.interview_id, 
                            st.session_state.messages,
                            st.session_state.cache_job_title,
                            datetime.datetime.now().strftime('%m-%d-%Y'),
                            st.session_state.cache_interview_language,
                            st.session_state.cache_number_of_questions,
                            st.session_state.cache_difficulty_level
                        )

                        st.toast("Your interview has been recorded")

                        overall_interview_analysis = genai_engine.submit_interview_and_generate_report(st.session_state.messages)

                        interview_collection.store_candidate_overall_interview_analysis(
                            st.session_state.username, 
                            interview_type_code,
                            st.session_state.interview_id, 
                            overall_interview_analysis,
                        )

                        st.toast("Getting your results ready")
                        ques_by_ques_analysis = genai_engine.generate_question_by_question_feedback(st.session_state.messages)

                        interview_collection.store_candidate_question_by_question_analysis(
                            st.session_state.username, 
                            interview_type_code,
                            st.session_state.interview_id, 
                            ques_by_ques_analysis,
                        )

                        st.toast("You report will be available in the profile section")


                        # delete session states to reset for next interview
                        del st.session_state.interview_id
                        del st.session_state.chat
                        del st.session_state.cache_interview_type
                        del st.session_state.cache_job_title
                        del st.session_state.cache_job_description
                        del st.session_state.cache_number_of_questions
                        del st.session_state.cache_difficulty_level
                        del st.session_state.cache_resume_details
                        del st.session_state.cache_interview_language
                        del st.session_state.messages
                        del st.session_state.cache_display_chat_interface

                        time.sleep(3)
                        st.rerun()
                        

                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # This shows the chat history on UI
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                if "interview_id" not in st.session_state:
                    st.session_state.interview_id = str(int(time.time()))

                if "chat" not in st.session_state:
                    #st.session_state.chat = st.session_state.gemini_flash.start_chat(
                    #    history=st.session_state.messages
                    #)
                    client = genai.Client(
                        api_key=st.secrets['GEMINI_API_KEY']
                    )

                    system_instruction = f"""
                    You are an AI mock interview assistant. Conduct a mock interview for the user based on the following details:

                    - Job Title: {st.session_state.cache_job_title}
                    - Job Description: {st.session_state.cache_job_description}
                    - Interview Type: {st.session_state.cache_interview_type}
                    - Number of Questions: {st.session_state.cache_number_of_questions}
                    - Language of Interview: {st.session_state.cache_interview_language}

                    - Candidate's Resume: {st.session_state.cache_resume_details}

                    Directly start by asking the first question. No need for any introductions.
                    """

                    st.session_state.chat = client.chats.create(
                        model='gemini-2.0-flash-exp', 
                        history=st.session_state.messages,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.5,
                        ),
                    )

                    welcome_message = f"""
                    Hello {st.session_state.user_display_name.split()[0]}! 👋 
                    Welcome to MockMate, your personalized mock interview assistant.
                    Let's get you ready for success!
                    """
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": welcome_message,
                        }
                    )

                    instructions_message = f"""
                    Here's how this mock interview works:

                    I'll ask you {st.session_state.cache_number_of_questions} questions tailored to the {st.session_state.cache_job_title} role based on the {st.session_state.cache_interview_type} round you selected.
                    You can respond by typing or using your voice. At the end, I'll provide detailed feedback, including your strengths, areas to improve, and suggestions.
                    Are you ready to begin this mock interview?
                    """
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": instructions_message,
                        },
                    )

                    st.rerun()

                if prompt := st.chat_input("Type your question here..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})

                    # 2. Users prompt is displayed in the UI
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner(
                            "Typing..."
                        ):
                            response_from_model = st.session_state.chat.send_message(
                                prompt,
                            )

                            def response_generator(response):
                                for word in response:
                                    time.sleep(0.01)
                                    try:
                                        yield word.text
                                    except Exception as err:
                                        yield word

                            # 3.2 Display LLM's response in UI
                            try:
                                response = st.write_stream(
                                    response_generator(response_from_model.text)
                                )

                            except Exception as err:
                                fallback_message = (
                                    f"Sorry, I am unable to answer this.\nReason: {err}"
                                )

                                response = st.write_stream(
                                    response_generator(fallback_message)
                                )

                    # Update chat history for dislaying in UI in next run
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    
                
            else:
                with st.sidebar:
                    with sidebar_container:
                        st.session_state.cache_job_title = st.text_input(
                            "Job Title", 
                            placeholder='Job Title', 
                            label_visibility='collapsed'
                        )

                        st.session_state.cache_job_description = st.text_area(
                            "Job Description", 
                            placeholder='Enter the job description', 
                            label_visibility='collapsed'
                        )

                        cola, colb = st.columns([4, 1])

                        with cola:
                            button_launch_interview = st.button(
                                "🚀 Launch Interview",
                                on_click=set_cache_display_chat_interface_to_true,
                                use_container_width=True,
                            )

                        with colb:
                            if st.button('⚙️', use_container_width=True):
                                configure_interview_options()
                    
                    if st.button("🔓 Logout of MockMate", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()


                st.write(' ')
                st.markdown(
                    f"<BR><BR><H2>Hi {st.session_state.user_display_name.split()[0]}, Welcome to MockMate! 🎉</H2><H4>Prepare, Perform, and Perfect - Your Interview Preperation Journey Starts Here!!</H4>Feeling anxious about upcoming job interviews? Or perhaps you are struggling to articulate your skills and experience effectively? get started with our AI-powered mock interview platform that provides realistic practice, detailed feedback, and resume analysis!!",
                    unsafe_allow_html=True,
                )

                #st.markdown("<BR>", unsafe_allow_html=True)

                usage_instructions = """
                **Here's how you can get started:**

                1. Simply upload your resume, choose the type of role you are preparing for, and configure your mock intreview experience!
                2. Wait for the AI to generate tailored questions, evaluate your responses and provide detailed feedback on your preperation
                """
                st.info(usage_instructions)



        if selected_menu_item == 'Interview Reports':
            with sidebar_container:
                interview_type = st.selectbox('Select Interview Type', ['Technical', 'Behavioural', 'Overall Evaluation'], index=None)

            if interview_type:
                if interview_type == 'Technical':
                    interview_type = 'technical_interview'
                
                elif interview_type == 'Behavioural':
                    interview_type = 'behavioural_interview'
                
                else:
                    interview_type = 'overall_evaluation'

                interview_collection = InterviewCollection()
                available_interview_ids = interview_collection.fetch_all_interview_ids_by_username(st.session_state.username, interview_type)
                available_interview_ids.sort(reverse=True)

                if len(available_interview_ids) > 0:
                    st.markdown("<H2>Interview Reports</H2><HR>", unsafe_allow_html=True)
                    cola, colb, colc, cold = st.columns(4)

                    for idx, interview_id in enumerate(available_interview_ids):

                        interview_date, job_title = interview_collection.fetch_interview_date_and_role(st.session_state.username, interview_type, interview_id)

                        if idx % 4 == 0:
                            with cola:
                                st.image('assets/report_headers/header1.jpg', use_container_width=True)
                                st.markdown(f"<B>{job_title} Role</B><BR>Interview taken on {interview_date}", unsafe_allow_html=True)
                                if st.button("View Report", use_container_width=True, key=f'_explore_button_{idx}'):
                                    view_interview_report(interview_type, interview_id)
                        
                        elif idx % 4 == 1:
                            with colb:
                                st.image('assets/report_headers/header1.jpg', use_container_width=True)
                                st.markdown(f"<B>{job_title} Role</B><BR>Interview taken on {interview_date}", unsafe_allow_html=True)
                                if st.button("View Report", use_container_width=True, key=f'_explore_button_{idx}'):
                                    view_interview_report(interview_type, interview_id)

                        elif idx % 4 == 2:
                            with colc:
                                st.image('assets/report_headers/header1.jpg', use_container_width=True)
                                st.markdown(f"<B>{job_title} Role</B><BR>Interview taken on {interview_date}", unsafe_allow_html=True)
                                if st.button("View Report", use_container_width=True, key=f'_explore_button_{idx}'):
                                    view_interview_report(interview_type, interview_id)

                        else:
                            with cold:
                                st.image('assets/report_headers/header1.jpg', use_container_width=True)
                                st.markdown(f"<B>{job_title} Role</B><BR>Interview taken on {interview_date}", unsafe_allow_html=True)
                                if st.button("View Report", use_container_width=True, key=f'_explore_button_{idx}'):
                                    view_interview_report(interview_type, interview_id)

                else:
                    st.markdown("<BR><BR><BR><BR><BR>", unsafe_allow_html=True)
                    sac.result(label='You are yet to take an interview', description='Reports for you intervews will appear here', status='empty')

            else:
                sac.result(label='Select the Interview Type', description='Your previous interviews will appear here', status=404)

        if selected_menu_item == 'Resume Analyzer':
            with sidebar_container:
                job_description = st.text_area("Enter the job description", placeholder='Enter the job description here...')
                user_resume = st.file_uploader("Upload your Resume", ['pdf'], accept_multiple_files=False)
                
            with st.sidebar:
                button_anayze_resume = st.button("Analyze Resume", use_container_width=True)

            if button_anayze_resume:
                resume_file_path = os.path.join(
                    "temp", user_resume.name
                )

                try:
                    with open(resume_file_path, "wb") as f:
                        f.write(user_resume.getbuffer())

                except Exception as error: pass

                resume_feedback = genai_engine.analyze_resume_and_generate_feedback(resume_file_path, job_description)

                st.markdown("## Here is a Detailed Analysis of your resume")
                st.markdown(resume_feedback)
                st.markdown("<BR><BR>", unsafe_allow_html=True)

            else:
                sac.result(label='Enter your Resume and Job Description', description='And get a detailed insight into tuning your resume', status=404)

    else:

        try:
            firebase_credentials = credentials.Certificate(
                    "config/firebase_service_account_key.json"
                )
            firebase_admin.initialize_app(firebase_credentials)

        except: pass

        _, cola, _ = st.columns([1, 2, 1])

        with cola:
            st.markdown("<BR><center><H2> Welcome to MockMate</H2></center>", unsafe_allow_html=True)

            with st.form(key='_form_login'):
                email = st.text_input('EMail/Username', placeholder='username', label_visibility='collapsed')
                password = st.text_input('Password', placeholder='password', label_visibility='collapsed', type="password")

                if st.session_state.username is False:
                    warning_message = st.warning("Invalid Username or Password")
                    time.sleep(3)
                    st.session_state.username = None
                    warning_message.empty()

                _, colx, _ = st.columns([1, 2, 1])

                with colx:
                    button_login = st.form_submit_button("LogIn to MockMate", use_container_width=True)
                        
                if button_login:
                    try:
                        api_key = st.secrets['FIREBASE_WEB_API_KEY']
                        base_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

                        if "@" not in email:
                            username = email
                            user = firebase_admin.auth.get_user(username)
                            email = user.email

                        data = {"email": email, "password": password}

                        response = requests.post(
                            base_url.format(api_key=api_key), json=data
                        )

                        if response.status_code == 200:
                            data = response.json()

                            if "user_display_name" not in st.session_state:
                                st.session_state.user_display_name = data["displayName"]
                                
                            st.session_state.user_display_name = data["displayName"]
                            st.session_state.username = firebase_admin.auth.get_user_by_email(email).uid

                            st.rerun()
                    
                        else:
                            print('hey')
                            st.session_state.username = False
                            st.rerun()

                    except Exception as error:
                        print(error)
                        st.session_state.username = False
                        st.rerun()


            st.markdown(" ", unsafe_allow_html=True)

            _, colx, _ = st.columns([1, 2, 1])

            with colx:
                if st.button("Create New Account", use_container_width=True, type='tertiary'):
                    create_account()


            
