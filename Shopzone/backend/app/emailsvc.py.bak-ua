"""Transactional email via the Resend API — fully automatic (server-triggered).

Flows: welcome (register) · receipt (purchase) · fraud alert (blocked payment) ·
password-changed confirmation · password-reset link.

* With RESEND_API_KEY set  → POST https://api.resend.com/emails (real delivery).
* Without a key (dev)     → emails are written to data/outbox/*.eml so you can
  inspect exactly what would be sent. Nothing ever breaks a request: sending
  happens in a background thread and failures are logged, never raised.
"""
import html
import json
import logging
import threading
import urllib.request
from datetime import datetime
from pathlib import Path

from .config import APP_URL, DATA_DIR, RESEND_API_KEY, RESEND_FROM

logger = logging.getLogger("shopzone.mail")

OUTBOX = DATA_DIR / "outbox"


# ------------------------------------------------------------------ transport

def _post_resend(payload: dict) -> dict:
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.load(res)


def send_email(to: str, subject: str, html_body: str) -> dict:
    """Fire-and-forget safe: returns status dict, never raises."""
    try:
        if RESEND_API_KEY:
            out = _post_resend({
                "from": RESEND_FROM,
                "to": [to],
                "subject": subject,
                "html": html_body,
            })
            logger.info("email sent via Resend to %s (%s)", to, out.get("id"))
            return {"sent": True, "id": out.get("id")}
        OUTBOX.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        safe = "".join(c if c.isalnum() or c in ".@_-" else "_" for c in to)
        f = OUTBOX / f"{stamp}-{safe}.eml"
        f.write_text(f"From: {RESEND_FROM}\nTo: {to}\nSubject: {subject}\n\n{html_body}\n")
        logger.info("dev outbox: %s", f.name)
        return {"sent": False, "outbox": f.name}
    except Exception as exc:  # never break the user request for email
        logger.error("email to %s failed: %s", to, exc)
        return {"sent": False, "error": str(exc)}


def send_async(to: str, subject: str, html_body: str) -> None:
    threading.Thread(target=send_email, args=(to, subject, html_body), daemon=True).start()


# ------------------------------------------------------------------ layout

def _layout(title: str, preheader: str, body_html: str) -> str:
    return f"""<!doctype html>
<html><body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',system-ui,Arial,sans-serif;color:#0f172a">
<div style="display:none;max-height:0;overflow:hidden">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 12px">
 <tr><td align="center">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0">
   <tr><td style="background:linear-gradient(120deg,#059669,#0284c7);padding:26px 32px">
     <table role="presentation" width="100%"><tr>
       <td style="color:#ffffff;font-size:22px;font-weight:800;letter-spacing:-.02em">🛍️ Shop<span style="color:#d1fae5">Zone</span></td>
       <td align="right" style="color:#e2e8f0;font-size:12px">Secure commerce · ML fraud shield</td>
     </tr></table>
   </td></tr>
   <tr><td style="padding:34px 36px">
     <h1 style="margin:0 0 6px;font-size:23px;letter-spacing:-.02em">{title}</h1>
     <p style="margin:0 0 22px;color:#64748b;font-size:13.5px">{preheader}</p>
     {body_html}
   </td></tr>
   <tr><td style="padding:20px 36px;background:#f8fafc;border-top:1px solid #e2e8f0;color:#94a3b8;font-size:12px;line-height:1.7">
     This is an automated message from your ShopZone account.<br>
     ShopZone · Secure e-commerce with real-time fraud detection · <a href="{APP_URL}" style="color:#059669">{APP_URL}</a>
   </td></tr>
  </table>
 </td></tr>
</table>
</body></html>"""


def _btn(href: str, label: str) -> str:
    return (f'<a href="{href}" style="display:inline-block;background:#059669;color:#ffffff;'
            f'padding:12px 26px;border-radius:10px;font-weight:700;font-size:14px;'
            f'text-decoration:none">{label}</a>')


def _kv(rows: list[tuple[str, str]]) -> str:
    cells = "".join(
        f'<tr><td style="padding:9px 0;color:#64748b;font-size:13.5px;width:150px">{k}</td>'
        f'<td style="padding:9px 0;font-size:13.5px;font-weight:600">{v}</td></tr>'
        for k, v in rows)
    return f'<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;border:1px solid #e2e8f0;border-radius:12px;padding:6px 18px;margin:0 0 22px">{cells}</table>'


# ------------------------------------------------------------------ templates

def welcome_email(name: str, email: str) -> tuple[str, str]:
    e = html.escape
    body = f"""
<p style="font-size:15px;line-height:1.65;margin:0 0 18px">Hi <b>{e(name)}</b>, welcome to the future of secure shopping!</p>
<p style="font-size:15px;line-height:1.65;margin:0 0 18px">Your ShopZone account is officially active. We combine advanced Machine Learning with real-time rule engines to keep your transactions completely safe.</p>
{_kv([("Account email", e(email)), ("Member since", datetime.now().strftime("%d %b %Y")), ("Account status", "✅ Active & protected")])}
<p style="font-size:14px;line-height:1.7;margin:0 0 24px">Here is what you can do right now:</p>
<ul style="margin:0 0 26px;padding-left:20px;font-size:14px;line-height:1.9;color:#334155">
  <li>Browse our exclusive collection of products</li>
  <li>Save your favourite items to your personal wishlist</li>
  <li>Checkout securely with our AI fraud shield</li>
  <li>Track all your orders in real-time from your dashboard</li>
</ul>
{_btn(APP_URL + '/shop', 'Start shopping →')}
<p style="font-size:12.5px;color:#94a3b8;margin:26px 0 0">Didn't create this account? Reset the password from the sign-in page or ignore this mail.</p>"""
    return "Welcome to ShopZone 🎉 — your account is ready", _layout("Welcome to ShopZone 🎉", "Your account is ready — protected by the ShopZone Shield.", body)


