# PulseQL


A simple and Powerful tool for SQL

![Languages Top](https://img.shields.io/github/languages/top/SteBra00/PulseQL)
![License](https://img.shields.io/github/license/SteBra00/PulseQL)
![Next Version:0.5.0](https://img.shields.io/badge/Next%20Version-0.5.0-purple)
![Version:0.4.1](https://img.shields.io/badge/Stable-0.4.1-blue)
![Sqlite:OK](https://img.shields.io/badge/Sqlite-OK-green)
![MySql:InProgress](https://img.shields.io/badge/MySql-InProgress-yellow)
![Oracle:ComingSoon](https://img.shields.io/badge/Oracle-ComingSoon-red)
![Microsoft SQL Server:ComingSoon](https://img.shields.io/badge/Microsoft%20SQL%20Server-ComingSoon-red)
![PostgreSQL:ComingSoon](https://img.shields.io/badge/PostgreSQL-ComingSoon-red)
![IBM DB2:ComingSoon](https://img.shields.io/badge/IBM%20DB2-ComingSoon-red)
![SAP HANA:ComingSoon](https://img.shields.io/badge/SAP%20HANA-ComingSoon-red)
![Teradata:ComingSoon](https://img.shields.io/badge/Teradata-ComingSoon-red)
![Amazon Aurora:ComingSoon](https://img.shields.io/badge/Amazon%20Aurora-ComingSoon-red)



> V.0.4.1


```bash
python3 Sqlite3ToolServer.py -h
```

```text
usage: Sqlite3ServerTool [-h] [-v] [-db database_path] [-c] [-ac] [-s [address:port]] [-sf [filelog_path]]
                         [-sb [buffer_size]] [-j] [-f [path.sql ...]]

Server Tool for SQLite3

options:
  -h, --help            show this help message and exit
  -v, --version         Return versions
  -db database_path, --database database_path
                        Specific path of database.db (Default is "./database.db")
  -c, --console         Start program in ConsoleMode
  -ac, --console-auto-complete
                        Autocomplete command in ConsoleMode
  -s [address:port], --server [address:port]
                        Start program in ServerMode (Default is 0.0.0.0:5500)
  -sf [filelog_path], --server-file-log [filelog_path]
                        Specific logfile in ServerMode (Default is disabled)
  -sb [buffer_size], --server-buffer-size [buffer_size]
                        Spacific size of socket buffer
  -j, --json            Specific if encode output to JSON format
  -f [path.sql ...], --file [path.sql ...]
                        Load file's querys on database (Files are loads before start Console or Server Modes)
```



## Installation
### Linux
1. Update apt-get ```sudo apt-get update```
2. Install Python3 ```sudo apt-get install python3 python3-pip```
3. Test *Python* ```python3 --version``` or ```python --version```
4. Test *PIP* ```python3 -m pip```
5. Install requirments ```python3 -m pip install -r requirments.txt```
6. Run ```python3 Sqlite3ToolServer.py ...```
### Windows
1. Install Python3 from [Official Web Site](https://www.python.org/downloads/)
2. Include "pip" on installation
3. Test *Python* on *CMD* ```python --version``` or ```py --version``` (If not found, try ```python3``` or ```py3```)
4. Test *PIP* on *CMD* ```python -m pip``` or ```python3 -m pip```
5. Install requirments ```python -m pip install -r requirments.txt```
6. Run ```python Sqlite3ToolServer.py ...```
### MacOS
1. Install Python3 from [Official Web Site](https://www.python.org/downloads/)
2. Include "pip" on installation
3. Test *Python* ```python3 --version``` or ```python --version```
4. Test *PIP* ```python3 -m pip```
5. Install requirments ```python3 -m pip install -r requirments.txt```
6. Run ```python3 Sqlite3ToolServer.py
---
## ServerMode
### What is it
The tool in server mode offers a TCP\IP sockets, which only requires a query and returns the result in the form of a string or json (recommended for clients that do not support the 'tuple' data structure)

### Usage
```bash
python3 Sqlite3ToolServer.py -s 0.0.0.0:5500
```
or
```bash
python3 Sqlite3ToolServer.py -s 0.0.0.0:5500 -db mydatabase.db -sf myfilelog.log -sb 500 -f create.sql init.sql -j
```

| Flag | Args         | Values                  | Default       | Scope                                                                          |
|:---- |:-------------|:------------------------|:--------------|:-------------------------------------------------------------------------------|
| -s   | addr:port    | str(Ipv4), int(1-65534) | None          | Start tool il ServerMode (Required)                                            |
| -db  | path.db      | str                     | ./database.db | Specifies path of database (Recommended if you already have -db file)          |
| -sf  | path.log     | str                     | None          | Specifies path of file log (Recommended for debug)                             |
| -sb  | size         | int(1-4096)             | 1024          | Specifies the size of buffer for socket's requests                             |
| -f   | file.sql ... | List[str]               | None          | Include files .sql for initialize database (Not required)                      |
| -j   | None         | None                    | False         | Convert output on JSON standard format (Recommended for portability of output) |

---

## ConsoleMode
### What is it
The tool in console mode offers CLI with auto-suggests, auto-complete (optional) and hightlight keywords.

### Usage
```bash
python3 Sqlite3ToolServer.py -c
```
or
```bash
python3 Sqlite3ToolServer.py -c -db mydatabase.db -f create.sql init.sql -ac -j
```

| Flag | Args         | Values    | Default       | Scope                                                                          |
|:---- |:-------------|:----------|:--------------|:-------------------------------------------------------------------------------|
| -c   | None         | None      | False         | Start tool il ConsoleMode (Required)                                           |
| -db  | path.db      | str       | ./database.db | Specifies path of database (Recommended if you already have -db file)          |
| -f   | file.sql ... | List[str] | None          | Include files .sql for initialize database (Not required)                      |
| -ac  | None         | None      | Flase         | Autocomplete keywords                                                          |
| -j   | None         | None      | False         | Convert output on JSON standard format (Recommended for better output)         |

---
## TODO
* SSL\TLC connections
* File.style for setting CLI colors
