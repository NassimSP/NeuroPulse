import openai
import os

# Make sure to set your OpenAI API key as an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_quiz(topic, num_questions=5):
    prompt = f"""
Create a {num_questions}-question multiple choice quiz on the topic: "{topic}".
Each question should have 4 options (A-D), and clearly indicate the correct answer after each question.

Example format:
Q1: What is...?
A) ...
B) ...
C) ...
D) ...
Answer: C

Keep the tone friendly and short. Make it suitable for someone with ADHD who prefers fast-paced learning.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def main():
    print("📚 Welcome to NeuroPulse: Adaptive Quiz Engine")
    topic = input("Enter a topic you want to learn: ")

    print("\nGenerating your quiz... please wait.\n")
    quiz = generate_quiz(topic)
    print(quiz)

    print("\n✅ Quiz complete. You can copy this to track your answers.")
    print("📌 Future versions will let you answer and log results interactively.")

if __name__ == "__main__":
    main()