def receipt_email(name: str, txn_id: str, products: str, amount: str, status: str,
                  risk: str, card: str, email: str) -> tuple[str, str]:
    e = html.escape
    flag = "✅" if status == "Success" else "⚠️"
    body = f"""
<p style="font-size:15px;line-height:1.65;margin:0 0 18px">Hi <b>{e(name)}</b>, {flag} your payment was
<b>{e(status.lower())}</b> by the ShopZone fraud engine. A copy of this receipt is stored in your order history.</p>
{_kv([("Transaction ID", f"<span style='font-family:monospace'>{e(txn_id)}</span>"),
      ("Items", e(products)), ("Amount paid", e(amount)), ("Card", e(card)),
      ("Fraud verdict", f"{e(status)} · risk {e(risk)}"), ("Date", datetime.now().strftime("%d %b %Y, %H:%M"))])}
<p style="font-size:13.5px;color:#64748b;line-height:1.7;margin:0 0 24px">
{"Everything looked clean — thank you for shopping with ShopZone." if status == "Success" else "The engine noticed an unusual pattern on this order. It went through, but our team will keep an eye on it. If this was not you, change your password immediately."}</p>
{_btn(APP_URL + '/orders', 'View my orders →')}"""
    return f"ShopZone receipt · {txn_id} · {amount}", _layout("Payment confirmed ✅", f"Transaction {txn_id} · {status}", body)


def fraud_alert_email(name: str, txn_id: str, amount: str, risk: str, reason: str,
                      card: str) -> tuple[str, str]:
    e = html.escape
    body = f"""
<table role="presentation" width="100%" style="margin:0 0 20px"><tr><td style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:16px 18px;color:#b91c1c;font-size:14px;font-weight:700">
🚨 A payment on your account was BLOCKED by the fraud engine.</td></tr></table>
{_kv([("Transaction ID", f"<span style='font-family:monospace'>{e(txn_id)}</span>"),
      ("Attempted amount", e(amount)), ("Card", e(card)),
      ("Risk score", e(risk)), ("Reason", e(reason)), ("Time", datetime.now().strftime("%d %b %Y, %H:%M"))])}
<p style="font-size:14px;line-height:1.7;margin:0 0 24px">If this was you — no action is needed, the payment was simply declined.
If you do <b>not</b> recognise this attempt, change your password immediately and review your order history.</p>
{_btn(APP_URL + '/profile', 'Secure my account →')}"""
    return f"🚨 ShopZone security alert · blocked payment {txn_id}", _layout("Fraudulent payment blocked 🚨", f"We blocked a {amount} attempt on your account.", body)


def password_changed_email(name: str) -> tuple[str, str]:
    e = html.escape
    body = f"""
<p style="font-size:15px;line-height:1.65;margin:0 0 18px">Hi <b>{e(name)}</b>, the password on your ShopZone
account was just changed. If this was you, you're all set — use the new password next time you sign in.</p>
{_kv([("What changed", "Account password"), ("When", datetime.now().strftime("%d %b %Y, %H:%M")), ("Action needed", "None, if this was you")])}
<table role="presentation" width="100%" style="margin:0 0 20px"><tr><td style="background:#fffbeb;border:1px solid #fde68a;border-radius:12px;padding:16px 18px;color:#b45309;font-size:13.5px;line-height:1.6">
⚠️ <b>Didn't change your password?</b> Someone else may have access. Reset it immediately from the sign-in page (“Forgot password”) and check your order history.</td></tr></table>
{_btn(APP_URL + '/login', 'Go to sign-in →')}"""
    return "ShopZone · your password was changed", _layout("Password changed 🔐", "Your ShopZone password was updated.", body)


def reset_link_email(name: str, link: str) -> tuple[str, str]:
    e = html.escape
    body = f"""
<p style="font-size:15px;line-height:1.65;margin:0 0 18px">Hi <b>{e(name)}</b>,</p>
<p style="font-size:15px;line-height:1.65;margin:0 0 18px">We received a request to reset your password. Click the secure button below to choose a new one.</p>
<p style="font-size:14px;line-height:1.7;margin:0 0 22px;color:#b91c1c;"><b>Important:</b> This link is highly secure, valid for 60 minutes, and can only be used once.</p>
<div style="margin:0 0 22px;text-align:center">{_btn(link, 'Choose a new password →')}</div>
<p style="font-size:12.5px;color:#94a3b8;line-height:1.7;margin:0 0 8px">Button not working? Paste this link in your browser:<br>
<span style="font-family:monospace;color:#64748b;word-break:break-all">{e(link)}</span></p>
<p style="font-size:12.5px;color:#94a3b8;line-height:1.7;margin:0">Didn't ask for a reset? Ignore this email — your password stays unchanged and the link dies on its own.</p>"""
    return "ShopZone · reset your password", _layout("Password reset requested 🔑", "Your secure reset link is inside — valid for 60 minutes.", body)