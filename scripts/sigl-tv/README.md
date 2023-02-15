Pay TV Scripts
==============

This folder contains the Pay TV scripts for the sigls TV used in the smart card
lab by TUEISEC.

In order to view the stream you need to execute the 'client' script with the
server name and port given as parameters. It uses the 'receiver.py' file in
order to decrypt the stream with the help of a connected smart card.

The port cotains your group number plus a offset of 20000.
E.g: for group number 42 the following code should be executed:
    ./client tueisec-sigltv 20042

Possible issues:
* bash: ./client: Permission denied
    This means that the file does not have the executable flag set. First allow
    execution of the file as a program by running:
        chmod a+x client


Further scripts are included for debugging:
-------------------------------------------

The python script 'test.py' can be used to trigger a single decryption on the
card in order to ensure proper functioning of the interface. It can also be used
to test the AES implementation on the card by comparing the result with a
decryption performed with the key given in the file.
In order to run it, execute:
    python3 test.py


The 'test_system' script can be used in order to test the system using a custom
key given in 'streamer.py'. It takes the path to a video file as an input, e.g:
    ./test_system trailer_big_buck_bunny.m4v 
This script will encrypt the video file using 'streamer.py' and then use
'receiver.py' together with the connected smart card to decrypt the video again.
The key given in 'receiver.py' should match the key on the card.
