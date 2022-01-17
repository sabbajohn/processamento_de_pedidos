if ps -aux | grep -v grep | grep services_tbx
then
    echo 'Ja em Execucao!'  
else

    PYTHONPATH=/home/ubuntu/processamento_de_pedidos python3 -m services_tbx ?
fi

