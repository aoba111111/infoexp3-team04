async function loadMessages(){
  const r = await fetch('/api/messages');
  const xs = await r.json();
  
  document.querySelector('#messages').innerHTML = xs.map(x => `
    <article class="message" style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
      <b>${escapeHtml(x.name)}</b>
      <p style="font-weight: bold; color: #d9534f;">言い値: ${escapeHtml(String(x.price))}円</p>
      <img src="${escapeHtml(x.photo_path)}" style="max-width: 200px; display: block; margin-top: 10px; margin-bottom: 10px;">
      
      <!-- グッドボタンを追加 -->
      <button class="like-btn" data-id="${x.id}" style="margin-bottom: 10px; cursor: pointer;">
        👍 グッド ${x.likes}
      </button>

      <div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">
        <h4 style="margin: 0 0 10px 0; font-size: 0.9em; color: #555;">💬 コメント</h4>
        ${x.comments.map(c => `
          <div style="font-size: 0.85em; margin-bottom: 5px; border-bottom: 1px dashed #ccc; padding-bottom: 5px;">
            <strong>${escapeHtml(c.commenter_name)}:</strong> ${escapeHtml(c.comment_text)}
          </div>
        `).join('')}
        
        <form class="comment-form" data-id="${x.id}" style="margin-top: 10px; display: flex; gap: 5px;">
          <input type="text" class="c-name" placeholder="名前" required style="width: 60px; padding: 2px;">
          <input type="text" class="c-text" placeholder="コメント..." required style="flex-grow: 1; padding: 2px;">
          <button type="submit" style="padding: 2px 10px;">送信</button>
        </form>
      </div>
      
    </article>
  `).join('');
}

function escapeHtml(s){
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

document.querySelector('#form').addEventListener('submit', async e => {
  e.preventDefault();
  const name = document.querySelector('#name').value;
  const price = document.querySelector('#price').value;
  const photo = document.querySelector('#photo').files[0];

  const formData = new FormData();
  formData.append('name', name);
  formData.append('price', price);
  formData.append('photo', photo);

  const r = await fetch('/api/messages', {
    method: 'POST',
    body: formData
  });

  document.querySelector('#status').textContent = r.ok ? '投稿しました' : '投稿に失敗しました';
  if (r.ok) {
    document.querySelector('#name').value = '';
    document.querySelector('#price').value = '';
    document.querySelector('#photo').value = '';
    await loadMessages();
  }
});

// コメント送信とグッドボタンのクリック処理をまとめる
document.querySelector('#messages').addEventListener('click', async e => {
  // グッドボタンが押された場合
  if(e.target.classList.contains('like-btn')) {
    const messageId = e.target.getAttribute('data-id');
    const r = await fetch(`/api/messages/${messageId}/like`, {
      method: 'POST'
    });
    if (r.ok) {
      await loadMessages();
    }
  }
});

// コメントフォームの送信処理
document.querySelector('#messages').addEventListener('submit', async e => {
  if(e.target.classList.contains('comment-form')) {
    e.preventDefault();
    const form = e.target;
    const messageId = form.getAttribute('data-id');
    const name = form.querySelector('.c-name').value;
    const text = form.querySelector('.c-text').value;

    const r = await fetch(`/api/messages/${messageId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name, text: text })
    });

    if (r.ok) {
      await loadMessages();
    } else {
      alert('コメントの送信に失敗しました');
    }
  }
});

loadMessages();