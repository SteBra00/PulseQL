TOOL_NAME = 'PulseQL'
TOOL_VERSION = 'v.0.5.1 beta'


import sys
import json
import socket
import logging
import sqlite3
import argparse
import socketserver
from datetime import datetime
from rich.console import Console
from typing import Any, Tuple, Union, Optional, Iterable, Dict
from prompt_toolkit import PromptSession
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from pygments.style import Style
from pygments.lexer import RegexLexer
#from pygments.lexers.sql import SqlLexer
from pygments.token import (
    Keyword,
    Name,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
    Number,
    Comment
)



class Utils:
    @staticmethod
    def printHeader(console:Console, mode:str) -> None:
        console.print(f'{TOOL_NAME} {TOOL_VERSION} {mode} is running.')

    @staticmethod
    def queryExecute(database:sqlite3.Connection, query:str, alternativeSql:Optional[Dict[str, str]], toJson:bool=False) -> Any:
        result = None
        try:
            if alternativeSql:
                query = Utils.convertQuery(query, alternativeSql) if alternativeSql else query
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

    @staticmethod
    def getDictFromJsonFile(file_path:str) -> Dict[str, str]:
        data = {}
        with open(file_path, 'r') as file:
            data = json.loads(file.read())
        return data
    
    @staticmethod
    def convertQuery(query:str, alternativeSql:Dict[str, str]) -> str:
        words = query.split(' ')
        query = ''
        for i in range(len(words)):
            if words[i] in alternativeSql.keys():
                words[i] = alternativeSql[words[i]]
            query += words[i]+' '
        return query[:-1]
    
    @staticmethod
    def listToRegex(elements:Iterable[str], prefix:Optional[str]=None, separator:Optional[str]='.') -> str:
        s = ''
        for element in elements:
            s += prefix+separator if prefix!=None else ''
            s += element+'|'
        return s[:-1]

    @staticmethod
    def getDatabaseTables() -> Iterable[str]:
        return [] #FIXME
    
    @staticmethod
    def getDatabaseTableColumns(tableName:str) -> Iterable[str]:
        return [] #FIXME


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
    alternativeSql:Union[Dict[str, str], None] = None

    keywords = ('ABORT', 'ABS', 'ABSOLUTE', 'ACCESS', 'ADA', 'ADD', 'ADMIN', 'AFTER',
                'AGGREGATE', 'ALIAS', 'ALL', 'ALLOCATE', 'ALTER', 'ANALYSE', 'ANALYZE',
                'AND', 'ANY', 'ARE', 'AS', 'ASC', 'ASENSITIVE', 'ASSERTION', 'ASSIGNMENT',
                'ASYMMETRIC', 'AT', 'ATOMIC', 'AUTHORIZATION', 'AVG', 'BACKWARD',
                'BEFORE', 'BEGIN', 'BETWEEN', 'BITVAR', 'BIT_LENGTH', 'BOTH', 'BREADTH',
                'BY', 'C', 'CACHE', 'CALL', 'CALLED', 'CARDINALITY', 'CASCADE',
                'CASCADED', 'CASE', 'CAST', 'CATALOG', 'CATALOG_NAME', 'CHAIN',
                'CHARACTERISTICS', 'CHARACTER_LENGTH', 'CHARACTER_SET_CATALOG',
                'CHARACTER_SET_NAME', 'CHARACTER_SET_SCHEMA', 'CHAR_LENGTH', 'CHECK',
                'CHECKED', 'CHECKPOINT', 'CLASS', 'CLASS_ORIGIN', 'CLOB', 'CLOSE',
                'CLUSTER', 'COALESCE', 'COBOL', 'COLLATE', 'COLLATION',
                'COLLATION_CATALOG', 'COLLATION_NAME', 'COLLATION_SCHEMA', 'COLUMN',
                'COLUMN_NAME', 'COMMAND_FUNCTION', 'COMMAND_FUNCTION_CODE', 'COMMENT',
                'COMMIT', 'COMMITTED', 'COMPLETION', 'CONDITION_NUMBER', 'CONNECT',
                'CONNECTION', 'CONNECTION_NAME', 'CONSTRAINT', 'CONSTRAINTS',
                'CONSTRAINT_CATALOG', 'CONSTRAINT_NAME', 'CONSTRAINT_SCHEMA',
                'CONSTRUCTOR', 'CONTAINS', 'CONTINUE', 'CONVERSION', 'CONVERT',
                'COPY', 'CORRESPONDING', 'COUNT', 'CREATE', 'CREATEDB', 'CREATEUSER',
                'CROSS', 'CUBE', 'CURRENT', 'CURRENT_DATE', 'CURRENT_PATH',
                'CURRENT_ROLE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER',
                'CURSOR', 'CURSOR_NAME', 'CYCLE', 'DATA', 'DATABASE',
                'DATETIME_INTERVAL_CODE', 'DATETIME_INTERVAL_PRECISION', 'DAY',
                'DEALLOCATE', 'DECLARE', 'DEFAULT', 'DEFAULTS', 'DEFERRABLE',
                'DEFERRED', 'DEFINED', 'DEFINER', 'DELETE', 'DELIMITER', 'DELIMITERS',
                'DEREF', 'DESC', 'DESCRIBE', 'DESCRIPTOR', 'DESTROY', 'DESTRUCTOR',
                'DETERMINISTIC', 'DIAGNOSTICS', 'DICTIONARY', 'DISCONNECT', 'DISPATCH',
                'DISTINCT', 'DO', 'DOMAIN', 'DROP', 'DYNAMIC', 'DYNAMIC_FUNCTION',
                'DYNAMIC_FUNCTION_CODE', 'EACH', 'ELSE', 'ELSIF', 'ENCODING',
                'ENCRYPTED', 'END', 'END-EXEC', 'EQUALS', 'ESCAPE', 'EVERY', 'EXCEPTION',
                'EXCEPT', 'EXCLUDING', 'EXCLUSIVE', 'EXEC', 'EXECUTE', 'EXISTING',
                'EXISTS', 'EXPLAIN', 'EXTERNAL', 'EXTRACT', 'FALSE', 'FETCH', 'FINAL',
                'FIRST', 'FOR', 'FORCE', 'FOREIGN', 'FORTRAN', 'FORWARD', 'FOUND', 'FREE',
                'FREEZE', 'FROM', 'FULL', 'FUNCTION', 'G', 'GENERAL', 'GENERATED', 'GET',
                'GLOBAL', 'GO', 'GOTO', 'GRANT', 'GRANTED', 'GROUP', 'GROUPING',
                'HANDLER', 'HAVING', 'HIERARCHY', 'HOLD', 'HOST', 'IDENTITY', 'IF',
                'IGNORE', 'ILIKE', 'IMMEDIATE', 'IMMEDIATELY', 'IMMUTABLE', 'IMPLEMENTATION', 'IMPLICIT',
                'IN', 'INCLUDING', 'INCREMENT', 'INDEX', 'INDITCATOR', 'INFIX',
                'INHERITS', 'INITIALIZE', 'INITIALLY', 'INNER', 'INOUT', 'INPUT',
                'INSENSITIVE', 'INSERT', 'INSTANTIABLE', 'INSTEAD', 'INTERSECT', 'INTO',
                'INVOKER', 'IS', 'ISNULL', 'ISOLATION', 'ITERATE', 'JOIN', 'KEY',
                'KEY_MEMBER', 'KEY_TYPE', 'LANCOMPILER', 'LANGUAGE', 'LARGE', 'LAST',
                'LATERAL', 'LEADING', 'LEFT', 'LENGTH', 'LESS', 'LEVEL', 'LIKE', 'LIMIT',
                'LISTEN', 'LOAD', 'LOCAL', 'LOCALTIME', 'LOCALTIMESTAMP', 'LOCATION',
                'LOCATOR', 'LOCK', 'LOWER', 'MAP', 'MATCH', 'MAX', 'MAXVALUE',
                'MESSAGE_LENGTH', 'MESSAGE_OCTET_LENGTH', 'MESSAGE_TEXT', 'METHOD', 'MIN',
                'MINUTE', 'MINVALUE', 'MOD', 'MODE', 'MODIFIES', 'MODIFY', 'MONTH',
                'MORE', 'MOVE', 'MUMPS', 'NAMES', 'NATIONAL', 'NATURAL', 'NCHAR', 'NCLOB',
                'NEW', 'NEXT', 'NO', 'NOCREATEDB', 'NOCREATEUSER', 'NONE', 'NOT',
                'NOTHING', 'NOTIFY', 'NOTNULL', 'NULL', 'NULLABLE', 'NULLIF', 'OBJECT',
                'OCTET_LENGTH', 'OF', 'OFF', 'OFFSET', 'OIDS', 'OLD', 'ON', 'ONLY',
                'OPEN', 'OPERATION', 'OPERATOR', 'OPTION', 'OPTIONS', 'OR', 'ORDER',
                'ORDINALITY', 'OUT', 'OUTER', 'OUTPUT', 'OVERLAPS', 'OVERLAY',
                'OVERRIDING', 'OWNER', 'PAD', 'PARAMETER', 'PARAMETERS', 'PARAMETER_MODE',
                'PARAMETER_NAME', 'PARAMETER_ORDINAL_POSITION',
                'PARAMETER_SPECIFIC_CATALOG', 'PARAMETER_SPECIFIC_NAME',
                'PARAMETER_SPECIFIC_SCHEMA', 'PARTIAL', 'PASCAL', 'PENDANT', 'PERIOD', 'PLACING',
                'PLI', 'POSITION', 'POSTFIX', 'PRECEEDS', 'PRECISION', 'PREFIX', 'PREORDER',
                'PREPARE', 'PRESERVE', 'PRIMARY', 'PRIOR', 'PRIVILEGES', 'PROCEDURAL',
                'PROCEDURE', 'PUBLIC', 'READ', 'READS', 'RECHECK', 'RECURSIVE', 'REF',
                'REFERENCES', 'REFERENCING', 'REINDEX', 'RELATIVE', 'RENAME',
                'REPEATABLE', 'REPLACE', 'RESET', 'RESTART', 'RESTRICT', 'RESULT',
                'RETURN', 'RETURNED_LENGTH', 'RETURNED_OCTET_LENGTH', 'RETURNED_SQLSTATE',
                'RETURNS', 'REVOKE', 'RIGHT', 'ROLE', 'ROLLBACK', 'ROLLUP', 'ROUTINE',
                'ROUTINE_CATALOG', 'ROUTINE_NAME', 'ROUTINE_SCHEMA', 'ROW', 'ROWS',
                'ROW_COUNT', 'RULE', 'SAVE_POINT', 'SCALE', 'SCHEMA', 'SCHEMA_NAME',
                'SCOPE', 'SCROLL', 'SEARCH', 'SECOND', 'SECURITY', 'SELECT', 'SELF',
                'SENSITIVE', 'SERIALIZABLE', 'SERVER_NAME', 'SESSION', 'SESSION_USER',
                'SET', 'SETOF', 'SETS', 'SHARE', 'SHOW', 'SIMILAR', 'SIMPLE', 'SIZE',
                'SOME', 'SOURCE', 'SPACE', 'SPECIFIC', 'SPECIFICTYPE', 'SPECIFIC_NAME',
                'SQL', 'SQLCODE', 'SQLERROR', 'SQLEXCEPTION', 'SQLSTATE', 'SQLWARNINIG',
                'STABLE', 'START', 'STATE', 'STATEMENT', 'STATIC', 'STATISTICS', 'STDIN',
                'STDOUT', 'STORAGE', 'STRICT', 'STRUCTURE', 'STYPE', 'SUBCLASS_ORIGIN',
                'SUBLIST', 'SUBSTRING', 'SUCCEEDS', 'SUM', 'SYMMETRIC', 'SYSID', 'SYSTEM',
                'SYSTEM_USER', 'TABLE', 'TABLE_NAME', ' TEMP', 'TEMPLATE', 'TEMPORARY',
                'TERMINATE', 'THAN', 'THEN', 'TIME', 'TIMESTAMP', 'TIMEZONE_HOUR',
                'TIMEZONE_MINUTE', 'TO', 'TOAST', 'TRAILING', 'TRANSACTION',
                'TRANSACTIONS_COMMITTED', 'TRANSACTIONS_ROLLED_BACK', 'TRANSACTION_ACTIVE',
                'TRANSFORM', 'TRANSFORMS', 'TRANSLATE', 'TRANSLATION', 'TREAT', 'TRIGGER',
                'TRIGGER_CATALOG', 'TRIGGER_NAME', 'TRIGGER_SCHEMA', 'TRIM', 'TRUE',
                'TRUNCATE', 'TRUSTED', 'TYPE', 'UNCOMMITTED', 'UNDER', 'UNENCRYPTED',
                'UNION', 'UNIQUE', 'UNKNOWN', 'UNLISTEN', 'UNNAMED', 'UNNEST', 'UNTIL',
                'UPDATE', 'UPPER', 'USAGE', 'USER', 'USER_DEFINED_TYPE_CATALOG',
                'USER_DEFINED_TYPE_NAME', 'USER_DEFINED_TYPE_SCHEMA', 'USING', 'VACUUM',
                'VALID', 'VALIDATOR', 'VALUES', 'VARIABLE', 'VERBOSE',
                'VERSION', 'VERSIONS', 'VERSIONING', 'VIEW',
                'VOLATILE', 'WHEN', 'WHENEVER', 'WHERE', 'WITH', 'WITHOUT', 'WORK',
                'WRITE', 'YEAR', 'ZONE')

    colors = {
        'keyword': '#008800',
        'name': '#e0e0e0',
        'operator': '#e0e0e0',
        'punctuation': '#e0e0e0',
        'string': '#d727ff',
        'comment': '#81dfff'
    }

    @staticmethod
    def getColor(key:str) -> str:
        return DataSetting.colors[key]
    
    @staticmethod
    def getKeywords() -> Iterable[str]:
        if DataSetting.alternativeSql:
            temp_keys = list(DataSetting.keywords)
            for key, value in DataSetting.alternativeSql.items():
                if value in temp_keys:
                    temp_keys.remove(value)
                    temp_keys.append(key)
                else:
                    print(f"Warning: Keyword '{value}' not found in SQL standard dictionary")
            return temp_keys
        else:
            return DataSetting.keywords




