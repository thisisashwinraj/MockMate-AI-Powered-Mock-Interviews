## Level Up Your Interview Prep with MockMate: AI-Powered Mock Interviews, and Resume Analysis

Landing your dream job often hinges on acing the interview. But how do you effectively practice and refine your interviewing skills without real-world pressure? The traditional methods of rehearsing with friends or simply hoping for the best often fall short. Many candidates struggle to articulate their strengths, understand their weaknesses, and tailor their resumes effectively to different job descriptions.
This is where MockMate comes in - an AI-powered mock interview app designed to help you prepare, perform, and perfect your interview skills. Whether you're a seasoned professional or a fresh graduate, MockMate offers a realistic and personalized practice environment with in-depth feedback to boost your confidence and chances of success.
System Architecture and Design

MockMate is designed as a comprehensive interview preparation tool with a clean and intuitive user experience. The core architecture is centered on a user-friendly interface, leveraging Streamlit for interactive front-end elements, and a robust backend using Google's Gemini 2.0 Flash.
The app's design rationale is based on the following key aspects:
Realistic Simulation: Gemini 2.0 Flash is used to generate natural-sounding interview questions, creating an authentic interview experience, taking into account the job title, description, resume, number of questions, language, and difficulty level provided by the user.
Detailed Feedback: Users receive not just an overall score, but also a comprehensive analysis through three reports: a general summary, detailed performance analysis, and a question-by-question breakdown. This is achieved using the multimodal capabilities of Gemini 2.0 Flash and sometimes Pydantic to generate structured responses.

Mockmate - HomepagePersonalized Experience: Users can customize their interview sessions based on the type of interview (technical, behavioral, or overall evaluation), difficulty level, language, and the number of questions to suit their particular requirements, enabling them to target their preparation effectively.
Resume Optimization: MockMate's resume analyzer assesses how well a resume matches the requirements of the job description providing suggestions, skill gap analysis, and overall feedback, ensuring that each user's resume is a perfect match for the application.
Scalable Architecture: Firestore is used as a backend to store user data (resumes, interview transcripts, and feedback), preferences, and configurations. The application leverages cloud storage to handle uploaded user resumes, ensuring a scalable, reliable, and secure storage and access mechanism.

The application's design ensures that users can easily navigate through the application and gain valuable insights into their interview strengths and weaknesses, in order to improve their overall performance.
Prerequisites
Before you start using the MockMate app, make sure you have the following:
Python 3.7+: Required for building and running the application.
Streamlit: For building the front-end. Install using `pip install streamlit`.
Firebase Admin SDK: Install using `pip install firebase-admin`.
Gemini API Python Client: Install using `pip install google-generativeai`.
Google Gemini API Key: Get your API key from Google AI Studio.

Step-by-Step Instructions
While we won't build the entire app from scratch in this blog, here's a breakdown of the key steps involved in building the project
User Authentication: Implement Firebase authentication within the streamlit UI to facilitate user signups and logins.

Firebase Authenticationfirebase_credentials = credentials.Certificate(
  "config/firebase_service_account_key.json"
)
firebase_admin.initialize_app(firebase_credentials)

with st.form(key='_form_login'):
  email = st.text_input('EMail/Username', placeholder='username', label_visibility='collapsed')
  password = st.text_input('Password', placeholder='password', label_visibility='collapsed', type="password")

  # Form submission button and authentication logic here
  # Signup button to trigger signup dialog

  if st.button("Create New Account", use_container_width=True, type='tertiary'):
     create_account() # Dialog function to trigger the new account creation
2. Resume Handling: Implement the functionality to handle resume uploads. Use Cloud storage to store the resumes in the cloud. You can use a library like `PyPDF2` or similar to extract text from resumes for analysis if needed. But it may sometimes struggles with tabular data and/or if the user enters resume in an image format.
Google Cloud StorageAlso, store a summary of the resume in Firestore to reuse for generating interview questions later.
email = st.text_input('EMail/Username', placeholder='username', label_visibility='collapsed')

user_resume = st.file_uploader("Upload your resume", type=['pdf'], accept_multiple_files=False)

