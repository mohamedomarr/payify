import os
import requests
import urllib.parse
import re
import smtplib

from email.message import EmailMessage
from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/home")
        return f(*args, **kwargs)
    return decorated_function


# Make a regular email expression
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


# for validating an Email
def email_check(email):

    # pass the regualar expression
    # and the string in search() method
    if(re.search(regex, email)):
        return True

    else:
        return False



def reg_mail(toemail, name):   
    EMAIL_ADDRESS = 'payifypayments@gmail.com'
    EMAIL_PASSWORD = 'q23192322'

    msg = EmailMessage()
    msg['Subject'] = 'Registered!'
    msg['From'] = "Payify <EMAIL_ADDRESS>"
    msg['To'] = toemail

    msg.add_alternative(f"""\
    <!DOCTYPE html>
<html><head>
</head>
  <body data-gr-c-s-loaded="true" cz-shortcut-listen="true"><table cellspacing="0" cellpadding="0" align="center" width="520" style="background:#ffffff; min-width:520px">
    <tbody><tr>
      <td width="20" style="background:#eeeeee"></td>
        <td width="480">
        <table cellspacing="0" cellpadding="0" width="100%">
          <tbody><tr>
            <td height="20" style="background:#eeeeee"></td>
          </tr>
          
          <!-- header -->
          <tr>
            <td>
             <table cellspacing="0" cellpadding="0" width="100%" style="border-bottom:1px solid #eeeeee">
              <tbody><tr>
                <td height="49"></td>
               </tr>
               <tr>
               <td style="font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;color:#4285f4; font-size:32px;font-weight:normal;line-height:46px;margin:0;padding:0 25px;text-align:center;text-transform: capitalize;">Hi {name},</td>
               </tr>
               
                <tr><td height="20"></td></tr>
                
                <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px; font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;"> Thank you for creating a Payify Account. Here is some info to get started with your Payify account.</td></tr>
               <tr><td height="30"></td></tr>
               
             </tbody></table>
            </td>
          </tr>

          <!-- Bouns Header -->
          <tr>
              <td><table cellspacing="0" cellpadding="0" width="100%" style="border-bottom:1px solid #eeeeee">
                <tbody><tr><td height="30"></td></tr>
                <tr><td style="text-align:center;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;color:#757575; font-size:24px;font-weight:normal;line-height:33px;margin:0;padding:0 25px 0 25px;"><span style="color: #FFc30b;">$</span> Bonus <span style="color: #FFc30b;">$</span></td></tr>
                <tr><td height="4" style="line-height:4px;font-size:4px"></td></tr>
                  <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">Get 5000$ when you sign up isn't amazing !</td></tr>
                 <tr><td height="30"></td></tr>
               </tbody></table>
              </td>
          </tr>

          <!-- transfer money -->
          <tr>
            <td>
              <table cellspacing="0" cellpadding="0" width="100%" style="border-bottom:1px solid #eeeeee">
              <tbody><tr>
                <td height="30"></td>
               </tr>
               <tr>
                <td style="text-align:center;color:#757575; font-size:24px;font-weight:normal;line-height:33px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;">Transfer Money</td>
               </tr>
               <tr>
                <td height="4" style="line-height:4px;font-size:4px"></td>
               </tr>
               <tr>
                 <td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">You can Transfer Money by just a few clicks with the lowest transfer fees in the market only 1% per Transaction.</td>
               </tr>
               <tr>
                <td height="30"></td>
               </tr>
             </tbody></table>
            </td>
          </tr>

          <tr>
            <td>
              <table cellspacing="0" cellpadding="0" width="100%">
              <tbody>
               <tr><td height="30"></td></tr>
               
               <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">Enjoy your new account,</td></tr>
               <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">Payify Community Team</td></tr>
               <tr><td height="30"></td></tr>
               
               <tr><td width="134" height="46" align="center">
                  <span style="font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;font-size: xx-large;"><span style="color: #012169;">Pay</span><span style="color: #009CDE;">ify</span></span>
                </td></tr>
              <tr><td height="30"></td></tr>
            
              <tr><td height="19" style="background:#eeeeee"></td></tr>
               
            <tr>
               <td valign="middle" style="text-align:center;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;background:#eee;color:#777; font-size:10px;font-weight:normal;line-height:14px;margin:0;padding:0 6px 0 6px;">
                  © 2019 Payify a CS50 Final Project created By <a href="https://www.linkedin.com/in/msomar/">Mohamed Omar</a>, Egypt.<br>This email was sent to you because you created a Payify Account.</td>
               </tr>
             </tbody></table>
            </td>
          </tr>          
          <tr><td height="18" style="background:#eeeeee"></td></tr>
        </tbody></table>
      </td>
      <td width="20" style="background:#eeeeee"></td>
    </tr>
  </tbody></table>
</body></html>
    """, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        

def trans_mail(tomail, details, trans):
    EMAIL_ADDRESS = 'payifypayments@gmail.com'
    EMAIL_PASSWORD = 'q23192322'

    msg = EmailMessage()
    msg['Subject'] = trans['subject']
    msg['From'] = "Payify <EMAIL_ADDRESS>"
    msg['To'] = tomail

    msg.add_alternative(f"""\
    <!DOCTYPE html>
<html><head>
</head>
  <body><table cellspacing="0" cellpadding="0" align="center" width="520" style="background:#ffffff; min-width:520px">
    <tbody><tr>
      <td width="20" style="background:#eeeeee"></td>
      <td width="480">
      <table cellspacing="0" cellpadding="0" width="100%">
        <tbody><tr><td height="20" style="background:#eeeeee"></td></tr>
          
          <!-- header -->
          <tr><td><table cellspacing="0" cellpadding="0" width="100%" style="border-bottom:1px solid #eeeeee">
            <tbody>
              <tr><td height="49"></td></tr>
              <tr><td style="font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;color:#4285f4; font-size:32px;font-weight:normal;line-height:46px;margin:0;padding:0 25px;text-align:center;">Transaction details</td></tr>
               
              <tr><td height="20"></td></tr>
                
              <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px; font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">{details['first']} {details['last']} {trans['header']} you ‪{trans['gross']} USD‬</td></tr>
              <tr><td height="30"></td></tr>
               
            </tbody></table>
          </td></tr>

          <!-- Bouns Header -->
          <tr><td><table cellspacing="0" cellpadding="0" width="100%" style="border-bottom:1px solid #eeeeee">
            <tbody><tr><td height="30"></td></tr>
              <tr><td><div style="color:#757575; width: 100%; min-height: 1px; padding-left: 30px; text-align: left; line-height: 30px; font-size: 18px; font-weight: 400; font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;">
                
                <!-- Payment Recived or Sent (from/to) first and last name  -->
                <span><b>Payment
                    {trans['type']}
                  </b>
                    {trans['type2']}
                      <span style="color: #009CDE;">{details['first']} {details['last']}</span>
                  </span>
                  
                  <!-- email and datetime -->
                  <div><b>Email:</b> {details['email']}</div>
                  <div style="text-align: left;">{trans['date']} at {trans['time']}</div>
                  </div></td></tr>

                 <tr><td height="30"></td></tr>
               </tbody></table>
              </td>
          </tr>

          <!-- Your Payment Details -->
          <!-- header -->
          <tr><td><table cellspacing="0" cellpadding="0" width="100%" style="border-bottom:1px solid #eeeeee">
            <tbody><tr><td height="30"></td></tr>
              <tr><td style="text-align:center;color:#757575; font-size:24px;font-weight:normal;line-height:33px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;">Payment Details</td></tr>
                <tr><td height="20"></td></tr>
                
                <!-- details -->
                <tr><td>
                  <!-- Money Recived Row -->
                  <table width="100%" cellspacing="0" cellpadding="0" border="0" style="padding: 5px 30px">
                  <tbody>
                    <!-- money Recived text -->
                    <tr>
                      <td valign="top" width="70%">
                      <table align="left" cellpadding="0" cellspacing="0" border="0">
                        <tbody>
                          <tr><td valign="top" style="font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#444444"><div style="display:block">Money {trans['type']}</div></td></tr>
                        </tbody></table></td>
                              
                        <!-- amount money recived -->
                        <td valign="top" width="30%" align="right">
                          <table align="right" cellpadding="0" cellspacing="0" border="0">
                            <tbody><tr> 
                              <td align="right" valign="top" style="font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#333333">‪{trans['gross']}&nbsp;USD‬</td></tr>
                            </tbody></table></td></tr>
                    </tbody>
                    </table>
                        
                        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="padding: 5px 30px">
                            <tbody>
                                  <tr><td valign="top" width="70%">
                                <table align="left" cellpadding="0" cellspacing="0" border="0">
                                              <tbody><tr> 
                                                <!-- fee word -->
                                                <td valign="top" style="font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#444444"><div style="display:block">Fee</div></td>
                                                 
                                              </tr>
                                            </tbody></table>
                                          </td>
                                          <td valign="top" width="30%" align="right">
                                            <table align="right" cellpadding="0" cellspacing="0" border="0">
                                              <tbody><tr> 
                                                <!-- fee amount -->
                                                <td align="right" valign="top" style="font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#333333">‪{trans['fee']}&nbsp;USD‬</td>
                                                 
                                              </tr>
                                            </tbody></table>
                                         </td>
                                  </tr>
                                </tbody>
                            </table>

                            <table width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tbody>
                                      <tr>
                                  <td align="center" style="padding:10px 30px">
                                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                                  <tbody><tr> 
                                                    
                                                    <td align="center" valign="top" style="font-size:0px;line-height:0px;border-bottom:1px solid #d6d6d6">&nbsp;</td>
                                                     
                                                  </tr>
                                                </tbody></table>
                                            </td>
                                      </tr>
                                    </tbody>
                                </table>

                                <table width="100%" cellspacing="0" cellpadding="0" border="0" style="padding: 0px 30px">
                                    <tbody>
                                          <tr><td valign="top" width="70%">
                                        <table align="left" cellpadding="0" cellspacing="0" border="0">
                                                      <tbody><tr> 
                                                        <!-- total word -->
                                                        <td valign="top" style="font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#444444"><div style="display:block">Total</div></td>
                                                         
                                                      </tr>
                                                    </tbody></table>
                                                  </td>
                                                  <td valign="top" width="30%" align="right">
                                                    <table align="right" cellpadding="0" cellspacing="0" border="0">
                                                      <tbody><tr> 
                                                        <!-- total amount -->
                                                        <td align="right" valign="top" style="font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#333333">‪{trans['netcash']}&nbsp;USD‬</td>
                                                         
                                                      </tr>
                                                    </tbody></table>
                                                 </td>
                                          </tr>
                                        </tbody>
                                    </table>
                </td></tr>
                <tr><td height="30"></td></tr>
             </tbody></table>
            </td>
          </tr>
          <tr>
            <td>
              <table cellspacing="0" cellpadding="0" width="100%">
              <tbody>
               <tr><td height="30"></td></tr>
               
               <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">Enjoy your Day :)</td></tr>
               <tr><td style="color:#757575; font-size:17px;font-weight:normal;line-height:24px;margin:0;padding:0 25px 0 25px;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;text-align:center;">Payify Community Team</td></tr>
               <tr><td height="30"></td></tr>
               
               <tr><td width="134" height="46" align="center">
                  <span style="font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;font-size: xx-large;"><span style="color: #012169;">Pay</span><span style="color: #009CDE;">ify</span></span>
                </td></tr>
              <tr><td height="30"></td></tr>
            
              <tr><td height="19" style="background:#eeeeee"></td></tr>
               
            <tr>
               <td valign="middle" style="text-align:center;font-family:Roboto,OpenSans,Open Sans,Arial,sans-serif;background:#eee;color:#777; font-size:10px;font-weight:normal;line-height:14px;margin:0;padding:0 6px 0 6px;">
                  © 2019 Payify a CS50 Final Project created By <a href="https://www.linkedin.com/in/msomar/">Mohamed Omar</a>, Egypt.</td>
               </tr>
             </tbody></table>
            </td>
          </tr>          
          <tr><td height="18" style="background:#eeeeee"></td></tr>
        </tbody></table>
      </td>
      <td width="20" style="background:#eeeeee"></td>
    </tr>
  </tbody></table>
</body></html>
    """, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)