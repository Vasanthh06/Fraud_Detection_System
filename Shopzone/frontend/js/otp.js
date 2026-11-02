async function requestOtp(email, purpose) {
  return API.post('/otp/send', { email, purpose });
}
function showOtpModal({ email, purpose, onVerified }) {
  if (document.getElementById('otpModal')) return;
  const wrap = document.createElement('div');
  wrap.id = 'otpModal';
  wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.55);display:grid;place-items:center;z-index:9999';
  wrap.innerHTML = `
    <div style="background:var(--card,#fff);color:inherit;padding:24px;border-radius:14px;width:340px;max-width:92vw;box-shadow:0 20px 60px rgba(0,0,0,.4)">
      <h3 style="margin:0 0 8px">Verify your email</h3>
      <p style="margin:0 0 16px;font-size:14px;opacity:.8">We sent a 6-digit code to <b>${email}</b> for <b>${purpose}</b>.</p>
      <input id="otpCode" inputmode="numeric" maxlength="6" style="width:100%;padding:10px;font-size:22px;letter-spacing:8px;text-align:center;border-radius:10px;border:1px solid #ccc" placeholder="••••••" />
      <div id="otpErr" style="color:#e11d48;font-size:13px;margin-top:8px;display:none"></div>
      <div style="display:flex;gap:8px;margin-top:14px">
        <button id="otpCancel" style="flex:1;padding:10px;border-radius:10px;border:1px solid #ccc;background:transparent;color:inherit;cursor:pointer">Cancel</button>
        <button id="otpResend" style="flex:1;padding:10px;border-radius:10px;border:1px solid #ccc;background:transparent;color:inherit;cursor:pointer" disabled>Resend (30s)</button>
        <button id="otpOk" style="flex:1;padding:10px;border-radius:10px;border:none;background:#10b981;color:#04121a;font-weight:700;cursor:pointer">Verify</button>
      </div>
    </div>`;
  document.body.appendChild(wrap);
  const codeEl = wrap.querySelector('#otpCode');
  const errEl  = wrap.querySelector('#otpErr');
  const okBtn  = wrap.querySelector('#otpOk');
  const rsBtn  = wrap.querySelector('#otpResend');
  const cancel = wrap.querySelector('#otpCancel');
  codeEl.focus();
  let seconds = 30;
  const tick = setInterval(() => {
    seconds -= 1;
    if (seconds <= 0) { clearInterval(tick); rsBtn.disabled = false; rsBtn.textContent = 'Resend'; }
    else { rsBtn.textContent = `Resend (${seconds}s)`; }
  }, 1000);
  const close = () => { clearInterval(tick); wrap.remove(); };
  cancel.onclick = close;
  rsBtn.onclick = async () => {
    rsBtn.disabled = true; seconds = 30; rsBtn.textContent = `Resend (${seconds}s)`;
    try { await requestOtp(email, purpose); } catch (e) { errEl.textContent = e.message; errEl.style.display = 'block'; }
  };
  okBtn.onclick = async () => {
    errEl.style.display = 'none';
    const code = codeEl.value.trim();
    if (!/^\d{6}$/.test(code)) { errEl.textContent = 'Enter the 6-digit code.'; errEl.style.display = 'block'; return; }
    okBtn.disabled = true; okBtn.textContent = 'Verifying…';
    try {
      const res = await API.post('/otp/verify', { email, code, purpose });
      close(); onVerified(res.otp_token);
    } catch (e) {
      errEl.textContent = e.message; errEl.style.display = 'block';
      okBtn.disabled = false; okBtn.textContent = 'Verify';
    }
  };
}