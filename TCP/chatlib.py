from typing import List, Tuple

# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages

class Protocol_Client:
	LOGIN = 'LOGIN'
	LOGOUT = 'LOGOUT'
	MY_SCORE = 'MY_SCORE'
	HIGHSCORE = 'HIGHSCORE'
	GET_QUESTION = 'GET_QUESTION'
	SEND_ANSWER = 'SEND_ANSWER'
	LOGGED = 'LOGGED'
	DISCONNECTION = 'DISCONNECTION'


class Protocol_Server:
	LOGIN_OK = 'LOGIN_OK'
	ERROR = 'ERROR'
	YOUR_SCORE = 'YOUR_SCORE'
	ALL_SCORE = 'ALL_SCORE'
	LOGGED_ANSWER = 'LOGGED_ANSWER'
	YOUR_QUESTION = 'YOUR_QUESTION'
	CORRECT_ANSWER = 'CORRECT_ANSWER'
	WRONG_ANSWER = 'WRONG_ANSWER'



ERROR_RETURN = None

FIELDS_LENGTH = 3 # exact length of the fields


class Errors:
	USER_NOT_LOGGED_IN = "User isn't logged in"
	INCORRECT_PASSWORD = "Incorrect password"
	UNKNOWN_COMMAND = "Unknown command"
	CTRL_C_SERVER = "\nThe server was disconnected by ctrl+c"
	CTRL_C_CLIENT = "\nThe client was disconnected by ctrl+c"
	INAPPROPRIATE_REQUEST = 'A requst that is not LOGIN from a user that hasn\'t logged in yet'


def build_message(cmd: str, data: str) -> str | ERROR_RETURN:
	"""
	Gets command name (str) and data field (str) and creates a valid protocol message
	Returns: str, or None if error occured
	"""
	
	if len(cmd) > CMD_FIELD_LENGTH or len(data) > MAX_DATA_LENGTH:
		return ERROR_RETURN
	# cmd
	full_msg = cmd + ' ' * (CMD_FIELD_LENGTH - len(cmd))
	full_msg += DELIMITER

	# data length
	full_msg += str(len(data)).zfill(LENGTH_FIELD_LENGTH)
	full_msg += DELIMITER

	# data
	full_msg += data
	return full_msg


def parse_message(data: str) -> Tuple[str, str] | Tuple[ERROR_RETURN, ERROR_RETURN]:
	"""
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""

	data_split = data.split(DELIMITER)
	if len(data_split) != FIELDS_LENGTH or\
	   len(data_split[0]) != CMD_FIELD_LENGTH or\
	   not data_split[1].isnumeric() or\
	   int(data_split[1]) != len(data_split[2]):
		return ERROR_RETURN, ERROR_RETURN
	cmd = ""
	for i in range(data_split[0].index(' ')):
		cmd += data_split[0][i]
	msg = data_split[2]
	return cmd, msg

	
def split_data(msg: str, expected_fields: int) -> List[str | ERROR_RETURN]:
	"""
	Helper method. Gets a string and number of expected fields in it. Splits the string 
	using protocol's data field delimiter (|#) and validates that there are correct number of fields.
	Returns: list of fields if all ok. If some error occured, returns None
	"""

	if expected_fields != msg.count(DATA_DELIMITER):
		return [ERROR_RETURN]
	return msg.split(DATA_DELIMITER)

def join_data(msg_fields: List) -> str:
	"""
	Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter. 
	Returns: string that looks like cell1#cell2#cell3
	"""

	msg = ""
	for i in range(len(msg_fields)-1):
		msg += msg_fields[i]
		msg += DATA_DELIMITER
	msg += msg_fields[-1]
	return msg
