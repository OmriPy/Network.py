##############################################################################
# server.py
##############################################################################

from socket import socket, AF_INET, SOCK_STREAM
from random import randint
from typing import Tuple, Dict, Any, List
import chatlib

# GLOBALS
users: Dict[str, Dict[str, Any]] = {
	'test': {
		'password': 'test',
		'score': 0,
		'questions_asked': []
	},
	'abc': {
		'password': '123',
		'score': 50,
		'questions_asked': []
	},
	'master': {
		'password': 'master',
		'score': 200,
		'questions_asked': []
	}
}
questions: Dict[int, List[str]] = {
	1: ['How much is 1+1?', '5', '6', '7', '2', '4'],
	2: ['What is the captial of USA?', 'Washington DC', 'NY', 'LA', 'Detroit', '1']
}
logged_users: Dict[socket, str] = {} # a dictionary of client hostnames to usernames - will be used later

SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn: socket, code: str, msg: str):
	"""
	Builds a new message using chatlib, wanted code and message. 
	Prints debug info, then sends it to the given socket.
	Paramaters: conn (socket object), code (str), data (str)
	Returns: Nothing
	"""

	full_msg = chatlib.build_message(code, msg)
	#print(full_msg)
	conn.send(full_msg.encode())
	print("[SERVER] ",full_msg)	  # Debug print


def recv_message_and_parse(conn: socket) -> Tuple[str, str] | Tuple[chatlib.ERROR_RETURN, chatlib.ERROR_RETURN]:
	"""
	Recieves a new message from given socket,
	then parses the message using chatlib.
	Paramaters: conn (socket object)
	Returns: cmd (str) and data (str) of the received message. 
	If error occured, will return None, None
	"""
	
	full_msg = conn.recv(chatlib.MAX_MSG_LENGTH)
	cmd, data = chatlib.parse_message(full_msg.decode())
	print("[CLIENT] ",full_msg.decode())	  # Debug print
	return cmd, data


# Data Loaders #

def load_questions():
	"""
	Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
	Recieves: -
	Returns: questions dictionary
	"""
	questions = {
				2313 : {"question":"How much is 2+2","answers":["3","4","2","1"],"correct":2},
				4122 : {"question":"What is the capital of France?","answers":["Lion","Marseille","Paris","Montpellier"],"correct":3} 
				}
	
	return questions

def load_user_database():
	"""
	Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
	Recieves: -
	Returns: user dictionary
	"""
	users = {
			"test"		:	{"password":"test","score":0,"questions_asked":[]},
			"yossi"		:	{"password":"123","score":50,"questions_asked":[]},
			"master"	:	{"password":"master","score":200,"questions_asked":[]}
			}
	return users

	
# SOCKET CREATOR

def setup_socket() -> socket:
	"""
	Creates new listening socket and returns it
	Recieves: -
	Returns: the socket object
	"""

	sock = socket(AF_INET, SOCK_STREAM)
	try:
		sock.bind((SERVER_IP, SERVER_PORT))
	except OSError:
		print("Try again later")
		exit()
	sock.listen()
	return sock

		
def send_error(conn: socket, error_msg: str):
	"""
	Send error message with given message
	Recieves: socket, message error string from called function
	Returns: None
	"""
	
	build_and_send_message(
		conn,
		chatlib.PROTOCOL_SERVER.get(chatlib.LOGIN_FAILED_MSG),
		error_msg)

	

##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
	global users

	build_and_send_message(
		conn,
		chatlib.PROTOCOL_SERVER.get(chatlib.YOUR_SCORE),
		str(users.get(username).get('score'))
	)


def handle_highscore_message(conn: socket):
	scores_unsorted: Tuple[List[str], List[int]] = ([], [])
	for user, info_dict in users.items():
		scores_unsorted[0].append(user)
		scores_unsorted[1].append(info_dict.get('score'))

	scores_sorted: Tuple[List[str], List[int]] = ([], [])
	for user in users.keys():
		max_score = max(scores_unsorted[1])
		max_user = scores_unsorted[0][scores_unsorted[1].index(max_score)]
		scores_sorted[0].append(max_user)
		scores_sorted[1].append(max_score)
		scores_unsorted[0].remove(max_user)
		scores_unsorted[1].remove(max_score)

	users_scores: List[str] = []
	for i in range(len(scores_sorted[0])):
		users_scores.append(f'{scores_sorted[0][i]}: {scores_sorted[1][i]}')

	build_and_send_message(
		conn,
		chatlib.PROTOCOL_SERVER.get(chatlib.ALL_SCORES),
		'\n'.join(users_scores))


