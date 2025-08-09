from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def get_llm_response(api_key: str, speech_to_text_output: str) -> str:
    
    llm = ChatGroq(
        model="llama3-70b-8192",  
        api_key=api_key,
        temperature=0.1,
        max_tokens=1000
    )

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful AI. The user has asked the following question: {context}.\n"
        "Reply in a simple, polite, and easy-to-understand way without using complex words."
)

  
    chain = prompt | llm
    response = chain.invoke({"context": speech_to_text_output})


    return response.content



