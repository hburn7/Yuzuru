# Yuzuru
Successor to [Kaguya](https://github.com/kaguyabot/Kaguya)

## Development
Follow the instructions below to run Yuzuru on your own.

### Prerequisites:
- [Docker](https://docs.docker.com/get-docker/)
- A Discord bot token (read more below)

### Discord Bot Creation
_This section may be skipped if you already have a Discord bot created._

- Check out the "Getting Started" section of [this article](https://www.howtogeek.com/364225/how-to-make-your-own-discord-bot/).
- Copy the bot's "token" into a safe place, we will use it later.

### Running the Bot
Clone the source code into your favorite directory.

```
git clone https://github.com/hburn7/Yuzuru && cd Yuzuru
```

**Configuration file**

Create a `config.ini` file in the project root directory. 
You may also launch the application and it will be generated for you.
```ini
[BOT_CONFIG]
token = YOUR_TOKEN_HERE
postgres_username = postgres
postgres_pass = password
postgres_host = localhost
postgres_port = 5500
postgres_database = yuzuru
docker = False

[DATA]
neko_dir = 
lewd_dir = 
nsfw_dir = 
```

Ensure the `config.ini` file has accurate information. The postgres username and password values are arbitrary - Docker handles everything. What's important is that the `docker-compose.yml` file has the same credentials, more on this later.
Paste your token inside of the token section. It should look like this: `token = YOUR_TOKEN_HERE` - no quotes.
For testing, the default postgres information can be left the same. _Port 5500 is used over 5432 to avoid conflicts
with existing databases running on your system._ Docker maps the ports for us. Lastly, set `docker = True` when
running the program through `docker-compose`. If you are working in an IDE and testing through that, set it to `False` instead.
More on that later. Realistically, the only value that needs to be changed is the token when developing locally, as the default docker-compose.yml will work with the default config provided here.

**Start the program**

This specific Docker compose file relies on a pre-existing network named `yuzuru-network`. This is to ensure everything 
plays nice with VPNs run on the local machine. This must be run regardless of whether you use a VPN.

```
docker network create yuzuru-network --subnet 172.24.24.0/24
```

Docker compose automatically configures the database and bot to run together in an isolated environment.
**NOTE:** The database credentials in `docker-compose.yml` must match those in `config.ini`.
Please validate consistencies if any issues arise. Once everything is in order, run Yuzuru through `docker-compose`.
```
docker-compose up
```
_If you run into issues, check out the [Docker Compose Installation Guide.](https://docs.docker.com/compose/install/)_

### Editing the Source Code
Use your favorite IDE or text editor to modify and run Yuzuru locally in a development environment.
Yuzuru needs a database in order to function, so we can configure that separately, again using Docker.

**Configuration file**

Ensure `config.ini` and the values provided below match exactly. Otherwise, the bot will be unable to connect 
to the database. Docker relies on the values passed in the CLI, Yuzuru relies on the values in config.ini.

**Spin up the database locally**

_Following the default `config.ini` values..._

```
docker run -d -p 5500:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=yuzuru postgres
```

An ID will be output to the console. View the logs of the database at anytime using `docker logs [-f] <id>`.
Specify `-f` if you want continuous, live output.

Now that you have the database configured, we're almost ready to run Yuzuru.

**Create a virtual environment**

Run the following in the project's root directory to configure Yuzuru's virtual environment.
```
python3 -m venv env && source env/bin/activate
```

`(env)` should now appear at the front of the console commands you run. e.g. `(env) [user@example Yuzuru]$`

Install the required packages.
```
pip install -r requirements.txt
```

And that's it! You are ready to run Yuzuru. Configure your IDE's Python interpreter to point to `[...]/Yuzuru/env/bin/python`.

Yuzuru runs through `main.py` -- try it now with `python main.py`!