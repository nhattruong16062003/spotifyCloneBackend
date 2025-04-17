import os
from dotenv import load_dotenv

load_dotenv()

URL_FRONTEND = os.getenv("URL_FRONTEND", "http://zmusic.io.vn")

VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE')
VNPAY_HASH_SECRET = os.getenv('VNPAY_HASH_SECRET')
VNPAY_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
VNPAY_RETURN_URL = f"{URL_FRONTEND}/payment/vnpay"
