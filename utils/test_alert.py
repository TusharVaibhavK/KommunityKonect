from telegram_bot import send_telegram_alert

# Test formatted alert
send_telegram_alert("""
*New Service Request!*
- Issue: Plumbing leak
- Customer: @test_user
- Time: ASAP
""")