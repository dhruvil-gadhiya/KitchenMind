// minor UX: pressing Enter inside search input submits form; nothing heavy
document.addEventListener('DOMContentLoaded', function(){
  const searchBox = document.getElementById('search-box');
  if(searchBox){
    searchBox.addEventListener('keydown', function(e){
      if(e.key === 'Enter'){
        // allow form submit
      }
    });
  }

  // Password visibility toggles
  document.querySelectorAll('[data-toggle-password]').forEach(function(toggle){
    const targetId = toggle.getAttribute('data-toggle-password');
    const input = document.getElementById(targetId);
    if(!input) return;
    toggle.addEventListener('click', function(){
      input.type = (input.type === 'password') ? 'text' : 'password';
    });
  });

  // Resend OTP button handler only

  document.querySelectorAll('[data-send-otp]').forEach(function(link){
    link.addEventListener('click', function(e){
      e.preventDefault();
      const form = link.closest('form');
      if(!form) return;
      const emailField = form.querySelector('input[name="email"]');
      const email = (emailField && emailField.value || '').trim();
      if(!email){
        const statusEl = document.getElementById('otp-status');
        if(statusEl){ statusEl.textContent = 'Enter email first'; }
        return;
      }
      const kind = link.getAttribute('data-send-otp');
      const fd = new FormData();
      fd.append('email', email);
      fd.append('kind', kind);
      fetch('/send_otp', { method: 'POST', body: fd }).then(function(r){ return r.json(); }).then(function(res){
        const statusEl = document.getElementById('otp-status');
        if(statusEl){ statusEl.textContent = res.ok ? 'OTP sent' : (res.message || 'Failed to send OTP'); }
      }).catch(function(){});
    });
  });
});
