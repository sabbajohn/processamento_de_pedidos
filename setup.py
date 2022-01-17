from setuptools import setup

setup(name='services_tbx',
        version='0.1',
        description='Serviço de Processamento de pedidos',
        url='https://github.com/Grupo-TBX/processamento_de_pedidos/',
        author='Johnnathan Sabbá',
        author_email='johnnathan.sabba@grupotbx.com.br',
        license='Proprietary',
        packages=['services_tbx'],
        install_requires=[
            'redis',
            'schedule',
            'dicttoxml',
            'xmltodict'
        ],
        zip_safe=False) 