try:
  user_resume_filename = user_resume.name
  local_file_path = os.path.join(
    "temp", user_resume_filename
  )

  try:
    with open(local_file_path, "wb") as f:
      f.write(user_resume.getbuffer())
   
  except Exception as error: pass
  
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
except Exception as error: print(error)
Firestore instance3. Configuring the Interview: Implement a form or modal in Streamlit to allow users to configure interview details (job title, description, interview type, number of questions, difficulty, language) and save these configurations in session storage.
# configuration dialog
with st.dialog('Configure Your Interview', width='large'):
  # Inputs to take the user defined interview parameters
  st.session_state.cache_interview_type = st.selectbox("Interview Type",['Technical Interview', 'Behavioural Interview', 'Overall Evaluation'], placeholder='Interview Type')
  st.session_state.cache_difficulty_level = st.selectbox("Difficulty Level",options=['Beginner ', 'Intermediate ', 'Experienced', 'Expert'], index=1)
  
  st.session_state.cache_number_of_questions = st.number_input("Number of Questions",placeholder='Number of Questions', min_value=5, max_value=15)
  st.session_state.cache_interview_language = st.selectbox("Language for Interview",options=['English ', 'Hindi ', 'French'])
  
  # Other UI elements
4. Chat Interface: Use Streamlit's chat input to create an interactive chat-based mock interview. Make use of session states for persistent storage across multiple iterations.
if "messages" not in st.session_state:
  st.session_state.messages = []
  
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

if prompt := st.chat_input("Type your question here…"):
  st.session_state.messages.append({"role": "user", "content": prompt})
 
  with st.chat_message("user"):
    st.markdown(prompt)
  
  with st.chat_message("assistant"):
  # AI response generation
  # Logic for displaying response and appending to chat history
5. Generating Feedback: After an interview is completed, use Gemini 2.0 Flash to generate a detailed summary, performance analysis, and a question-by-question breakdown of the user's interview. Store these details in Firestore.
Interview Report - Performance Analysisinterview_collection = InterviewCollection()

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

overall_interview_analysis = genai_engine.submit_interview_and_generate_report(
  st.session_state.messages
)

interview_collection.store_candidate_overall_interview_analysis(
  st.session_state.username,
  interview_type_code,
  st.session_state.interview_id,
  overall_interview_analysis,
)

ques_by_ques_analysis = genai_engine.generate_question_by_question_feedback(
  st.session_state.messages
)

interview_collection.store_candidate_question_by_question_analysis(
  st.session_state.username,
  interview_type_code,
  st.session_state.interview_id,
  ques_by_ques_analysis,
)
6. Resume Analysis: Implement an interface to perform resume analysis against a given job description using Gemini. The AI should output feedback on how the resume aligns with the job description.
user_resume = st.file_uploader(
  "Upload your Resume", 
  ['pdf'], 
  accept_multiple_files=False
)

resume_file_path = os.path.join(
  "temp", user_resume.name
)

try:
  with open(resume_file_path, "wb") as f:
    f.write(user_resume.getbuffer())
except Exception as error: pass

resume_feedback = genai_engine.analyze_resume_and_generate_feedback(resume_file_path, job_description)
Result
After conducting a mock interview, MockMate will provide a detailed report, including the following details:
Interview Summary: Shows the overall score and probability of your selection, along with a brief snapshot of your performance.
Performance Analysis: Provides a detailed breakdown of your strengths and weaknesses, including your strong skills, skill gaps, a comparitive analysis of your performance, a quantitative and a qualitative analysis of your interview. It also provides insights on your cultural fit and final remarks on your overall performance.
Question-by-Question Analysis: Analyzes each question individually, providing detailed feedback on your responses and areas for improvement.

When performing resume analysis, MockMate provides:
Suitability Score: The suitability score indicates how close your resume is to the ideal requirements of the job description.
Feedback on Skills: Highlight your strengths and suggest areas for improvement for your skill sets.
Actionable Suggestions: Specific tweaks in your resume will be suggested to highlight the needed keywords.

By utilizing these reports, users can gain a deeper understanding of how to align their skills with the job descriptions and how to improve their responses. MockMate helps users to tailor their approach to different job opportunities.
Future Scope
MockMate is designed to continuously evolve by adding new features to improve the user experience. We are working to incorporate:
Multimodal Analysis: Integrating features to understand and analyse user's non-verbal communication during the interviews.
Personalized Learning Paths: We are working towards creating personalized learning paths based on user's profile and weaknesses, including providing mock interviews for specific skills.
Community Building: Building a community for users to come and share their feedback to enhance their growth.

With that, we have reached the end of this article. If you have any questions or believe I have made any mistake, please feel free to reach out to me! You can get in touch with me via Email or LinkedIn. Until then, happy learning!
To learn more about Google Cloud services and to create impact for the work you do, get around to these steps right away:
Register for Code Vipassana sessions
Join the meetup group Datapreneur Social
Sign up to become Google Cloud Innovator
