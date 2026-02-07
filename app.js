// Counter
const counterEl = document.getElementById("counter");
const incrementBtn = document.getElementById("increment");
const decrementBtn = document.getElementById("decrement");
const resetBtn = document.getElementById("reset");

let count = 0;

function updateCounter() {
  counterEl.textContent = count;
}

incrementBtn.addEventListener("click", () => { count++; updateCounter(); });
decrementBtn.addEventListener("click", () => { count--; updateCounter(); });
resetBtn.addEventListener("click", () => { count = 0; updateCounter(); });

// Notes
const noteForm = document.getElementById("note-form");
const noteInput = document.getElementById("note-input");
const noteList = document.getElementById("note-list");
const emptyMsg = document.getElementById("empty-msg");

function updateEmptyMsg() {
  emptyMsg.style.display = noteList.children.length === 0 ? "block" : "none";
}

noteForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = noteInput.value.trim();
  if (!text) return;

  const li = document.createElement("li");
  li.innerHTML = `<span>${escapeHtml(text)}</span><button class="delete-btn" title="Delete">&times;</button>`;
  li.querySelector(".delete-btn").addEventListener("click", () => {
    li.remove();
    updateEmptyMsg();
  });

  noteList.appendChild(li);
  noteInput.value = "";
  updateEmptyMsg();
});

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
