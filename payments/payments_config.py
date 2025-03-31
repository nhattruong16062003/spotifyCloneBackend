import os
from dotenv import load_dotenv

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE')
VNPAY_HASH_SECRET = os.getenv('VNPAY_HASH_SECRET')
VNPAY_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
VNPAY_RETURN_URL = f"{FRONTEND_URL}/payment/vnpay"
