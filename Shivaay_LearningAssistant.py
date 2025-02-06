import streamlit as st
from pylatexenc.latex2text import LatexNodes2Text
import requests

# Shivaay AI API Details
API_URL = st.secrets["API_URL"]
API_KEY = st.secrets["API_KEY"]

# Initialize session state if not already initialized
if 'history' not in st.session_state:
    st.session_state.history = []

# Streamlit App Title
st.title("Study Assistant")
st.write("( Using Shivaay_AI )")


# Sidebar for navigation
mode = st.sidebar.radio(
    "Choose an option",
    [
        "Answering Questions: Provide explanations for various subjects or topics",
        "Quiz Generator: Generate quizzes based on your study area",
        "Learning Plans: Create personalized study plans",
        "Provide Resources: Share links, videos, or documents for your topics",
        "Flashcard Generator: Create flashcards from topics, PDFs, or URLs",
        "Code Expert: Debug, Explain, Optimize, Suggest Additions, or Generate Code",
        "History: View and Manage Your History"
    ]
)

# Function to make API requests to the AI
def get_ai_response(user_input, mode_type):
    # Construct API request payload
    payload = {
        "messages": [
            {"role": "system", "content": "You are an educational assistant who helps students with various tasks."},
            {"role": "user", "content": f"{mode_type}: {user_input}"}
        ],
        "temperature": 0.7,
        "top_p": 1
    }

    # Make API request
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json", "api-subscription-key": API_KEY}, json=payload, verify=False)
        response_data = response.json()
        answer = response_data.get("answer", "No response received.")
        return answer
    except Exception as e:
        return f"Error during request: {e}"
    

# Function to store the history
def add_to_history(action, question, result):
    st.session_state.history.append({"action": action, "question": question, "result": result})

# Function to delete a particular history entry
def delete_history_entry(index):
    if 0 <= index < len(st.session_state.history):
        del st.session_state.history[index]

# Function to clear all history
def clear_history():
    st.session_state.history.clear()

# Function to view and manage history
def view_history():
    st.header("Your History")
    
    if len(st.session_state.history) == 0:
        st.write("You don't have any history yet.")
    else:
        for idx, entry in enumerate(st.session_state.history):
            st.subheader(f"Item {idx + 1}: {entry['action']}")
            st.write(f"**Question:** {entry['question']}")
            st.write(f"**Result:** {entry['result']}")
            
            # Add buttons for delete and clear
            st.write("--double-click to delete--")
            if st.button(f"Delete Item {idx + 1}"):
                delete_history_entry(idx)
        
        # Clear all history
        if st.button("Clear All History"):
            clear_history()

# Function for Answering Questions
def answering_questions():
    st.header("Answering Questions")
    subject = st.text_input("Enter the subject or topic you need help with:")
    if subject:
        if st.button("Generate Response"):
            st.write(f"AI is preparing the explanation for '{subject}'...")
            QA_prompt=f"Describe the subject or topic:{subject} and tell me pointers about it and make sure they are concise and correct"
            answer = get_ai_response(QA_prompt, "Answering Questions")
            st.write("🤖 **Assistant:**", answer)
            add_to_history("Answering Questions", subject, answer)
    else:
        st.warning("Please enter a topic or subject to get an explanation.")

# Function for Quiz Generator
def quiz_generator():
    st.header("Quiz Generator")
    topic = st.text_input("Enter the study topic for quiz generation:")

    if topic:
        num_questions = st.number_input("How many questions would you like in the quiz?", min_value=1, max_value=10, value=5)

        # Prompt the AI to generate a quiz with the specified number of questions
        if st.button("Generate Quiz"):
            st.write(f"AI is generating a quiz for '{topic}' with {num_questions} questions...")

            # Generate the quiz with the number of questions
            quiz_prompt = f"Generate a quiz with {num_questions} multiple choice questions about {topic}. Make sure that any numerical is represented in a normal text for like 1/root(1-x^2) and not in latex form like ""( f(x) = frac{1{sqrt{1 - x^2}})"". Include the correct answers and the step by step solution as well.and before providing the answers and solutions i want you to think at each step and provide valid steps to reach to the correct answer"
            answer = get_ai_response(quiz_prompt, "Quiz Generator")

            # Convert LaTeX to normal text
            formatted_response = LatexNodes2Text().latex_to_text(answer)
            st.write("🤖 **Assistant:**", formatted_response)
            add_to_history("Quiz Generated", topic, formatted_response)

            # Create the file for download
            quiz_filename = f"{topic}_quiz.txt"
            st.download_button(
                label="Download Quiz as Text File",
                data=formatted_response,
                file_name=quiz_filename,
                mime="text/plain"
            )

        else:
            st.warning("Please click the 'Generate Quiz' button to get the quiz.")
    else:
        st.warning("Please enter a topic to generate a quiz.")

# Function for Learning Plans
def learning_plans():
    st.header("Learning Plans")
    goal = st.text_input("Enter your learning goal like 'Improve in Mathematics', 'Master Machine Learning', 'Learn Programming' : ")

    if goal:
        if st.button("Generate plan"):
            st.write(f"AI is creating a personalized learning plan for: {goal}...")

            lp_response = f"Generate a learnging plan so that i can achieve the goal of: {goal} make sure that the plan is comprehensive and easy to follow."
            answer = get_ai_response(lp_response, "Learning Plans")
            st.write("🤖 **Assistant:**", answer)
            add_to_history("Learning Plans", goal, answer)

