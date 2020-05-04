git clone https://github.com/tonysimpson/nanomsg-python
cd nanomsg-python
python3 setup.py build 
sudo python3 setup.py install 
cd ..
sudo rm -rf nanomsg-python
npm install 
$(npm bin)/electron-rebuild