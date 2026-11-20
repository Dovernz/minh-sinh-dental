import base64
import hashlib
import hmac
import json
import time
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect

User = get_user_model()

# List of allowed permissions for SSO to WordPress
SSO_PERMISSIONS = [
    'booking.manage_wordpress_posts',
    'booking.view_article',
    'booking.add_article',
    'booking.change_article',
    'booking.view_marketingarticle',
]

# HTML Template for Access Denied / Invalid Token (Minh Sinh Dental Branding)
DENIED_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Truy Cập Bị Từ Chối - Nha Khoa Minh Sinh</title>
    <style>
        :root {{
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --error-bg: #fef2f2;
            --error-border: #fecaca;
            --error-text: #dc2626;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 1.5rem;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            max-width: 480px;
            width: 100%;
            padding: 2.5rem 2rem;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .icon-box {{
            width: 4rem;
            height: 4rem;
            background-color: var(--error-bg);
            border: 1px solid var(--error-border);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            color: var(--error-text);
        }}
        .icon-box svg {{
            width: 2rem;
            height: 2rem;
        }}
        h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 0.75rem;
        }}
        p {{
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1.75rem;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: var(--primary);
            color: #ffffff;
            font-weight: 600;
            font-size: 0.9rem;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            text-decoration: none;
            transition: background-color 0.2s ease-in-out;
        }}
        .btn:hover {{
            background-color: var(--primary-dark);
        }}
        .footer-brand {{
            margin-top: 2rem;
            font-size: 0.75rem;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
        </div>
        <h1>Truy Cập Bị Từ Chối</h1>
        <p>{message}</p>
        <a href="/admin/" class="btn">Quay lại Trang Quản Trị</a>
        <div class="footer-brand">Nha Khoa Minh Sinh &bull; SSO Security</div>
    </div>
</body>
</html>
"""


def _render_403_response(message: str) -> HttpResponseForbidden:
    """Helper to return a styled Vietnamese 403 response."""
    return HttpResponseForbidden(DENIED_HTML_TEMPLATE.format(message=message))


def _urlsafe_b64decode(s: str) -> bytes:
    """Helper to decode base64 urlsafe string with optional padding."""
    padding = '=' * (4 - (len(s) % 4))
    return base64.urlsafe_b64decode(s + padding)


@login_required(login_url='/admin/login/')
def sso_to_wordpress_view(request: HttpRequest) -> HttpResponse:
    """
    Generate SSO token and redirect from Django Unfold Admin to WordPress.
    """
    user = request.user

    # Permission check: superuser, staff, or specific permissions
    has_access = (
        user.is_superuser
        or user.is_staff
        or any(user.has_perm(perm) for perm in SSO_PERMISSIONS)
    )

    if not has_access:
        return _render_403_response(
            "Tài khoản của bạn không có quyền truy cập vào hệ thống WordPress Quản trị."
        )

    wp_role = 'administrator' if user.is_superuser else 'editor'
    target = request.GET.get('target', 'index.php')
    secret_key = getattr(
        settings, 'SSO_SECRET_KEY', 'minhsinh_dental_sso_secure_key_2026'
    )

    payload = {
        'u': user.username,
        'e': user.email or f'{user.username}@minhsinh.vn',
        'r': wp_role,
        't': target,
        'exp': int(time.time()) + 60,
        'nonce': uuid.uuid4().hex[:12],
    }

    # Encode payload to base64 urlsafe without padding '='
    json_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(json_bytes).decode('utf-8').rstrip('=')

    # Generate HMAC SHA256 signature
    sig = hmac.new(
        secret_key.encode('utf-8'),
        b64_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    token = f'{b64_payload}.{sig}'

    # Target WordPress site URL configuration
    wp_site_url = getattr(settings, 'WORDPRESS_URL', '').rstrip('/')
    redirect_url = f'{wp_site_url}/?minhsinh_sso={token}' if wp_site_url else f'/?minhsinh_sso={token}'

    return HttpResponseRedirect(redirect_url)


def sso_login_from_wordpress_view(request: HttpRequest) -> HttpResponse:
    """
    Authenticate user into Django Unfold Admin using token from WordPress.
    """
    token = request.GET.get('token')
    if not token or '.' not in token:
        return _render_403_response("Mã xác thực SSO không hợp lệ hoặc thiếu thông tin.")

    b64_payload, sig = token.rsplit('.', 1)
    secret_key = getattr(
        settings, 'SSO_SECRET_KEY', 'minhsinh_dental_sso_secure_key_2026'
    )

    # Validate HMAC signature
    expected_sig = hmac.new(
        secret_key.encode('utf-8'),
        b64_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        return _render_403_response("Chữ ký xác thực SSO không chính xác.")

    # Decode payload
    try:
        payload_bytes = _urlsafe_b64decode(b64_payload)
        payload = json.loads(payload_bytes.decode('utf-8'))
    except Exception:
        return _render_403_response("Dữ liệu xác thực SSO bị lỗi hoặc hỏng.")

    # Validate token expiration
    exp = payload.get('exp', 0)
    if int(exp) <= int(time.time()):
        return _render_403_response("Phiên đăng nhập SSO đã hết hạn. Vui lòng thử lại.")

    username = payload.get('u')
    email = payload.get('e')
    is_su = bool(payload.get('is_su', False) or payload.get('r') == 'administrator')

    if not username:
        return _render_403_response("Thiếu tên người dùng trong dữ liệu SSO.")

    # Query User by username, then email
    user = User.objects.filter(username=username).first()
    if not user and email:
        user = User.objects.filter(email=email).first()

    # Create user if does not exist
    if not user:
        user = User.objects.create_user(
            username=username,
            email=email or f'{username}@minhsinh.vn',
            password=None
        )

    # Ensure user staff and superuser permissions
    user.is_staff = True
    if is_su:
        user.is_superuser = True
    user.save()

    # Authenticate and log in user
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return HttpResponseRedirect('/admin/')