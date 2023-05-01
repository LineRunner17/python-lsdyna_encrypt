import sys
import pathlib
import os
import argparse
from datetime import (
    datetime,
    timedelta
)
import time
from typing import Optional, Union

# ==============================================================================
# TODO:
# - check pitfalls for different keywords in combination with startswith
# - add option to just encrypt keywords partially (not compatible with expiry date)
# -
# ==============================================================================
__versioninfo__ = (1, 0, 0)
__version__ = '.'.join(map(str, __versioninfo__))
__author__ = "Julian Junglas"
__authormail__ = ""
__date__ = "01.05.2023"
__license__ = "GPL-3.0 license"
#
# ==============================================================================
class CliColors:
    # reset to default background, default font
    reset_all = "\033[0;39;49m"
    # set foreground color
    fg_default = "\033[39m"
    fg_black = "\033[30m"
    fg_red = "\033[31m"
    fg_green = "\033[32m"
    fg_yellow = "\033[33m"
    fg_blue = "\033[34m"
    fg_magenta = "\033[35m"
    fg_cyan = "\033[36m"
    fg_lightgray = "\033[37m"
    fg_darkgray = "\033[90m"
    fg_lightred = "\033[91m"
    fg_lightgreen = "\033[92m"
    fg_lightyellow = "\033[93m"
    fg_lightblue = "\033[94m"
    fg_lightmagenta = "\033[95m"
    fg_lightcyan = "\033[96m"
    fg_white = "\033[97m"
    # set background color
    bg_default = "\033[49m"
    bg_black = "\033[40m"
    bg_red = "\033[41m"
    bg_green = "\033[42m"
    bg_yellow = "\033[43m"
    bg_blue = "\033[44m"
    bg_magenta = "\033[45m"
    bg_cyan = "\033[46m"
    bg_lightgray = "\033[47m"
    bg_darkgray = "\033[100m"
    bg_lightred = "\033[101m"
    bg_lightgreen = "\033[102m"
    bg_lightyellow = "\033[103m"
    bg_lightblue = "\033[104m"
    bg_lightmagenta = "\033[105m"
    bg_lightcyan = "\033[106m"
    bg_white = "\033[107m"
    # set font
    font_bold = "\033[1m"
    font_dim = "\033[2m"
    font_q3 = "\033[3m"
    font_undeline = "\033[4m"
    font_blink = "\033[5m"
    font_q6 = "\033[6m"
    font_reverse = "\033[7m"
    font_hidden = "\033[8m"
    # reset font
    reset_font_all = "\033[0m"
    reset_font_bold = "\033[21m"
    reset_font_dim = "\033[22m"
    reset_font_q3 = "\033[23m"
    reset_font_undeline = "\033[24m"
    reset_font_blink = "\033[25m"
    reset_font_q6 = "\033[26m"
    reset_font_reverse = "\033[27m"
    reset_font_hidden = "\033[28m"

    # special 
    PR_DEBUG = fg_blue
    PR_INFO = "\033[0;30;42m"
    PR_LIGHT_WARNING = fg_yellow
    PR_WARNING = "\033[0;30;103m"
    PR_ERROR = fg_lightred
    PR_CRITICAL = bg_lightred

# =================================================================================================
# logging module
import logging
# =================================================================================================
# CREDITS TO: Mad Physicist
# https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

addLoggingLevel('PRINT', logging.INFO + 5)
addLoggingLevel('LIGHT_WARNING', logging.WARNING - 1)

# -------------------------------------------------------------------------------------------------
# stream handler for logging
# -------------------------------------------------------------------------------------------------
class CustomSHFormatter(logging.Formatter):
	#format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
	format = '%(message)s'

	FORMATS = {
		logging.DEBUG: "%(funcName)25s: " + CliColors.fg_blue + format + CliColors.reset_all,
		logging.INFO: CliColors.PR_INFO + format + CliColors.reset_all,
		logging.PRINT: CliColors.reset_all + format + CliColors.reset_all,
		logging.LIGHT_WARNING: CliColors.PR_WARNING + format + CliColors.reset_all,
		logging.WARNING: CliColors.PR_WARNING + format + CliColors.reset_all,
		logging.ERROR: CliColors.PR_ERROR + format + CliColors.reset_all,
		logging.CRITICAL: CliColors.PR_CRITICAL + format + CliColors.reset_all
	}

	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)

