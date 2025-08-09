from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

conversation_memory = []  

def get_llm_response(api_key: str, speech_to_text_output: str) -> str:
    global conversation_memory

    llm = ChatGroq(
        model="llama3-70b-8192",  
        api_key=api_key,
        temperature=0.1,
        max_tokens=1000
    )

    memory_context = ""
    for user_q, ai_r in conversation_memory[-3:]: 
        memory_context += f"User: {user_q}\nAI: {ai_r}\n"

    prompt = ChatPromptTemplate.from_template(
        f"You are a helpful AI. The user has been having this conversation so far:\n"
        f"{memory_context}\n"
        f"Now, the user says: {{context}}\n"
        f"Reply in a simple, polite, and easy-to-understand way without using complex words."
    )

    chain = prompt | llm
    response = chain.invoke({"context": speech_to_text_output})
    ai_reply = response.content

    conversation_memory.append((speech_to_text_output, ai_reply))

    return ai_reply
