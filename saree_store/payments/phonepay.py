import base64
import json
import hashlib
from django.conf import settings

class PhonePeGateway:
    def __init__(self):
        self.merchant_id = getattr(settings, 'PHONEPE_MERCHANT_ID', 'DEMO_MERCHANT_ID')
        self.salt_key = getattr(settings, 'PHONEPE_SALT_KEY', 'DEMO_SALT_KEY_32CHARS_PLACEHOLDER')
        self.salt_index = getattr(settings, 'PHONEPE_SALT_INDEX', 1)
        self.base_url = getattr(settings, 'PHONEPE_BASE_URL', 'https://api-preprod.phonepe.com/apis/pg-sandbox')
        self.redirect_url = getattr(settings, 'PHONEPE_REDIRECT_URL', 'http://localhost:8000/payments/callback/')

    def build_payment_request(self, transaction_id, user_id, amount_in_rs, order_id):
        # PhonePe accepts amount in paise
        amount_in_paise = int(amount_in_rs * 100)
        
        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": transaction_id,
            "merchantUserId": f"USER_{user_id or 'GUEST'}",
            "amount": amount_in_paise,
            "redirectUrl": f"{self.redirect_url}?order_id={order_id}&transaction_id={transaction_id}",
            "redirectMode": "POST",
            "callbackUrl": f"{self.redirect_url}?order_id={order_id}&transaction_id={transaction_id}",
            "mobileNumber": "9999999999",
            "paymentInstrument": {
                "type": "PAY_PAGE"
            }
        }
        
        # Base64 Encode payload
        payload_json = json.dumps(payload)
        base64_payload = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
        
        # SHA256 Signature
        string_to_hash = base64_payload + "/pg/v1/pay" + self.salt_key
        hash_object = hashlib.sha256(string_to_hash.encode('utf-8'))
        sha256_val = hash_object.hexdigest()
        
        checksum = f"{sha256_val}###{self.salt_index}"
        
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum
        }
        
        # In a real integration, you would POST this payload to base_url + "/pg/v1/pay"
        # and receive a redirect URL. 
        # For our premium dummy implementation, we will redirect the user to a beautiful 
        # mock PhonePe payment screen at /payments/mock-gateway/ with all parameters.
        
        return {
            'payload': base64_payload,
            'checksum': checksum,
            'headers': headers,
            'api_url': f"{self.base_url}/pg/v1/pay"
        }
