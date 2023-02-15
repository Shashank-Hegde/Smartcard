### Install requirements for measurement scripts

1. Install Picoscope drivers from https://www.picotech.com/downloads/linux:
   - `sudo bash -c 'echo "deb https://labs.picotech.com/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope.list'`
   - `wget -O - https://labs.picotech.com/debian/dists/picoscope/Release.gpg.key | sudo apt-key add -`
   - `sudo apt-get update`
   - `sudo apt-get install picoscope`
2. Install picoskd-python-wrappers from https://github.com/picotech/picosdk-python-wrappers:
   - Download repository
   - `sudo python3 setup.py install`
   - Install requirements: `pip3 install -r requirements.txt`
3. To use picosdk-python-wrappers  use `import picosdk` within python