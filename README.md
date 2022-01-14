# Yuzuru
Successor to [Kaguya](https://github.com/kaguyabot/Kaguya)

## Development
Follow the instructions below to run Yuzuru on your own.

### Technical Requirements:
- [Python](https://www.python.org/) version 3.8 or higher
- Latest version of [pip](https://pypi.org/project/pip/)

### Discord Bot Creation
_This section may be skipped if you already have a Discord bot created._

- Check out the "Getting Started" section of [this article](https://www.howtogeek.com/364225/how-to-make-your-own-discord-bot/).
- Copy the bot's "token" into a safe place, we will use it later.

### Downloading and Running the Source Code
Clone the source code into your favorite directory.

```
git clone https://github.com/hburn7/Yuzuru
```

Now, we must create the virtual environment to install packages into and our code from.
First, upgrade pip to the latest version.

```
python3 -m pip install --upgrade pip
```
Install all project packages.
```
pip install -r requirements.txt
```

Yuzuru relies on the latest development version of [Pycord](https://github.com/Pycord-Development/pycord).
Install the latest alpha development build.
```
git clone https://github.com/Pycord-Development/pycord
cd pycord
python3 -m pip install -U .[voice]
```
_Note: If the last step above does not work, remove the `[voice]` from the end of the command._

You should now be able to run Yuzuru. Open Yuzuru in your favorite Python development environment and configure
it to run `main.py`. You should get an error related to not having your token properly setup. If you don't
see this error, check your configuration and installation. Now, grab your discord bot token from earlier and paste 
it into the newly created `config.ini` file in the root directory. Do not surround the token with quotation marks.

Yuzuru should now login. If you see a console message saying "Welcome to Yuzuru!", you're all set!