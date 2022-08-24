{
    'name': 'Razerpay Malaysia Payment',
    'version': '15.0',
    'summary': 'Provide secured connection to Razerpay Malaysia (FPX, Credit/Debit Cards, E-Wallets and many more)',
    'description': 'Razerpay Malaysia payment gateway',
    'category': 'website',
    'author': 'Wizeewig (Softlakes Sdn. Bhd)',
    'website': 'Website',
    'price': '30' ,
    'currency' : 'USD' ,
    'depends': ['payment', 'website_sale', 'account'],
    'data': [
        'views/payment_views.xml',
        'views/payment_razerpay_template.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False
}
