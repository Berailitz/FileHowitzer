FileHowitzer
===

A tool to share files.

Introduction
---
This tool will:
- Start a web server.
- Show a QR code containing the URL.

So you can:
- Send files from any device with a screen.
- Receive files at any device with a camera.

Usage
---
1. Make sure the sender and the receiver are in the same network.
1. Make sure the dependencies are installed.
1. Sender executes `python3.8 file_howitzer.py`.
1. Receiver scans the QR code on the sender's screen.
1. Get the files.

TODOs
---
 * [x] Add command-line interfaces.
 * [x] IPv6 support.
 * [x] Show QR code in the (ASCII) terminal.
 * [x] Add Travis CI and release standalone executables.
 * [ ] Dual stack support.
 * [ ] SSL support.
 * [ ] Add 2-way communication, based on the HTML5 FileSystem API and WebSocket. (maybe)