def handle_logged_message(conn: socket):
	users_list = [user for user in users.keys()]
	build_and_send_message(
		conn,
		chatlib.PROTOCOL_SERVER.get(chatlib.ANSWER_TO_LOGGED),
		', '.join(users_list)
	)

	
def handle_logout_message(conn: socket):
	"""
	Closes the given socket (in later chapters, also remove user from logged_users dictioary)
	Recieves: socket
	Returns: None
	"""
	global logged_users

	logged_users.pop(conn)
	conn.close()


def handle_login_message(conn: socket, data: str):
	"""
	Gets socket and message data of login message. Checks  user and pass exists and match.
	If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
	Recieves: socket, message code and data
	Returns: None (sends answer to client)
	"""
	global users  # This is needed to access the same users dictionary from all functions
	global logged_users	 # To be used later
	
	username, password = data.split(chatlib.DATA_DELIMITER)
	if not username in users.keys():
		send_error(conn, chatlib.Errors.USER_NOT_LOGGED_IN)
	elif users.get(username).get('password') != password:
		send_error(conn, chatlib.Errors.INCORRECT_PASSWORD)
	else:
		build_and_send_message(
			conn,
			chatlib.PROTOCOL_SERVER.get(chatlib.LOGIN_OK_MSG),
			'')
		logged_users.update({conn: username})


def create_random_question() -> str:
	global questions
	questions_local = {}
	for key, value in questions.items():
		cur_info_list = [val for val in value]
		questions_local.update({key: cur_info_list})
	question_id = randint(1, len(questions_local.keys()))
	questions_local = questions_local.get(question_id)
	questions_local.pop()
	questions_local.insert(0, str(question_id))
	questions_local = chatlib.DATA_DELIMITER.join(questions_local)
	return questions_local


def handle_question_message(conn: socket):
	build_and_send_message(
		conn,
		chatlib.PROTOCOL_SERVER.get(chatlib.YOUR_QUESTION),
		create_random_question()
	)


def handle_answer_message(conn: socket, data: str):
	global users, questions, logged_users
	id, choice = data.split(chatlib.DATA_DELIMITER)
	correct_ans = questions.get(int(id))
	correct_ans = correct_ans[-1]
	if correct_ans == choice:
		build_and_send_message(
			conn,
			chatlib.PROTOCOL_SERVER.get(chatlib.CORRECT_ANSWER),
			''
		)
		users.get(logged_users.get(conn))['score'] += 5
	else:
		build_and_send_message(
			conn,
			chatlib.PROTOCOL_SERVER.get(chatlib.WRONG_ANSWER),
			correct_ans
		)


def handle_client_message(conn: socket, cmd: str, data: str):
	"""
	Gets message code and data and calls the right function to handle command
	Recieves: socket, message code and data
	Returns: None
	"""
	global logged_users
	
	if conn in logged_users.keys():
		if cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.LOGOUT_MSG):
			handle_logout_message(conn)
		elif cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.SCORE):
			handle_getscore_message(conn, logged_users.get(conn))
		elif cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.HIGH_SCORE):
			handle_highscore_message(conn)
		elif cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.LOGGED_USERS):
			handle_logged_message(conn)
		elif cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.GET_QUESTION):
			handle_question_message(conn)
		elif cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.SEND_ANSWER):
			handle_answer_message(conn, data)
		else:
			send_error(conn, chatlib.Errors.UNKNOWN_COMMAND)
	else:
		if cmd == chatlib.PROTOCOL_CLIENT.get(chatlib.LOGIN_MSG):
			handle_login_message(conn, data)
		else:
			send_error(conn, chatlib.Errors.INAPPROPRIATE_REQUEST)



def main():
	# Initializes global users and questions dicionaries using load functions, will be used later
	global users
	global questions
	server = setup_socket()
	print("Welcome to Trivia Server!")
	while True: # for each client
		cmd = ''
		try:
			client, client_address = server.accept()
		except KeyboardInterrupt:
			print("\nServer disconnected by ctrl+c")
			try:
				client.close()
			except UnboundLocalError: # if no client is connected
				pass
			server.close()
			return
		print(f"\nNew client has joined!\t{client.getpeername()}")
		while cmd != chatlib.PROTOCOL_CLIENT.get(chatlib.LOGOUT_MSG): # for each command
			try:
				cmd, data = recv_message_and_parse(client)
				if (cmd, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
					print('Some error occured!')
					break
				else:
					handle_client_message(client, cmd, data)
			except KeyboardInterrupt:
				print("\nServer disconnected by ctrl+c")
				send_error(client, chatlib.Errors.CTRL_C_SERVER)
				client.close()
				server.close()
				return



if __name__ == '__main__':
	main()