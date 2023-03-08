config = {
    'monitorInterval': 10,                         # auto reload time interval [secs]
    'loggers': {
        'LogDemo': {
            'level': "DEBUG",
            'additivity': False,
            'AppenderRef' : ['LogDemo']
            },
        'root': {
            'level': "DEBUG",
            'AppenderRef': ['output_root']
        }
    },
    'appenders': {
        'output_root': {
            'type': "file",
            'FileName': "error.log",            # log file name
            'backup_count': 5,                       # files count use backup log
            'file_size_limit': 1024 * 1024 * 20,     # single log file size, default :20MB
            'PatternLayout': "[level:%(levelname)\ts-file:%(filename)\ts-lineno:%(lineno)d]\t%(asctime)s\t%(message)s"
        },
        'LogDemo': {
            'type': "file",
            'FileName':"LogDemo.log",
            'PatternLayout': "[level:%(levelname)\ts-file:%(filename)\ts-lineno:%(lineno)d]\t%(asctime)s\t%(message)s"
        },
        'console': {
            'type': "console",
            'target': "console",
            'PatternLayout': "[%(levelname)s]\t%(asctime)s\t%(message)s"
        }
    }
}