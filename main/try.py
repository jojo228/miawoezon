import requests
import json


data = {
    "apikey": "167837621065f9bc1762a003.17505002",
    "site_id": "5867973",
    "transaction_id": "13422801",
}
payment = requests.post(
    url = "https://miawoezon.com/payment/notification",
    data = data
)


print(payment.text)