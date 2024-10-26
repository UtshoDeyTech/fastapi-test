from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables with default values
TITLE = os.getenv("TITLE", "Todo API")
DESCRIPTION = os.getenv("DESCRIPTION", "A simple FastAPI Todo application")

app = FastAPI(title=TITLE, description=DESCRIPTION)

# Pydantic models for request/response
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1

class Todo(TodoCreate):
    id: str
    created_at: datetime
    completed: bool = False

# In-memory storage
todos = {}

# Dependency for getting a todo by ID
async def get_todo_by_id(todo_id: str):
    todo = todos.get(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    return todo

@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    """Create a new todo item"""
    todo_id = str(uuid.uuid4())
    new_todo = Todo(
        id=todo_id,
        created_at=datetime.now(),
        **todo.model_dump()  # Updated from dict() to model_dump()
    )
    todos[todo_id] = new_todo
    return new_todo

@app.get("/todos/", response_model=List[Todo])
async def list_todos():
    """Get all todos"""
    return list(todos.values())

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo: Todo = Depends(get_todo_by_id)):
    """Get a specific todo by ID"""
    return todo

@app.patch("/todos/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: str,
    update_data: TodoCreate,
    todo: Todo = Depends(get_todo_by_id)
):
    """Update a todo item"""
    updated_todo = Todo(
        id=todo.id,
        created_at=todo.created_at,
        completed=todo.completed,
        **update_data.model_dump(exclude_unset=True)  # Updated from dict() to model_dump()
    )
    todos[todo_id] = updated_todo
    return updated_todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo: Todo = Depends(get_todo_by_id)):
    """Delete a todo item"""
    todos.pop(todo.id)
    return None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Todo API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)