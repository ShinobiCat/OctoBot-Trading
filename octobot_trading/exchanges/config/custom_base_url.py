class CustomBaseUrlConfig:
    '''
    Handle custom base url for api endpopint, overriding CCXT defaults when necessary.
    '''
    custom_base_url = {
        'okx': {
            'myokx': 'my.okx.com',
            'rest': 'eea.okx.com',
            'websocket': 'wseea.okx.com'
        },
        # Add more exchanges and their custom hostnames here
    }

    @classmethod
    def get_custom_base_url(cls, exchange_name, custom_base_url):
        return cls.custom_base_url.get(exchange_name, {}).get(custom_base_url)
