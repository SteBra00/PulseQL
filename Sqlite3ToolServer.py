import sys
import json
import socket
import logging
import sqlite3
import argparse
import socketserver
from datetime import datetime
from rich.console import Console
from typing import Any, Tuple, Union, Optional, Iterable
from prompt_toolkit import PromptSession
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from pygments.style import Style
from pygments.lexers.sql import SqlLexer
from pygments.token import Keyword, Name, Operator, Punctuation, String, Text


class SqlFileLoader:
    def __init__(self, path:str, files:Iterable[str]) -> None:
        database = sqlite3.Connection(path)

        for file in files:
            with open(file, 'r') as f:
                queries = f.read()
                for query in queries.split(';'):
                    try:
                        Utils.queryExecute(database, query)
                    except Exception as e:
                        print(repr(e))


class DataSetting:
    keywords = ('ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND',
        'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN',
        'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT',
        'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME',
        'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE',
        'DESC', 'DETACH', 'DISTINCT', 'DO', 'DROP', 'EACH', 'ELSE', 'END', 'ESCAPE',
        'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL', 'FOR', 'FOREIGN', 'FROM',
        'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE', 'IN',
        'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT',
        'INTO', 'IS', 'ISNULL', 'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH',
        'NATURAL', 'NO', 'NOT', 'NOTNULL', 'NULL', 'OF', 'OFFSET', 'ON', 'OR',
        'ORDER', 'OUTER', 'PLAN', 'PRAGMA', 'PRIMARY', 'QUERY', 'RAISE', 'RECURSIVE',
        'REFERENCES', 'REGEXP', 'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT',
        'RIGHT', 'ROLLBACK', 'ROW', 'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP',
        'TEMPORARY', 'THEN', 'TO', 'TRANSACTION', 'TRIGGER', 'UNION', 'UNIQUE',
        'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE',
        'WITH', 'WITHOUT'
    )

    colors = {
        'keyword': '#ff6600',
        'name': '#008800',
        'operator': '#dd1144',
        'punctuation': '#999999',
        'string': '#aa3333',
    }


class SqlConsoleStyle(Style):
    styles = {
        Keyword: DataSetting.colors['keyword'],
        Name: DataSetting.colors['name'],
        Operator: DataSetting.colors['operator'],
        Punctuation: DataSetting.colors['punctuation'],
        String: DataSetting.colors['string'],
    }


