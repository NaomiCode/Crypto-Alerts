# Telegram-Signal-Bot

Telegram-Signal-Bot is a Python Application for Managing crypto financial signals in a telegram bot.

## Installation
1. be sure to have python 3.10 installed!
```bash
sudo apt update -y && sudo apt upgrade -y && sudo add-apt-repository ppa:deadsnakes/ppa -y && sudo apt update && sudo apt install python3.10-full && sudo apt install python3-pip
```
2. install mongoDB
```bash
sudo apt install software-properties-common gnupg apt-transport-https ca-certificates -y && curl -fsSL https://pgp.mongodb.com/server-7.0.asc |  sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list && sudo apt update && sudo apt install mongodb-org -y && sudo systemctl start mongod && sudo systemctl enable mongod && sudo systemctl restart mongod
```
3. check if mongoDB is installed correctly
```bash
sudo systemctl status mongod
```

4. then navigate to project directory and create a virtual environment and activate it

```bash
git clone https://github.com/naomicode/crypto-alert.git && cd Crypto-Alert && python3 -m venv venv && source venv/bin/activate
```
5. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip3 install -r requirements.txt
```
6. and run the application
```bash
nohup python3 main.py &
```
7. Enjoy!

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)
