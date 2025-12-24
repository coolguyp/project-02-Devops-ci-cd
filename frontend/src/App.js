import React, { useEffect, useState } from "react";
import { getTodos, addTodo } from "./api";

function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");

  const loadTodos = async () => {
    const data = await getTodos();
    setTodos(data);
  };

  useEffect(() => {
    loadTodos();
  }, []);

  const handleAdd = async () => {
    if (!title) return;
    await addTodo(title);
    setTitle("");
    loadTodos();
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>📝 DevOps To-Do App version_1</h1>

      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="New task"
      />
      <button onClick={handleAdd}>Add</button>

      <ul>
        {todos.map((t) => (
          <li key={t.id}>{t.title}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
