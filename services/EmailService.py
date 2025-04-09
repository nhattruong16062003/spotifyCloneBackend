from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_custom_email(subject, username, message, link=None, recipient_email=None, template_name='email_template.html'):
    """
    Hàm gửi email với template HTML.
    
    Args:
        subject (str): Tiêu đề email
        username (str): Tên người dùng
        message (str): Nội dung thông điệp
        link (str, optional): Link (nếu có)
        recipient_email (str): Email người nhận
        template_name (str): Tên file template (mặc định: email_template.html)
    
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    try:
        # Dữ liệu để truyền vào template
        context = {
            'subject': subject,
            'username': username,
            'message': message,
            'link': link,
        }
        
        # Render template thành chuỗi HTML
        email_body = render_to_string(template_name, context)
        
        # Tạo và gửi email
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.content_subtype = 'html'
        email.send()
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        return False