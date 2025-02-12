from db.database import SessionLocal, engine
from db.schemas import AgentState, CheckRelevance, ConvertToSQL, RewrittenQuestion

import os
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import text, inspect

# Aquí definimos un almacenamiento en memoria (puede ser reemplazado por una base de datos)
session_storage = {}

def get_session_history(uuid_sesion: str) -> list:
    """
    Recupera el historial de la sesión basado en el uuid_sesion.
    Si no existe, inicializa un historial vacío.
    """
    # Aquí puedes recuperar el historial desde la base de datos o almacenamiento en memoria
    # Por ejemplo, utilizando una base de datos o un diccionario en memoria
    session_history = session_storage.get(uuid_sesion, [])
    return session_history

def save_session_history(uuid_sesion: str, session_history: list):
    """
    Guarda el historial de la sesión en la base de datos o almacenamiento.
    """
    # Aquí puedes guardar el historial en la base de datos o en memoria
    # Por ejemplo, utilizando una base de datos o un diccionario en memoria
    session_storage[uuid_sesion] = session_history


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
    print("check_relevance")
    # Obtener el uuid_sesion desde el estado
    uuid_sesion = state.uuid_sesion

    # Recuperar o inicializar el historial para esta sesión
    session_history = get_session_history(uuid_sesion)

    question = state.question  
    schema = get_database_schema(engine)
    print(f"Checking relevance of the question: {question}")
    system = """You are an assistant that determines whether a given question is related to the following database schema.

    Schema:
    {schema}

    Respond with only "relevant" or "not_relevant".
    
    "Orden Trabajo is also referred to as OT."

    """.format(schema=schema)    
    # Construir el prompt, incluyendo el historial de la sesión
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", f"Historial: {session_history}, Question: {question}")
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
    print("convert_nl_to_sql")
    # Obtener el uuid_sesion desde el estado
    uuid_sesion = state.uuid_sesion

    # Recuperar o inicializar el historial para esta sesión
    session_history = get_session_history(uuid_sesion)

    # Obtener la pregunta de la sesión
    question = state.question
    schema = get_database_schema(engine)

    print(f"Converting question to SQL")
    
    # Definir el sistema y el prompt para convertir la pregunta a SQL
    system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:

    {schema}

    Provide only the SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.

    For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'. 

    Select only the relevant fields to generate the response.

    When performing a SELECT *, make the necessary joins to retrieve the corresponding descriptions and avoid returning ID fields.

    "When you need to search for text fields, always use LIKE. For example, DO NOT USE this: SELECT id_linea FROM linea WHERE descripcion = 'plastificados III', but instead use this: SELECT id_linea FROM linea WHERE descripcion ILIKE '%plastificados III%'."
    
    "Orden Trabajo is also referred to as OT."
    """.format(schema=schema)

    # Construir el prompt, incluyendo el historial de la sesión
    convert_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", f"Historial: {session_history}, Question: {question}")
        ]
    )

    # Inicializar el modelo de IA (Azure OpenAI)
    llm = AzureChatOpenAI(
        temperature=0.0,
        model="gpt-35-turbo-16k", 
        deployment_name="gpt-35-turbo-16k",  
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2024-10-21"
    )

    # Configuración del modelo para generar el SQL estructurado
    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm

    # Generar la consulta SQL
    result = sql_generator.invoke({"question": question})
    
    # Guardar la consulta SQL generada en el estado
    state.sql_query = result.sql_query
    print(f"Generated SQL query: {state.sql_query}")

    # Actualizar el historial de la sesión con la nueva pregunta
    session_history.append(question)

    # Limitar el historial a un máximo de 5 elementos
    if len(session_history) > 5:
        session_history = session_history[-5:]  # Mantener solo los últimos 5 elementos

    # Guardar el historial de vuelta en la base de datos o en memoria para esa sesión
    save_session_history(uuid_sesion, session_history)

    # Mostrar el historial actualizado en los logs
    print(f"Session History: {uuid_sesion}")
    print(session_history)

    return state


def execute_sql(state: AgentState):
    print("execute_sql")
    sql_query = state.sql_query.strip()
    session = SessionLocal()
    print(f"Executing SQL query: {sql_query}")
    
    try:
        # Verificar si la consulta es de tipo DROP, INSERT, DELETE o UPDATE
        if any(sql_query.lower().startswith(command) for command in ["insert", "delete", "update", "drop"]):
            print("Detected potentially dangerous query (INSERT, DELETE, UPDATE, or DROP). Redirecting to regenerate_query.")
            # Llamar a regenerate_query en lugar de ejecutar la consulta
            state.query_result = {
                "content": "Detected potentially dangerous query (INSERT, DELETE, UPDATE, or DROP). Redirecting to regenerate_query."
            }
            state.sql_error = True
            return state

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
            
            # Verificar la longitud de la respuesta
            if len(str(formatted_result)) > 500:
                print("Result exceeds 500 characters. Redirecting to regenerate_query.")
                state.query_result = {
                    "content": "Result exceeds 500 characters. Redirecting to regenerate_query."
                }
                state.sql_error = True
                return state
                
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
    print("generate_human_readable_answer")
    print(state.query_result)
    # Comprobar si la respuesta generada excede los 500 caracteres
    if not state.query_result or len(state.query_result) > 500 or len(state.query_result) == 0:
        # Si la consulta no tiene resultados o es demasiado larga, asignamos el mensaje predeterminado
        state.query_result = "No existen resultados para la búsqueda o es demasiado larga la respuesta. Haga una pregunta más precisa, por favor."
        return state

    # Generar un mensaje con IA para interpretar los datos
    natural_language_prompt = f"""
        Proporciona una respuesta en lenguaje natural de los siguientes datos: {state.query_result}. Organizando claramente los datos, utiliza enumeraciones en caso de ser necesario, negritas, etc
        Tiene que responder a la pregunta: {state.question}
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
    print(state)
    return state


def regenerate_query(state: AgentState):
    print("regenerate_query")
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
    print("alert_not_relevant_results")
    state.query_result = {
        "content": "No existen resultados para la búsqueda o es demasiado larga la respuesta. Haga una pregunta más precisa, por favor."
    }
    return state

def end_max_iterations(state: AgentState):
    print("end_max_iterations")
    state.query_result = {
        "content": "No existen resultados para la búsqueda o es demasiado larga la respuesta. Haga una pregunta más precisa, por favor."
    }
    print("Maximum attempts reached. Ending the workflow.")
    return state

def relevance_router(state: AgentState):
    print("relevance_router")
    if state.relevance.lower() == "relevant":
        return "convert_to_sql"
    else:
        return "alert_not_relevant_results"

def check_attempts_router(state: AgentState):
    print("check_attempts_router")
    print(state)
    print("state attemps")
    print(state.attempts)
    if state.attempts < 3:
        return "convert_to_sql"
    else:
        return "end_max_iterations"
    
def execute_sql_router(state: AgentState):
    print("execute_sql_router")
    # Acceder directamente al atributo sql_error
    if not state.sql_error:  # Esto es equivalente a comprobar si sql_error es False o None
        return "generate_human_readable_answer"
    else:
        return "regenerate_query"
