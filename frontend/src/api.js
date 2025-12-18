const API_URL = "/api/todos";

export async function getTodos() {
  const res = await fetch(API_URL);
  return res.json();
}

export async function addTodo(title) {
  return fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
}