# Function for Providing Resources
def provide_resources():
    st.header("Provide Resources")
    topic = st.text_input("Enter the topic you'd like resources for:")
    if topic:
        if st.button("Generate Resources"):
            st.write(f"AI is fetching resources for '{topic}'...")

            resource_prompt=f"Provide a comprehensive list of resources for the topic:{topic} and also give the links where you can."
            answer = get_ai_response(resource_prompt, "Provide Resources")
            st.write("🤖 **Assistant:**", answer)
            add_to_history("Provide Resources", topic, answer)

    else:
        st.warning("Please enter a topic to get resources.")


# Function to parse AI-generated flashcards
def parse_flashcards(response_text):
    flashcards = []
    sections = response_text.split("\n\n")  # Split into blocks

    for section in sections:
        lines = section.split("\n")
        front, back = None, None

        for line in lines:
            if line.strip().lower().startswith("front:"):
                front = line.replace("Front:", "").strip()
            elif line.strip().lower().startswith("back:"):
                back = line.replace("Back:", "").strip()

        if front and back:
            flashcards.append({"front": front, "back": back})

    return flashcards

# Function to convert flashcards into a downloadable text format
def format_flashcards_for_download(flashcards):
    flashcard_text = "\n\n".join([f"{i+1}. {card['front']}\n   {card['back']}" for i, card in enumerate(flashcards)])
    return flashcard_text

# Function for Flashcard Generator
def flashcard_generator():
    st.header("🎴 Flashcard Generator")
    option = st.radio("Choose input type:", ["Enter a Topic"])  ##["Upload a PDF", "Provide a URL"]
    
    if option == "Enter a Topic":
        topic = st.text_input("Enter the topic for flashcards:")
        num_flashcards = st.slider("Number of flashcards:", 1, 20, 10)
        
        if topic and st.button("Generate Flashcards"):
            prompt = f"Generate {num_flashcards} flashcards for the topic '{topic}'. Each flashcard must follow this format:\n\nFront: Question/Concept\nBack: Answer/Explanation\n\nEnsure the response is structured exactly as above."
            response = get_ai_response(prompt, "Flashcard Generator")
            flashcards = parse_flashcards(response)
            
            if flashcards:
                st.subheader("📖 Generated Flashcards")
                for i, card in enumerate(flashcards):
                    with st.expander(f"🔹 {card['front']}"):
                        st.write(card['back'])
                
                # Convert to downloadable text format
                flashcard_text = format_flashcards_for_download(flashcards)
                flashcard_filename = f"{topic.replace(' ', '_')}_flashcards.txt"

                # Provide download button
                st.download_button(
                    label="📥 Download Flashcards",
                    data=flashcard_text,
                    file_name=flashcard_filename,
                    mime="text/plain"
                )
            else:
                st.warning("⚠️ No valid flashcards were generated. Try rewording your topic.")

###elif option == "Upload a PDF":
##        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
  ##      if uploaded_file and st.button("Extract Flashcards"):
    ##        st.warning("🚧 PDF processing not implemented yet.") 

###elif option == "Provide a URL":
    ##    url = st.text_input("Enter a URL:")
      ##  if url and st.button("Extract Flashcards"):
        ##    st.warning("🚧 URL processing not implemented yet.")    ## not implemented yet 



# Function for Dynamic Code Expert (Debugging, Explanation, Optimization, Suggestions, Code Generation)
def code_expert():
    st.header("Dynamic Code Expert")

    # Input for code snippet or request
    code_or_request = st.text_area("Enter your code snippet or describe what you want to do:")

    if code_or_request:
        task_type = st.selectbox("What would you like to do with the code?", 
                                 ["Explain", "Debug", "Optimize", "Suggest Additions", "Generate Code"])
        
        if st.button("Send Message"):

            st.write("AI is analyzing your request...")

            if task_type == "Explain":
                explanation_prompt = f"Explain the following code in simple terms:\n\n{code_or_request}"
                explanation = get_ai_response(explanation_prompt, "Code Expert")
                st.write("🤖 **Assistant:**", explanation)

            elif task_type == "Debug":
                debug_prompt = f"Identify and fix any bugs in the following code:\n\n{code_or_request}"
                debugged_code = get_ai_response(debug_prompt, "Code Expert")
                st.write("🤖 **Assistant (Debugged Code):**", debugged_code)

            elif task_type == "Optimize":
                optimize_prompt = f"Optimize the following code for better performance or readability:\n\n{code_or_request}"
                optimized_code = get_ai_response(optimize_prompt, "Code Expert")
                st.write("🤖 **Assistant (Optimized Code):**", optimized_code)

            elif task_type == "Suggest Additions":
                suggestion_prompt = f"Suggest improvements or additional features that can be added to the following code:\n\n{code_or_request}"
                suggestions = get_ai_response(suggestion_prompt, "Code Expert")
                st.write("🤖 **Assistant (Suggestions):**", suggestions)

            elif task_type == "Generate Code":
                generation_prompt = f"Generate code based on the following request:\n\n{code_or_request}"
                generated_code = get_ai_response(generation_prompt, "Code Expert")
                st.write("🤖 **Assistant (Generated Code):**", generated_code)
                

    else:
        st.warning("Please enter a code snippet or describe what you want to do.")

# Display the corresponding section based on user selection
if mode == "Answering Questions: Provide explanations for various subjects or topics":
    answering_questions()
elif mode == "Quiz Generator: Generate quizzes based on your study area":
    quiz_generator()
elif mode == "Learning Plans: Create personalized study plans":
    learning_plans()
elif mode == "Provide Resources: Share links, videos, or documents for your topics":
    provide_resources()
elif mode == "Flashcard Generator: Create flashcards from topics, PDFs, or URLs":
    flashcard_generator()
elif mode == "Code Expert: Debug, Explain, Optimize, Suggest Additions, or Generate Code":
    code_expert()
elif mode == "History: View and Manage Your History":
    view_history()