# -------------------------------------------------------------------------------------------------
stream_handler_level = logging.INFO
sh_logger = logging.getLogger(__name__)
sh_logger.setLevel(stream_handler_level)

sh = logging.StreamHandler()
sh.setFormatter(CustomSHFormatter())
# sh.setLevel(stream_handler_level)
sh_logger.addHandler(sh)
PRINT = logging.INFO + 5
logging.addLevelName(PRINT, "PRINT")

# =================================================================================================
# =================================================================================================
# displays a progress bar in the console
# =================================================================================================
def progress_bar(iteration, maximum):
    """
    Draws a progress bar in the console based on the given iteration and maximum.

    After finishing the progress bar, it is necessary/advisable to print a newline to avoid overwriting the progress bar and start outputting text on the same line.
    Easy workaround is to print a newline after the progress bar is finished. 
    """
    progress = (iteration + 1) / maximum
    progress_bar_length = 30
    num_bar_chars = int(progress * progress_bar_length)
    bar = '[' + CliColors.fg_green + '■' * num_bar_chars + CliColors.reset_all + ' ' * (progress_bar_length - num_bar_chars) + ' ]'
    print(f"Progress: {bar} {progress*100:.1f}%", end='\r')
    
# =================================================================================================
def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end-start:.6f} seconds to execute. *args: {args[0]}")
        return result
    return wrapper

# =================================================================================================
def ask_overwrite(question):
    while True:
        sh_logger.critical(f"{question} Overwrite? (y/n)")
        overwrite = input().lower().strip()
        if overwrite == 'y':
            break
        elif overwrite == 'n':
            sh_logger.error(f"User canceled.")
            sys.exit()
        else:
            sh_logger.error(f"invalid input. Try again.")

# ==============================================================================
# classes
# ==============================================================================
class LS_Dyna_Encryptor:
    LS_DYNA_PUBLIC_PGP_KEY_1028_BIT = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.19 (GNU/Linux)

