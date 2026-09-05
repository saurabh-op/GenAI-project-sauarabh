from app.agents.review_graph import review_graph
result=review_graph.invoke({
    "paper_id":"30105286-7ee1-417b-9401-5f0344a3168d"
})

print("\n===== FINAL RESEARCH REVIEW =====")
print(result["final_review"])