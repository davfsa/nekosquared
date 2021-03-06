# nekosquared

[![mit](https://img.shields.io/badge/Licensed%20under-MIT-red.svg?style=flat-square)](./LICENSE)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python%203.6.5-ffde57.svg?&colorB=4584b6&style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAPBSURBVFhHtVdNaBNBFJ5Nqz3VRsWDF1E8iaCNFhKFaquCBxFT7EFBaQOCKLW0HixUsL15KVVEwYNIC+qhJf0JKoJgCxabUMFUPYlie1E8JejBmjYzfm9nf2aTze4i8aXfvjfvvXnfy2RnZ6uxgBLrTzUzJvYzzluFxnYxwbcwwcKMcbhFAfgGI4t4avFh78hK7ocwpnqKbwOx66kwiHpQ/CpI6gUG0BKS3LBVP2nemRk+P0o1vCRk6MoiyQdQ8Df0fcaLH/zJdYxEe0fjVMJL/BtgYq8szC6mb7Zdgj7kT464tDtgeEqAFeAohY/gO43x1nJC1bbISW/HxVN8G5B1qCAbivaNz2D0xkmo2gq5FfOWAD+BsdxStwC481UC0hQrIYctdO0tARpgCRSLoF4EtoRuw6f7ed5upJSc4C3WNoz1T2O78dOY02xtNV2bK2D4yu0zQJ0a08mlnX1+bqx9c3jdgoxzVlwTczUhMaztfjmLBNkAyHGziHHMbbLI9QIGuSxWYrs3ZpNTnJkNfLZyDBRWi+11kVdJ8ye4heQqkxtazVGwvkZ7IN4fCYdi/VNxOOJVJ/cDw80sRGcIc9v+C7nMWdrcUFtv+Uy/MR/zWkK47LGDVSUnPQp9uMxvQEMMK1DcJINVJc/jMpi5PDUL+6jiL0VYi/YlYfmSU8F30F+hf5px+pg2LvjTc5c1oT1Jd03giGYDcPRYOS5AA+P0VaTDvWAKg470lQnynYR7h5XjyLWAVRXbgDYM6EZTY2XQotfGcjAqPF7FEgaRdPdkJ2wcyUZBJ6E7guQA1C0tr+20yaGKj9PdE3QcDwJVJwe+owGeshwKOdmaFnrLi+I4xg16zK9wkByCmcdEhp6E8jmtT7TJSfO1P79C9P4XtKibvxRqHhPJUGbo7CPsApxoTvIyuxIo51/IhVjE8Kk8C+iOLU0wba/iXjEVlOfMza6uiYQWTeet4xgvkI0I0J3eSMn0kOHFwoWFnmddGNB5oRbADMt+4fCbcG+Obvp5BG8TOfH6vpaLTycmMcnZgFI8ly8c2LihdsURt5HXmuZoK1cU/zcitSARl3wzkM9D01PSBj01JSb1Gh4SvAH3JXWC6c+UrNPnLcEa8CO34iyh7XuN90SRsGPeEqSBJauYG0xyqfX3POgvdtxbfBvAu9s9q1gpylaGz4iFg7ST7sgxm5ZVKovvLiARH4/R/wO0G4KeB4ILcRff7oYWy+jbrZIEasAUvtgax4RTIMAzg1Mz6nG7jL5yMOgmTGKfzxnTPISxv/JfZTs2HsqNAAAAAElFTkSuQmCC
)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)
[![Discord](https://img.shields.io/discord/265828729970753537.svg?logo=discord&label=Sebi%27s+Bot+Tutorial&style=flat-square)](https://discord.gg/GWdhBSp)
[![HitCount](http://hits.dwyl.io/neko404notfound/nekosquared.svg)](http://hits.dwyl.io/neko404notfound/nekosquared)
![](https://tokei.rs/b1/github/neko404notfound/nekosquared?category=lines)
![](https://tokei.rs/b1/github/neko404notfound/nekosquared?category=files)


The second iteration of Nekozilla. A developer-oriented and utility-oriented
Discord bot.

I am a slightly weird bot that does a variety of things. Functionality is 
mostly geared towards various development tools, such as interpreters
and compilers for over 45 different programming languages. Various tools
for accessing documentation also exist. Functions to provide an easier way
to manage Discord guilds are also being implemented, and are a 
work-in-progress.

Oh, and I cannot evaluate the price of lime.

<img src="pfp.png" style="float: right; max-height:20vw; padding: 3em" />

## Installation

0. Install Python3.6
1. Install `virtualenv` from `pip`.
2. Clone this repo: `git clone https://github.com/neko404notfound/nekosquared`.
3. Enter the directory: `cd nekosquared`.
4. Set up a virtual environment and enter it: `python3.6 -m venv venv; source ./venv/bin/activate`.
5. Install `libjpeg8` for your system from your distro package manager.
6. Install the dependencies: `python3.6 -m pip install -U -r requirements.txt`.
7. If YARL errors, or aiohttp complains, run `python3.6 -m pip install -U --force-reinstall aiohttp`.
8. Follow the configuration instructions further down on this page.

## Running

To run the bot, you should run the following:

```bash
# On OSX, Unix, Linux
python3.6 -m neko2

# On Windows NT
py -3.6 -m neko2
```

If you do not want any error messages sent to your inbox from the bot regarding
errors whilst the bot is physically online, then you should supply the flag
`--nowarnrun`

### The config files

The bot defaults to the config directory `../neko2config`. This is changeable
by specifying the path as the first command line option when running the bot:

```bash
python3.6 -m neko2 /home/me/my_directory
# or
python3.6 -m neko2 ~/my_directory
```

Config files can have any supported file extension, but they **must** have
one. The file type should be guessed automatically. For example, `discord` will
load either `discord.json`, `discord.py` or `discord.yaml` depending on which
is found first.

The bot currently supports the following serialization formats:

| Extension | Format | Notes |
|---|---|---|
| `.json` | JSON | Recommended. |
| `.yaml` | YAML | YAML Ain't Markup Language. Requires `pyyaml` to be installed. |
| `.py` | Python | Loads the file and attempts to `eval` it. This risks arbitrary code execution and is untested. | 

The current config files are required for the bot to work:

| Name | Description |
|---|---|
| `discord` | Basic Discord config and authentication. Holds a dictionary of two dictionaries: `bot` and `auth`. `bot` contains `command_prefix` (string) and `owner_id` (int); `auth` contains `client_id` (int) and `token` (string). An additional `debug` boolean config value can be supplied to enable verbose stack traces. This defaults to `false` if unspecified. The `dm_errors` parameter can also be specified to control whether errors get sent to the bot owner's inbox. This defaults to true if not specified. |

Cogs require the following additional configurations:

| Cog | Name | Description |
|---|---|---|
| `urlshorten` | `urlshorten` | [String API key](https://console.developers.google.com/apis/credentials) for the `goo.gl` API for URL shortening. |
| `wordnik` | `wordnik` | [String API key](http://developer.wordnik.com/) for the `wordnik` API for dictionary access. |

