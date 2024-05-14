from IPython.display import display
from IPython.display import Markdown
import google.generativeai as genai
import re
import os

API = os.environ['API_KEY']
genai.configure(api_key=API)

def generate_related_words(course_name, lesson_name, grade):
    model = genai.GenerativeModel('gemini-1.0-pro')
    response = model.generate_content(f"The course is about {course_name}. The lesson is {lesson_name}. The grade is {grade}. Generate ten new single-word with length not over 14 characters related to this context, remember to emphasize on the fact that these words have to be non compound words:")
    words = response.text.split('\n')
    ten_words = [re.sub(r'\d+\.\s*', '', word) for word in words if word]
    new_words = ", ".join(ten_words)
    return new_words

