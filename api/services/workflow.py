from db.schemas import AgentState
from services.utils import (
    check_relevance,
    convert_nl_to_sql,
    execute_sql,
    generate_human_readable_answer,
    regenerate_query,
    alert_not_relevant_results,
    end_max_iterations,
    relevance_router,
    execute_sql_router,
    check_attempts_router
)
from langgraph.graph import StateGraph

# Definir el flujo de trabajo
workflow = StateGraph(AgentState)

workflow.add_node("check_relevance", check_relevance)
workflow.add_node("convert_to_sql", convert_nl_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("alert_not_relevant_results", alert_not_relevant_results)
workflow.add_node("end_max_iterations", end_max_iterations)

workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "convert_to_sql": "convert_to_sql",
        "alert_not_relevant_results": "alert_not_relevant_results",
    },
)

workflow.add_edge("convert_to_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    execute_sql_router,
    {
        "generate_human_readable_answer": "generate_human_readable_answer",
        "regenerate_query": "regenerate_query",
    },
)

workflow.add_conditional_edges(
    "regenerate_query",
    check_attempts_router,
    {
        "convert_to_sql": "convert_to_sql",
        "end_max_iterations": "end_max_iterations",
    },
)

# Establecer nodos de finalización en lugar de "END"
workflow.set_finish_point("generate_human_readable_answer")
workflow.set_finish_point("alert_not_relevant_results")
workflow.set_finish_point("end_max_iterations")

workflow.set_entry_point("check_relevance")

# Compilar el workflow
app_workflow = workflow.compile()
