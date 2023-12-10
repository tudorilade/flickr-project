# Flickr Tags Searcher

### Python Project: Category A

Project for Python course. The goal of the project is to display on a map the coordinates of 
the most **X** recent posts given a hashtag.

## Installation

### Prerequisite

A virtual environment with python version >=3.10 is requested to be installed.

After you chose the interpreter, run:

```shell
pip install -r requirements.txt
```
in order to install the dependencies.


## Run the program

In order to run the program, execute the script in this way:

```shell
python main.py --hashtag <hashtag> [--limit <X>]
```
The **--hashtag** is required. You can insert either with "#" or not. The **--limit** tag is 
optional. If you don't pass it, it will search for hashtag input in the entire API response.

Some examples:

1) Get first 100 photos with #nice hashtag
```shell
python main.py --hashtag nice --limit 100
```

2) Get all photos containing #blabla
```shell
python main.py --hashtag blabla
```


### Author: Tudor Ilade
### Fall 2023 - Alexandru Ioan Cuza University
