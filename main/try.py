import requests
import json


data = {
    "apikey": "167837621065f9bc1762a003.17505002",
    "site_id": "5867973",
    "transaction_id": "60784557",
}
payment = requests.post(
    url = "https://api-checkout.cinetpay.com/v2/payment/check",
    data = data
)


print(payment.text)