import requests
import base64
from datetime import datetime
import json
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MpesaAPI:
    def __init__(self):
        self.business_shortcode = current_app.config['MPESA_SHORTCODE']
        self.consumer_key = current_app.config['MPESA_CONSUMER_KEY']
        self.consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
        self.passkey = current_app.config['MPESA_PASSKEY']
        
        # API endpoints
        self.auth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        self.query_url = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        
    def get_auth_token(self):
        try:
            auth_string = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {"Authorization": f"Basic {auth_string}"}
            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result.get("access_token")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting auth token: {str(e)}")
            return None
            
    def generate_password(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode(), timestamp
            
    def initiate_stk_push(self, phone_number, amount, account_reference, description):
        """
        Initiate STK push to customer's phone
        """
        try:
            access_token = self.get_auth_token()
            if not access_token:
                return False, "Could not get access token"
                
            password, timestamp = self.generate_password()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
                "AccountReference": account_reference,
                "TransactionDesc": description
            }
            
            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("ResponseCode") == "0":
                return True, {
                    "CheckoutRequestID": result.get("CheckoutRequestID"),
                    "MerchantRequestID": result.get("MerchantRequestID"),
                    "ResponseDescription": result.get("ResponseDescription")
                }
            return False, result.get("ResponseDescription")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating STK push: {str(e)}")
            return False, "Failed to initiate payment"
            
    def query_stk_status(self, checkout_request_id):
        """
        Query the status of an STK push request
        """
        try:
            access_token = self.get_auth_token()
            if not access_token:
                return False, "Could not get access token"
                
            password, timestamp = self.generate_password()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(self.query_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return True, response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying STK status: {str(e)}")
            return False, "Failed to query payment status"