if __name__=='__main__':
    parser = argparse.ArgumentParser(prog=TOOL_NAME)
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s: {TOOL_VERSION}', help='Return versions')
    parser.add_argument('-db', '--database', metavar='database_path', default='database.db', help='Specific path of database.db (Default is "./database.db")')
    parser.add_argument('-c', '--console', action='store_true', help='Start program in ConsoleMode')
    parser.add_argument('-ac', '--console-auto-complete', action='store_true', help='Autocomplete command in ConsoleMode')
    parser.add_argument('-s', '--server', nargs='?', type=Utils.validateAddress, metavar='address:port', help='Start program in ServerMode (Default is 0.0.0.0:5500)')
    parser.add_argument('-sf', '--server-file-log', nargs='?', metavar='filelog_path', help='Specific logfile in ServerMode (Default is disabled)')
    parser.add_argument('-sb', '--server-buffer-size', nargs='?', metavar='buffer_size', type=int, default=1024, help='Spacific size of socket buffer')
    parser.add_argument('-j', '--json', action='store_true', help='Specific if encode output to JSON format')
    parser.add_argument('-f', '--file', metavar='path.sql', nargs='*', help="Load file's querys on database (Files are loads before start Console or Server Modes)")
    parser.add_argument('-d', '--dictionary-json', metavar='file.json', nargs='?', help='Load file for traslating SQL query into alternative lenguage')

    args = parser.parse_args(sys.argv[1:])

    DataSetting.alternativeSql = Utils.getDictFromJsonFile(args.dictionary_json) if args.dictionary_json else None