class SqlConsoleLexer(SqlLexer):
    tokens = SqlLexer.tokens.copy()
    tokens['reserved'] = [
        (kw, Keyword) for kw in DataSetting.keywords
    ]

    tokens['name'] = [
        (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
        (r'\"[^\"]+\"', Name),
        (r'\[[^\]]+\]', Name)
    ]

    tokens['keyword'] = [
        (r'\b%s\b' % kw, Keyword) for kw in DataSetting.keywords
    ]

    tokens['whitespace'] = [
        (r'\s+', Text)
    ]


class SqlConsoleAutoSuggester(AutoSuggest):
    def __init__(self, autoComplete:bool) -> None:
        self.autoComplete = autoComplete
        super().__init__()

    def get_suggestion(self, buffer:Buffer, document:Document) -> Optional[Suggestion]:
        word = document.get_word_before_cursor()
        suggestions = []
        if len(word)>0:
            for keyword in DataSetting.keywords:
                if keyword.startswith(word):
                    suggestions.append(Suggestion(keyword[len(word):]))
                elif keyword.lower().startswith(word):
                    suggestions.append(Suggestion(keyword[len(word):].lower()))
            if len(suggestions)==1 and self.autoComplete:
                buffer.insert_text(suggestions[0].text)
                return None
            return suggestions[0] if len(suggestions)>0 else None
        return None


class ConsoleMode:
    def __init__(self, path:str, toJson:bool, autoComplete:bool) -> None:
        self.console = Console()
        self.promptSession = PromptSession('>>> ',
            lexer=PygmentsLexer(SqlConsoleLexer),
            style=style_from_pygments_cls(SqlConsoleStyle),
            auto_suggest=SqlConsoleAutoSuggester(autoComplete=autoComplete),
            vi_mode=True
        )
        self.toJson = toJson
        try:
            self.database = sqlite3.connect(path)
        except sqlite3.Error as e:
            self.console.print(repr(e))

    def run(self) -> None:
        running = True
        Utils.printHeader(self.console, 'ConsoleMode')
        self.console.print("('_clear' for clear console, '_exit' for exit)")
        while running:
            query = self.promptSession.prompt()
            if query=='_clear':
                self.console.clear()
            elif query=='_exit':
                running = False
            else:
                try:
                    result = Utils.queryExecute(self.database, query, self.toJson)
                    if self.toJson:
                        self.console.print_json(result)
                    else:
                        self.console.print(result)
                except sqlite3.Error as e:
                    self.console.print(repr(e))
        self.database.close()


class SqlServerLogger:
    def __init__(self, console:Console, log_to_file:bool=False, log_file_name:str='logfile.log') -> None:
        self.console = console
        self.log_to_file = log_to_file
        self.log_file_name = log_file_name

        if self.log_to_file:
            logging.basicConfig(filename=self.log_file_name, level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
    
    def logDebug(self, message:str, header:str=None) -> None:
        self._log_('DEBUG', message, header)
        if self.log_to_file:
            logging.debug(self._create_message_(message, header))

    def logInfo(self, message:str, header:str=None) -> None:
        self._log_('INFO', message, header)
        if self.log_to_file:
            logging.info(self._create_message_(message, header))

    def logWarning(self, message:str, header:str=None) -> None:
        self._log_('WARNING', message, header, 'yellow')
        if self.log_to_file:
            logging.warning(self._create_message_(message, header))

    def logError(self, message:str, header:str=None) -> None:
        self._log_('ERROR', message, header, 'red')
        if self.log_to_file:
            logging.error(self._create_message_(message, header))
    
    def logCritical(self, message:str, header:str=None) -> None:
        self._log_('CRITICAL', message, header, 'red')
        if self.log_to_file:
            logging.critical(self._create_message_(message, header))

    def _log_(self, level_name:str, message:str, header:str=None, style:str=None) -> None:
        message = self._create_message_(message, header)
        self.console.print(f'[{datetime.now()}] {level_name} {message}', style=style)
    
    def _create_message_(self, message:str, header:str=None) -> None:
        header = header+' ' if header else ''
        return f'{header}-> {message}'


class ClientHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            database = sqlite3.connect(self.server.core.dbPath)

            data = self.request.recv(self.server.core.bufferSize).strip().decode('utf-8')
            self.server.core.sqlServerLogger.logInfo(message=data, header=f'{self.client_address[0]}:{self.client_address[1]}')

            result = Utils.queryExecute(database=database, query=data, toJson=self.server.core.toJson)
            self.request.send(str(result).encode('utf-8'))
        except (sqlite3.Error, Exception) as e:
            self.server.core.sqlServerLogger.logError(message=repr(e), header=f'{self.client_address[0]}:{self.client_address[1]}')
            self.request.sendall(b'Exception')
        finally:
            database.commit()
            database.close()
            self.request.close()


class ServerMode:
    def __init__(self, addr:Tuple[str, int], path:str, filelog:Union[str, None], bufferSize:int, toJson:bool) -> None:
        self.console = Console()
        self.dbPath = path
        self.addr = addr
        self.dbLogger = SqlServerLogger(self.console, True, filelog) if filelog else SqlServerLogger(self.console)
        self.bufferSize = bufferSize
        self.toJson = toJson

    def run(self) -> None:
        with socketserver.TCPServer(self.addr, ClientHandler) as server:
            server.core = self
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                self.console.print('Clossing...')
            except Exception as e:
                self.console.print(repr(e))
            finally:
                server.server_close()


class Utils:
    @staticmethod
    def printHeader(console:Console, mode:str) -> None:
        console.print(f'DBServer {mode} is running.')

    @staticmethod
    def queryExecute(database:sqlite3.Connection, query:str, toJson:bool=False) -> Any:
        result = None
        try:
            cursor = database.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            if toJson:
                result = json.dumps(result)
        except (sqlite3.Error, json.JSONDecodeError) as e:
            raise e
        finally:
            database.commit()
        return result

    @staticmethod
    def validateAddress(arg:str) -> Tuple[str, int]:
        arg = arg.split(':')
        try:
            addr = arg[0]
            if len(addr.split('.'))!=4:
                raise argparse.ArgumentTypeError('Server address is not valid')
            port = int(arg[1])
            if not 0<port<65535:
                raise argparse.ArgumentTypeError('Server port is not valid')
            if socket.socket().connect_ex((addr, port))==0:
                raise argparse.ArgumentTypeError('This address is already in use')
            return addr, port
        except (ValueError, AttributeError):
            raise argparse.ArgumentTypeError('Server address is not valid')



if __name__=='__main__':
    SERVER_VERSION = '0.4.1'
    PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
    SQLITE3_VERSION = sqlite3.version

    parser = argparse.ArgumentParser(prog='Sqlite3ServerTool', description='Server Tool for SQLite3')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s: {SERVER_VERSION}; Python3: {PYTHON_VERSION}; SQLite3: {SQLITE3_VERSION}', help='Return versions')
    parser.add_argument('-db', '--database', metavar='database_path', default='database.db', help='Specific path of database.db (Default is "./database.db")')
    parser.add_argument('-c', '--console', action='store_true', help='Start program in ConsoleMode')
    parser.add_argument('-ac', '--console-auto-complete', action='store_true', help='Autocomplete command in ConsoleMode')
    parser.add_argument('-s', '--server', nargs='?', type=Utils.validateAddress, metavar='address:port', help='Start program in ServerMode (Default is 0.0.0.0:5500)')
    parser.add_argument('-sf', '--server-file-log', nargs='?', metavar='filelog_path', help='Specific logfile in ServerMode (Default is disabled)')
    parser.add_argument('-sb', '--server-buffer-size', nargs='?', metavar='buffer_size', type=int, default=1024, help='Spacific size of socket buffer')
    parser.add_argument('-j', '--json', action='store_true', help='Specific if encode output to JSON format')
    parser.add_argument('-f', '--file', metavar='path.sql', nargs='*', help="Load file's querys on database (Files are loads before start Console or Server Modes)")

    args = parser.parse_args(sys.argv[1:])

    if args.file:
        SqlFileLoader(path=args.database, files=args.file)

    if args.console:
        ConsoleMode(path=args.database, toJson=args.json, autoComplete=args.console_auto_complete).run()
    elif args.server:
        ServerMode(addr=(args.server[0], args.server[1]), path=args.database, filelog=args.server_file_log, bufferSize=args.server_buffer_size, toJson=args.json).run()
    else:
        parser.print_help()
    exit()
