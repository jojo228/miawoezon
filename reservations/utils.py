from datetime import *
from django.utils import timezone

def generate_transaction_id(user, transaction_id_counter):
    # Obtenez les deux premières lettres du prénom de l'utilisateur
    first_two_letters = user.first_name[:2].upper()
    
    # Obtenez l'ID généré par Django
    django_id = str(transaction_id_counter)
    
    # Obtenez la date de la transaction
    transaction_date = timezone.now().strftime('%d%m%y')
    
    # Concaténez les parties pour former le transaction_id
    transaction_id = f"{first_two_letters}{django_id}{transaction_date}"
    
    return transaction_id