mQGiBFM61ScRBACgqz7q7kytYuuRpa+1DTD9J3Kn8s3kMHO7zPtLu8bsb1L1I4UQ
CC6HRL2fMVRtBQZuy445eqsot5npcnzpQ6rcvsQZTVCqXH/gx5O5xs6/W8ktaJXn
hBrxGabk6IzlOXYvmQ2+jOATfQs29pt4+e/+oXFI9EfKBHao2dEgtOWS6wCg+9gi
9azFZOUIHV0EJDPFQJZrRFUD/11AG23e7964MN0HTWAWCIvPs8johwB7NOF6UjRR
xuqD/ZqiQ1hhmQzJR89Weg0TeFFCVP+yK2tgPOgsXry/r7WF/RnO9S/7yvtTWHr8
QPVxCur7vcKX/Lis6ByiyyDvihavBB6RgMYl5HkrEstTY/j3O09woxtQ4Pae5yZ2
woj0BACI87Lk6aO/9wAVXBDYyufqX9bea/lbMEuQZ7qzBO7xjSwchYeoLUbCK5sh
iGI+nT3+liqUZW8+KXd/6I+xsN+YXuS9olmeN5L391VF7ZnWcsOKLbr3tnA3TKJb
Q/txpFhI/2CM2u0VU6w6DAAGlxic5Gf1Cdc8/mA5KaNEuq24PrRDTGl2ZXJtb3Jl
IFNvZnR3YXJlIFRlY2hub2xvZ3kgQ29ycG9yYXRpb24gKExTVEMpIDxzdXBwb3J0
QGxzdGMuY29tPohVBBMRAgAVAhsDAh4BAheABQJTOtVDAgsHAhYAAAoJECATgx5l
rsCu0P4An2f9h8YuWfW+mNY1gm29nIs+kbeZAJ44HMvNgfOVtqUxUCyTlCLjwR6O
CbkBDQRTOtUnEAQA4Q4D0F6l77N0e6XCIH49b7MHFyjkq3OdgHE4vylubEAXVeeX
FD4Vrojn3t/I1QqAUG4ipZZAlLVrSYruzQLYaLhjYP124Py/b6vRo0FcyVsLbazj
BxnGs+fFTrYspLaWfBK2dIrQ9ze9QSLhNous36W3em+fhx8hzGgcUUZRQOcAAwUD
/RkrdN+Mbim6H6MNnEKhoXlpogzriCUB+hpxfQSP+go6+Np2RGkQfTEu+W51vrFA
cW36cncp3OLpsvKzaQgTTT1rqb11Hoe/YpH3T9ngz4NX7a4OSDhHDKC1Q1BuzTEJ
3A3RXeAgRaMV8+hFm91g2KWZuMeqd+nSo2sb5EvpFhW9iEkEGBECAAkFAlM61ScC
GwwACgkQIBODHmWuwK7BaQCfUovuhS6oXuh+1sSqkGCxzHEGER8AniHYve/Kn6CL
SoAeXMxSC7F44Ood
=R0pG
-----END PGP PUBLIC KEY BLOCK-----"""

    LS_DYNA_PUBLIC_PGP_KEY_2048_BIT = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.19 (GNU/Linux)

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
=xfll
-----END PGP PUBLIC KEY BLOCK-----"""

    def __init__(self, *, inputfile: str, outfile: Optional[str] = None, expiry_date: Union[str, datetime.date], key_length: int = 1024):
        self.inputfile: pathlib.Path = pathlib.Path(inputfile).resolve()
        self.outfile: pathlib.Path = None
        if outfile is not None:
            self.outfile: pathlib.Path = pathlib.Path(outfile).resolve()
        self.expiry_date: Union[str, datetime.date] = expiry_date
        self.key_length: int = key_length
        
        self.keywords_to_encrypt = ['*DEFINE_TABLE', '*DEFINE_CURVE']
        self.output_text: list = []

        self.log_text: str = None
        self.ls_dyna_user_id: str = None

        self.inputfile_fullpath: pathlib.Path = self.inputfile.resolve()
        # check if the input file exists
        self.check_inputfile()

        # get name for output file
        self.check_outfile()
        # get name for log file
        self.logfile_fullpath: pathlib.Path 
        self.check_logfile()

        # check the expiry date
        self.check_expiry_date()

        # check the specified key_length to use
        self.__set_ls_dyna_user_id()
        self.check_gpg_key()

    # ==============================================================================
    def __set_ls_dyna_user_id(self):
        # these user ids probably need to be updated at some point if LSTC/ANSYS changes them
        if self.key_length == 1024:
            self.ls_dyna_user_id: str = "0x65AEC0AE"
        elif self.key_length == 2048:
            self.ls_dyna_user_id: str = "0x60C0435A"
        else:
            sh_logger.error("Encryption key length not available/not known. At the moment just 1024- and 2048-bit keys are supported by LS-Dyna. Exiting...")
            sys.exit()

    # ==============================================================================
    def check_inputfile(self):
        # check if inputfile exists
        if not self.inputfile_fullpath.exists():
            sh_logger.error(f"Specified inputfile does not exist. Exiting...")
            sys.exit()

    # ==============================================================================
    def check_outfile(self) -> str:
        # check if outfile was specified, if not set it to inputfile + .asc
        if self.outfile is None:
            self.outfile_fullpath: pathlib.Path = self.inputfile_fullpath.with_name(self.inputfile_fullpath.name + '.asc').resolve()
        # if outfile was specified, make it a full path
        else:
            self.outfile_fullpath: pathlib.Path = pathlib.Path(self.outfile).resolve()
        sh_logger.info(f"Output-File will be called: {self.outfile_fullpath.name}")

        # check if outfile already exists, if so ask if it should be overwritten
        # if not, exit the script
        if self.outfile_fullpath.exists():
            ask_overwrite(f"outfile: {self.outfile_fullpath.name} already exists.")

        self.outfile = self.outfile_fullpath.name

    # ==============================================================================
    def check_logfile(self) -> str:
        # check if logfile exists
        # if not just write the logfile
        # if yes, write the logfile
        # if no, exit script
        self.logfile_fullpath: pathlib.Path = self.outfile_fullpath.with_name(self.outfile_fullpath.name + '.log').resolve()
        if self.logfile_fullpath.exists():
            ask_overwrite(f"Logfile {self.logfile_fullpath} already exists.")

    # ==============================================================================
    def check_expiry_date(self) -> bool:
        # if True, expiry_date was specified as 0 on CLI. That means no expiry date will be set
        if self.expiry_date == '0' or self.expiry_date is None or self.expiry_date is False:
            sh_logger.info("No expiry date specified. Continue without expiry date.")
            self.expiry_date = None
            return
        # if True, expiry_date was not specified on CLI, default argument
        elif isinstance(self.expiry_date, datetime):
            sh_logger.debug(f"{self.expiry_date=}")
            sh_logger.debug(f"DATE      {self.expiry_date.strftime('%m/%d/%Y')}")
            sh_logger.info(f"The default expiry date will be the: {self.expiry_date.strftime('%d. %B %Y')}")
            return

        # if here, expiry_date was specified on CLI
        # raises ValueError if date is not in the correct format
        self.expiry_date = datetime.strptime(self.expiry_date, '%m/%d/%Y')
        
        # check if date is in the past, if so let user know.
        if datetime.today() > self.expiry_date:
            ask_overwrite("The specified expiry date is in the past. Please verify that you want to proceed since it does not make a lot of sense.")
        # check if date is more then 3 years in the future, if so let user know.
        elif datetime.today() + timedelta(days=3*365) < self.expiry_date:
            ask_overwrite("The specified expiry date is more than three years in the future. Please verify that you want to proceed since this is higher than the default.")

        sh_logger.debug(f"{self.expiry_date=}")
        sh_logger.debug(f"DATE      {self.expiry_date.strftime('%m/%d/%Y')}")
        sh_logger.info(f"The chosen expiry date will be the: {self.expiry_date.strftime('%d. %B %Y')}")
        return

    # ==============================================================================
    def generate_header(self) -> str:
        # get user id and date for the header
        user_id = os.popen('whoami').read().strip()
        today_date = datetime.now().strftime("%d.%m.%Y")

        header = f"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$
