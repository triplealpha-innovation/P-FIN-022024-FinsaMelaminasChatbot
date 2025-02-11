from db.database import SessionLocal, engine
from db.schemas import AgentState, CheckRelevance, ConvertToSQL, RewrittenQuestion

import os
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import text, inspect

def get_database_schema(engine):
    inspector = inspect(engine)
    schema = ""
    for table_name in inspector.get_table_names():
        schema += f"Table: {table_name}\n"
        for column in inspector.get_columns(table_name):
            col_name = column["name"]
            col_type = str(column["type"])
            if column.get("primary_key"):
                col_type += ", Primary Key"
            if column.get("foreign_keys"):
                fk = list(column["foreign_keys"])[0]
                col_type += f", Foreign Key to {fk.column.table.name}.{fk.column.name}"
            schema += f"- {col_name}: {col_type}\n"
        schema += "\n"
    print("Retrieved database schema.")
    return schema

def check_relevance(state: AgentState, config: RunnableConfig):
    question = state.question  
    schema = get_database_schema(engine)
    print(f"Checking relevance of the question: {question}")
    system = """You are an assistant that determines whether a given question is related to the following database schema.

    Schema:
    {schema}

    Respond with only "relevant" or "not_relevant".
    """.format(schema=schema)
    human = f"Question: {question}"
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", human),
        ]
    )
    llm = AzureChatOpenAI(
        temperature=0.0,
        model="gpt-35-turbo-16k",  
        deployment_name="gpt-35-turbo-16k",
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2024-10-21"
    )
    structured_llm = llm.with_structured_output(CheckRelevance)
    relevance_checker = check_prompt | structured_llm
    relevance = relevance_checker.invoke({})
    state.relevance = relevance.relevance
    print(f"Relevance determined: {state.relevance}")
    return state

def convert_nl_to_sql(state: AgentState, config: RunnableConfig):
    question = state.question
    schema = get_database_schema(engine)
    print(f"Converting question to SQL")
    system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:

    {schema}

    Provide only the SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.

    For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'.

    Select only the relevant fields to generate the response.
    
    When performing a SELECT *, make the necessary joins to retrieve the corresponding descriptions and avoid returning ID fields.
    """.format(schema=schema)
    convert_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Question: {question}"),
        ]
    )
    llm = AzureChatOpenAI(
        temperature=0.0,
        model="gpt-35-turbo-16k", 
        deployment_name="gpt-35-turbo-16k",  
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2024-10-21"
    )
    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm
    result = sql_generator.invoke({"question": question})
    state.sql_query = result.sql_query
    print(f"Generated SQL query: {state.sql_query}")
    return state


def execute_sql(state: AgentState):
    sql_query = state.sql_query.strip()
    session = SessionLocal()
    print(f"Executing SQL query: {sql_query}")
    
    try:
        # Verificar si la consulta es de tipo DROP, INSERT, DELETE o UPDATE
        if any(sql_query.lower().startswith(command) for command in ["insert", "delete", "update", "drop"]):
            print("Detected potentially dangerous query (INSERT, DELETE, UPDATE, or DROP). Redirecting to regenerate_query.")
            # Llamar a regenerate_query en lugar de ejecutar la consulta
            return regenerate_query(state)

        # Si la consulta no es de tipo peligroso (SELECT, etc.), la ejecutamos
        result = session.execute(text(sql_query))
        
        if sql_query.lower().startswith("select"):
            rows = result.fetchall()
            columns = result.keys()
            if rows:
                header = ", ".join(columns)
                state.query_rows = [dict(zip(columns, row)) for row in rows]
                print(f"Raw SQL Query Result: {state.query_rows}")
                # Formatear el resultado para su presentación
                formatted_result = state.query_rows
            else:
                state.query_rows = []
                formatted_result = "No results found."
            state.query_result = formatted_result
            state.sql_error = False
            print("SQL SELECT query executed successfully.")
        else:
            session.commit()
            state.query_result = {
                "content": "The action has been successfully completed."
            }
            state.sql_error = False
            print("SQL command executed successfully.")

    except Exception as e:
        state.query_result = {
                "content": f"Error executing SQL query: {str(e)}"
            }
        state.sql_error = True
        print(f"Error executing SQL query: {str(e)}")
    
    finally:
        session.close()

    return state

def generate_human_readable_answer(state: AgentState):
    # Generar un mensaje con IA para interpretar los datos
    natural_language_prompt = f"""
        Proporciona una respuesta en lenguaje natural de los siguientes datos: {state.query_result}.  
        Si hay una columna cuyo nombre comienza con 'id_' y existe otra columna que comienza con 'descripcion_', usa la información de 'descripcion_' en la respuesta en lugar de referirte al identificador.  
        No menciones los nombres de las columnas tal como están en la base de datos; exprésalos en lenguaje natural.
    """                
    # Usar el modelo para generar el resumen
    language_model = AzureChatOpenAI(
                    temperature=0.5,
                    model="gpt-35-turbo-16k",  
                    deployment_name="gpt-35-turbo-16k", 
                    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    openai_api_version="2024-10-21"
    )
                
    # Asegurarnos de pasar un prompt como string en vez de un diccionario
    natural_language_response = language_model.invoke(natural_language_prompt)
    state.query_result = natural_language_response
    # Acceder al contenido del mensaje generado por IA
    content = natural_language_response.content

    # Usar print con formato
    print("Resultados de la Consulta SQL:\n")
    print("=" * 50)  # Separador decorativo
    print(content)  # Imprimir el contenido del mensaje generado
    print("=" * 50)  # Separador decorativo
    return state

def regenerate_query(state: AgentState):
    question = state.question
    print("Regenerating the SQL query by rewriting the question.")
    system = """You are an assistant that reformulates an original question to enable more precise SQL queries. Ensure that all necessary details, such as table joins, are preserved to retrieve complete and accurate data.
    """
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                f"Original Question: {question}\nReformulate the question to enable more precise SQL queries, ensuring all necessary details are preserved.",
            ),
        ]
    )
    llm = AzureChatOpenAI(
        temperature=0.0,
        model="gpt-35-turbo-16k", 
        deployment_name="gpt-35-turbo-16k", 
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2024-10-21",
    )
    structured_llm = llm.with_structured_output(RewrittenQuestion)
    rewriter = rewrite_prompt | structured_llm
    rewritten = rewriter.invoke({})
    state.question = rewritten.question
    state.attempts += 1
    print(f"Rewritten question: {state.question}")
    return state

def alert_not_relevant_results(state: AgentState):
    state.query_result = {
        "content": "No existen resultados para la búsqueda. Haga una pregunta más precisa, por favor."
    }
    return state

def end_max_iterations(state: AgentState):
    state.query_result = {
        "content": "No existen resultados para la búsqueda. Haga una pregunta más precisa, por favor."
    }
    print("Maximum attempts reached. Ending the workflow.")
    return state

def relevance_router(state: AgentState):
    if state.relevance.lower() == "relevant":
        return "convert_to_sql"
    else:
        return "alert_not_relevant_results"

def check_attempts_router(state: AgentState):
    if state.attempts < 3:
        return "convert_to_sql"
    else:
        return "end_max_iterations"
    
def execute_sql_router(state: AgentState):
    # Acceder directamente al atributo sql_error
    if not state.sql_error:  # Esto es equivalente a comprobar si sql_error es False o None
        return "generate_human_readable_answer"
    else:
        return "regenerate_query"
