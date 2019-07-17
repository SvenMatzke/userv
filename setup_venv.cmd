call venv\Scripts\activate
cd userv.socket_server\
python setup.py develop -N
cd ..
cd userv.async_server\
python setup.py develop -N
cd ..
cd userv.core\
python setup.py develop -N
