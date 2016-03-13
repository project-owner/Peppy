Pylirc is LIRC Python wrapper and it's required to access LIRC from Python programs. To install Pylirc you should complete the following steps.

Install files required by pylirc:
```
sudo apt-get install python-dev
sudo apt-get install liblircclient-dev
```
Create folder
```
mkdir /home/pi/pylirc2-0.1
```
Download pylirc (pylirc2-0.1.tar.gz) from: [https://pypi.python.org/pypi/pylirc2](https://pypi.python.org/pypi/pylirc), extract files to the newly created folder ```/home/pi/pylirc2-0.1```

There is currently incompatibility between Python 3 and Pylirc. The problem was explained [here](http://stackoverflow.com/questions/34691314/python3-4-pylirc-module-not-loaded-although-is-installed-on-my-system). To fix the problem you should either follow the steps described [here](https://github.com/offlinehacker-playground/pylirc2/issues/3#issuecomment-170238377) or just download the file [pylircmodule.c](https://github.com/project-owner/Peppy/blob/master/files/pylircmodule.c) which I prepared using those instructions. The file should be placed in folder ```/home/pi/pylirc2-0.1```. Then Pylirc should be recompiled and installed. Also one file should be renamed:
```
cd /home/pi/pylirc2-0.1
sudo python setup.py install
sudo mv /usr/local/lib/python3.4/dist-packages/pylircmodule.cpython-34m.so /usr/local/lib/python3.4/dist-packages/pylirc.cpython-34m.so
```
After completing all these steps you can test Pylirc by running my testing program [test-pylirc.py](https://github.com/project-owner/Peppy/blob/master/files/test-pylirc.py) and pressing buttons on your IR remote control. The output in the console means that Pylirc works fine:
```
pi@raspberrypi ~ $ python test-lirc.py
['ok']
['up']
['down']
```

[<<Previous](https://github.com/project-owner/Peppy/wiki/LIRC) | [Next>>](https://github.com/project-owner/Peppy/wiki/Peppy)