$ START OF ENCRYPTION HEADER
$
$ This file was generated by:
$
$ LS-Dyna Material-File encryption script (generated by version {__version__})
$
$ user: {user_id}
$ date: {today_date}
$
$ END OF ENCRYPTION HEADER
$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$"""

        self.output_text.append(header)

# ==============================================================================
    def gather_logs(self):
        # gather all information for the logfile
        self.log_text = []
        self.log_text.append(f"# -----------------------------------------------------------------------------")
        self.log_text.append(f"Input file to encrypt: {self.inputfile_fullpath}")
        self.log_text.append(f"by: {self.ls_dyna_user_id}")
        self.log_text.append(f"on: {datetime.now().strftime('%d. %B %Y %H:%M:%S')}")
        if self.expiry_date:
            self.log_text.append(f"Expiry date: {self.expiry_date.strftime('%d. %B %Y')}")
        else:
            self.log_text.append(f"Expiry date: Never")
        self.log_text.append(f"Encrypted keywords: {', '.join(self.keywords_to_encrypt)}")

    # ==============================================================================
    def check_gpg_key(self):
        # check if the key is imported in gpg, returns 0 if available
        check_key = os.system(f'gpg -k {self.ls_dyna_user_id} > /dev/null 2>&1')

        if check_key != 0:
            sh_logger.error("""key_length not available/not known. Maybe also outdated. Exiting...
