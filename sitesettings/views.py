# views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated   # ← change here
from rest_framework.response import Response
from .models import RequestQuote
from .serializers import RequestQuoteSerializer
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class RequestQuoteViewSet(viewsets.ModelViewSet):
    queryset = RequestQuote.objects.all()
    serializer_class = RequestQuoteSerializer
    permission_classes = [IsAuthenticated]  

    def perform_create(self, serializer):
        """Automatically set email from the authenticated user"""
        serializer.save(email=self.request.user.email)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        try:
            self._send_admin_notification(serializer.data, request.user)
            print("Admin email sent successfully")
        except Exception as e:
            print(f"Email error — {type(e).__name__}: {e}")

        return Response({
            "success": True,
            "message": "Request quote created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def _send_admin_notification(self, data, user):
        subject = "New Quote Request Received"

        email = user.email           
        text = data.get('text', '').strip() or '(no message provided)'

        user_full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        text_message = f"""New Quote Request

From: {user_full_name}
Email: {email}
Message:
{text}
"""

        html_message = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>New Quote Request</title>
</head>
<body style="margin:0;padding:0;background-color:#0f0f0f;font-family:'Georgia',serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#0f0f0f;padding:48px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#1a1a1a;border-radius:2px;overflow:hidden;border:1px solid #2a2a2a;">

        <tr><td style="background:linear-gradient(90deg,#c8a96e 0%,#e8c97e 50%,#c8a96e 100%);height:4px;font-size:0;line-height:0;">&nbsp;</td></tr>

        <tr>
          <td style="padding:40px 48px 32px;border-bottom:1px solid #2a2a2a;">
            <div style="display:inline-block;background:linear-gradient(135deg,#c8a96e,#e8c97e);width:42px;height:42px;border-radius:2px;text-align:center;line-height:42px;font-size:20px;font-weight:bold;color:#0f0f0f;font-family:'Georgia',serif;margin-bottom:20px;">Q</div>
            <p style="margin:0 0 6px;font-size:11px;letter-spacing:4px;color:#c8a96e;text-transform:uppercase;font-family:'Courier New',monospace;">Incoming Request</p>
            <h1 style="margin:0;font-size:28px;font-weight:normal;color:#f5f0e8;letter-spacing:-0.5px;font-family:'Georgia',serif;line-height:1.2;">New Quote Request</h1>
          </td>
        </tr>

        <tr>
          <td style="padding:36px 48px;">
            <p style="margin:0 0 32px;font-size:14px;color:#888;font-family:'Courier New',monospace;letter-spacing:1px;">
              A new quote request from a registered user. Details below.
            </p>

            <table width="100%" cellpadding="0" cellspacing="0" border="0">

              <!-- User & Email -->
              <tr>
                <td style="padding:0 0 20px;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#222;border-left:3px solid #c8a96e;border-radius:0 2px 2px 0;">
                    <tr>
                      <td style="padding:16px 20px;">
                        <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;color:#c8a96e;text-transform:uppercase;font-family:'Courier New',monospace;">User</p>
                        <p style="margin:0;font-size:17px;color:#f5f0e8;font-family:'Georgia',serif;">{user_full_name}</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <tr>
                <td style="padding:0 0 20px;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#222;border-left:3px solid #c8a96e;border-radius:0 2px 2px 0;">
                    <tr>
                      <td style="padding:16px 20px;">
                        <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;color:#c8a96e;text-transform:uppercase;font-family:'Courier New',monospace;">Email</p>
                        <p style="margin:0;font-size:17px;color:#f5f0e8;font-family:'Georgia',serif;">
                          <a href="mailto:{email}" style="color:#c8a96e;text-decoration:none;">{email}</a>
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Message -->
              <tr>
                <td style="padding:0 0 0;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#1e1e1e;border:1px solid #2e2e2e;border-radius:2px;">
                    <tr>
                      <td style="padding:20px;">
                        <p style="margin:0 0 10px;font-size:10px;letter-spacing:3px;color:#888;text-transform:uppercase;font-family:'Courier New',monospace;">Message</p>
                        <p style="margin:0;font-size:15px;color:#ccc;font-family:'Georgia',serif;line-height:1.7;white-space:pre-wrap;">{text}</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

            </table>

            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:36px;">
              <tr>
                <td>
                  <a href="mailto:{email}" style="display:inline-block;background:linear-gradient(135deg,#c8a96e,#e8c97e);color:#0f0f0f;text-decoration:none;padding:14px 32px;border-radius:2px;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-family:'Courier New',monospace;font-weight:bold;">
                    Reply to User
                  </a>
                </td>
              </tr>
            </table>

          </td>
        </tr>

        <tr>
          <td style="padding:24px 48px;border-top:1px solid #2a2a2a;background-color:#141414;">
            <p style="margin:0;font-size:11px;color:#444;font-family:'Courier New',monospace;letter-spacing:1px;">
              This is an automated notification. Do not reply to this email directly.<br/>
              © 2026 Michael Milne — Admin Notifications
            </p>
          </td>
        </tr>

        <tr><td style="background:linear-gradient(90deg,#c8a96e 0%,#e8c97e 50%,#c8a96e 100%);height:2px;font-size:0;line-height:0;">&nbsp;</td></tr>

      </table>
    </td></tr>
  </table>

</body>
</html>"""

        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,  
            to=[settings.ADMIN_EMAIL],
            reply_to=[email],                      
        )

        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)