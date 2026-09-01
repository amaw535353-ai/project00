let token = null;
const output = document.querySelector("#output");
document.querySelector("#login").addEventListener("click", async () => {
  const response = await fetch("/api/auth/login", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:document.querySelector("#username").value,password:document.querySelector("#password").value})});
  const data = await response.json();
  if (!response.ok) { output.textContent = data.detail || "Sign-in failed"; return; }
  token = data.access_token; document.querySelector("#password").value = ""; document.querySelector("#send").disabled = false; output.textContent = "Signed in.";
});
document.querySelector("#send").addEventListener("click", async () => {
  const response = await fetch("/api/chat", {method:"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify({message:document.querySelector("#message").value})});
  const data = await response.json();
  // textContent is intentional: model output is never interpreted as HTML.
  output.textContent = response.ok ? data.response : (data.detail || "Request failed");
});