Please check your keys in your gpg configuration ot add the LS-Dyna keys. For further instructions refer to the LS-Dyna instructions:

https://ftp.lstc.com/anonymous/outgoing/support/FAQ/Instructions_encryption
""")
            sys.exit()	

    # ==============================================================================
    def encrypt_actual_data(self, enc_data):
        # make temp file for encryption
        tmp_inputfile = pathlib.Path("tmp_enc_script.txt").resolve()
        tmp_outputfile = pathlib.Path("tmp_enc_script.txt.asc").resolve()

        # text_to_encrypt is the data plus *VENDOR if expiry date
        if self.expiry_date is not None:
            # sh_logger.info(f"Encrypting file with expiry date: {expiry_date.strftime('%Y/%m/%d')}")
            enc_data.insert(0, f"This could be a self written error message in the VENDOR keyword")
            enc_data.insert(0, f"DATE      {self.expiry_date.strftime('%m/%d/%Y')}")
            enc_data.insert(0, "*VENDOR")
            enc_data.append("*VENDOR_END")

        # write text to encrypt to file
        with open(tmp_inputfile, 'w', encoding='utf-8', errors='ignore') as infile:
            # tte = text to encrypt
            for tte in enc_data:
                infile.write(tte + '\n')

        # if already encrypted file exists, just delete it
        if tmp_outputfile.exists():
            os.system(f'rm -f {tmp_outputfile} > /dev/null 2>&1')

        # encrypt the inputfile
        os.system(f'gpg -e -a --rfc2440 --textmode --cipher-algo AES  --compress-algo 0 -r {self.ls_dyna_user_id} --trust-model always {tmp_inputfile} > /dev/null 2>&1')

        # open the output file with encrypted data
        with open(tmp_outputfile, 'r', encoding='utf-8', errors='ignore') as tmp_enc_file:
            enc_text = tmp_enc_file.read().splitlines()

        # clean up all files
        os.system(f'rm -f {tmp_inputfile} {tmp_outputfile} > /dev/null 2>&1')

        return enc_text

    # ==============================================================================
    def encrypt_keyword(self, curve_data):
        # since just the next keyword ends the curve, it could be that some comments are after the current data to encrypt and before the next keyword
        # this is checked here and just appended to the outfile_text
        comments_after_enc_data = []
        for p, t in enumerate(reversed(curve_data)):
            if t.startswith('$'):
                comments_after_enc_data.append(t)
                continue
            break
    
        # reverse the comments after curve data to get the correct order
        comments_after_enc_data = reversed(comments_after_enc_data)
        # if there were comments after the curve the curve data needs to be reduced
        if p == 0:
            enc_data = curve_data
        else:
            enc_data = curve_data[:-p]
        
        # encrypt actual curve
        encrypted_xy_data = self.encrypt_actual_data(enc_data)
        # add comments after curve back to the text
        encrypted_xy_data.extend(comments_after_enc_data)
        return encrypted_xy_data

    # ==============================================================================
    def encrypt_data(self):
        sh_logger.info(f"Encrypting...")
        sh_logger.log(PRINT, f"Will encrypt the keywords: {' ,'.join(self.keywords_to_encrypt)}")
        to_encrypt = False
        tmp_text_to_encrypt = []
        for i, line in enumerate(self.input_text):
            progress_bar(iteration=i, maximum=len(self.input_text))

            # if line is not a keyword that should be encrypted just append to outputfile and go to next line
            if not line.upper().startswith(tuple(self.keywords_to_encrypt)) and not to_encrypt:
                self.output_text.append(line)
                continue
            
            # if line starts with asterix it is a keyword.
            # if its currently in to_encrypt (line before was in a keyword to encrypt), that means that the curent keyword is finished and a new keyword begins.
            #   in this case the current keyword needs to be encrypted and appended to the output text
            if line.startswith('*') and to_encrypt:
                # set to_encrypt to False since line is not longer inside of the curve
                to_encrypt = False
                # encrypt the curve and append to output text
                self.output_text.extend(self.encrypt_keyword(tmp_text_to_encrypt))
                # empty tmp var for holding encrypting data
                tmp_text_to_encrypt = []
                # check if the Keyword is a new keyword to encrypt
                # if so, set to_encrypt to True and append the line to the tmp_text_to_encrypt
                # if not just append to outfile
                if not line.upper().startswith(tuple(self.keywords_to_encrypt)):
                    self.output_text.append(line)

            # if True, then the line has keyword and that means a new keyword is starting, but we are currently not inside encryption mode
            if line.upper().startswith(tuple(self.keywords_to_encrypt)) and not to_encrypt:
                to_encrypt = True

            # if True, then we are inside a keyword and the data needs to be encrypted
            if to_encrypt:
                tmp_text_to_encrypt.append(line)

        # print after the progress bar to get to the next line
        print()

        # if no *END Keyword is specified and the last keyword is to encrypt, the encryption of the last curve is not triggered since the for loop just ends.
        # we must check if there is still something to encrypt
        if tmp_text_to_encrypt:
            self.output_text.extend(self.encrypt_keyword(tmp_text_to_encrypt))

    # ==============================================================================
    def read_inputfile(self):
        # read inputfile
        with open(self.inputfile_fullpath, 'r', encoding='utf-8', errors='ignore') as infile:
            self.input_text = infile.read().splitlines()

    # ==============================================================================
    def encrypt_file(self):
        self.read_inputfile()

        self.generate_header()

        # gather input for logfile
        self.gather_logs()

        self.encrypt_data()

        # write outfile
        sh_logger.debug(f"write output to file: {self.outfile_fullpath}")
        with open(self.outfile_fullpath, 'w', encoding='utf-8', errors='ignore') as outfile:
            for line in self.output_text:
                outfile.write(line + '\n')

        # write logfile
        sh_logger.debug(f"write logfile to file: {self.logfile_fullpath}")
        with open(self.logfile_fullpath, 'w', encoding='utf-8', errors='ignore') as logfile:
            for line in self.log_text:
                logfile.write(line + '\n')

# ==============================================================================
# defs
# ==============================================================================
def start_args():
    my_parser = argparse.ArgumentParser(prog=f'{sys.argv[0]}', description='Encrypt LS-Dyna Material Data', allow_abbrev=False) 
    my_parser.version = __version__
    my_parser.add_argument('inputfile', type=str, help='specify the inputfiles to evaluate')
    my_parser.add_argument('-o', '--outfile', type=str, help='specify the name of the outputfile. Default = inputfile + .asc')
    day_in_three_year = datetime.today() + timedelta(days=3*365) # 3 years
    my_parser.add_argument('-ed', '--expiry_date', type=str, default=day_in_three_year, help='specify the date when the encrypted file should expire. Format must be mm/dd/yyyy')
    key_lengths = [1024, 2048]
    my_parser.add_argument('-kl', '--key_length', type=int, choices=key_lengths, default=key_lengths[0], help='specify the key-length to use')
    my_parser.add_argument('-ver', '--version', action='version')
    args = my_parser.parse_args()

    sh_logger.debug(f"start arguments: {vars(args)}")

    return args.inputfile, args.outfile, args.expiry_date, args.key_length

# ==============================================================================
# ==============================================================================
if __name__ == '__main__':
    # start the argument parser, read the arguments from CLI and set the variables
    inputfile, outfile, expiry_date, key_length = start_args()
    print()
    lsdyna_me = LS_Dyna_Encryptor(inputfile=inputfile, outfile=outfile, expiry_date=expiry_date, key_length=key_length)
    lsdyna_me.encrypt_file()
    print()
