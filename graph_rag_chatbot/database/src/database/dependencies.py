from fastapi import Request

def get_graph(request: Request):
    return request.app.state.graph

def get_llm(request: Request):
    return request.app.state.llm