class SqlConsoleStyle(Style):
    styles = {
        Keyword: DataSetting.getColor('keyword'),
        Name: DataSetting.getColor('name'),
        Operator: DataSetting.getColor('operator'),
        Punctuation: DataSetting.getColor('punctuation'),
        String: DataSetting.getColor('string'),
        Comment: DataSetting.getColor('comment')
    }


class SqlConsoleLexer(RegexLexer):
    tokens = {
        'root': [
            (Utils.listToRegex(DataSetting.getKeywords()), Keyword),
            (r'\d+', Number),
            (r'"([^"\\]|\\.)*"|\'([^"\\]|\\.)*\'', String),
            (r'\s+', Whitespace),
            (r'\w+', Text),
            (r'[\(\)\[\]\{\};,]', Punctuation),
            #(r'', Name),
            (r'--.*$|/\*.*?\*/|\{-(.*?)-\}', Comment)
        ]
    }


class SqlConsoleAutoSuggester(AutoSuggest):
    def __init__(self, autoComplete:bool) -> None:
        self.autoComplete = autoComplete
        super().__init__()

    def get_suggestion(self, buffer:Buffer, document:Document) -> Optional[Suggestion]:
        word = document.get_word_before_cursor()
        suggestions = []
        if len(word)>0:
            for keyword in DataSetting.getKeywords():
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
    def __init__(self, path:str, toJson:bool, autoComplete:bool, alternativeSqlFile:Union[Dict[str, str], None]) -> None:
        self.console = Console()
        self.alternativeSql = Utils.getDictFromJsonFile(alternativeSqlFile) if alternativeSqlFile else None
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
                    result = Utils.queryExecute(self.database, query, self.alternativeSql, self.toJson)
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

            result = Utils.queryExecute(database=database, query=data, toJson=self.server.core.toJson, alternativeSql=DataSetting.alternativeSql)
            self.request.send(str(result).encode('utf-8'))
        except (sqlite3.Error, Exception) as e:
            self.server.core.sqlServerLogger.logError(message=repr(e), header=f'{self.client_address[0]}:{self.client_address[1]}')
            self.request.sendall(b'Exception')
        finally:
            database.commit()
            database.close()
            self.request.close()


class ServerMode:
    def __init__(self, addr:Tuple[str, int], path:str, filelog:Union[str, None], bufferSize:int, toJson:bool, alternativeSqlFile:Union[Dict[str, str], None]) -> None:
        self.console = Console()
        self.dbPath = path
        self.addr = addr
        self.sqlServerLogger = SqlServerLogger(self.console, True, filelog) if filelog else SqlServerLogger(self.console)
        self.bufferSize = bufferSize
        self.toJson = toJson
        self.alternativeSql = Utils.getDictFromJsonFile(alternativeSqlFile) if alternativeSqlFile else None

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



if __name__=='__main__':
    if args.file:
        SqlFileLoader(path=args.database, files=args.file)

    if args.console:
        ConsoleMode(path=args.database, toJson=args.json, autoComplete=args.console_auto_complete, alternativeSqlFile=args.dictionary_json).run()
    elif args.server:
        ServerMode(addr=(args.server[0], args.server[1]), path=args.database, filelog=args.server_file_log, bufferSize=args.server_buffer_size, toJson=args.json, alternativeSqlFile=args.dictionary_json).run()
    else:
        parser.print_help()
    exit()
