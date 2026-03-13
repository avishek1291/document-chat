from langchain_groq import ChatGroq;
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from splitter import Vectors
import dotenv
import os

dotenv.load_dotenv()

class Model():

    def get_model(self):
        llm  = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.9)
        return llm
    
    def get_prompt(self):
        template = PromptTemplate(
           template ='you are helpfull assitant, based on the {context} try to answer Question: {question}. If the answer is not in context just say you dont know',
           input_variables=['context', 'question']
        )
        return template
    
    def get_parallel_chain(self):
        retriever = Vectors().get_retriver()
        
        if retriever is None:
            raise ValueError("No document has been uploaded yet. Please upload a document first.")
        
        chain = RunnableParallel({
            'question': RunnablePassthrough(),
            'context': retriever
        })
        return chain

    def invoke_llm(self, user_query: str):
        parser = StrOutputParser()
        prompt = self.get_prompt()
        parallel_chain = self.get_parallel_chain()
        llm = self.get_model()
        chain = parallel_chain|prompt|llm|parser
        print(chain.get_graph().draw_ascii())
        return chain.invoke(user_query)







    

    
