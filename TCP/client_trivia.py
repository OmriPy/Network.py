from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple, Dict, Callable
import chatlib

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678

# HELPER SOCKET METHODS

def build_and_send_message(conn: socket, code: str, data: str):
	"""
	Builds a new message using chatlib, wanted code and message. 
	Prints debug info, then sends it to the given socket.
	Paramaters: conn (socket object), code (str), data (str)
	Returns: Nothing
	"""

	msg = chatlib.build_message(code, data)
	print(msg)
	conn.send(msg.encode())

	

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
	return cmd, data
	
	

def connect() -> socket:
	sock = socket(AF_INET, SOCK_STREAM)
	sock.connect((SERVER_IP, SERVER_PORT))
	return sock


def error_and_exit(error_msg: str):
    print(error_msg)
    exit()


def login(conn: socket):
	while True:
		username = input("Enter username:\t")
		password = input("Enter password:\t")
		data = f'{username}{chatlib.DATA_DELIMITER}{password}'
		build_and_send_message(
			conn,
			chatlib.PROTOCOL_CLIENT.get(chatlib.LOGIN_MSG),
			data)
		code, data = recv_message_and_parse(conn)
		if code == chatlib.PROTOCOL_SERVER.get(chatlib.LOGIN_FAILED_MSG):
			print(f"Login Failed - {data}\n")
			if data == chatlib.Errors.CTRL_C_SERVER:
				error_and_exit(data)
		else:
			print("Successful Login\n")
			return


def logout(conn: socket):
	build_and_send_message(
		conn,
		chatlib.PROTOCOL_CLIENT.get(chatlib.LOGOUT_MSG),
		"")


def build_send_recv_parse(conn: socket, code: str, data: str) -> Tuple[str, str] | Tuple[chatlib.ERROR_RETURN, chatlib.ERROR_RETURN]:
	build_and_send_message(conn, code, data)
	return recv_message_and_parse(conn)


def get_score(conn: socket):
	msg = build_send_recv_parse(
		conn,
		chatlib.PROTOCOL_CLIENT.get(chatlib.SCORE),
		'')
	if msg == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	print(f'Score:\t{msg[1]}')


def get_highscore(conn: socket):
	msg = build_send_recv_parse(conn,
		chatlib.PROTOCOL_CLIENT.get(chatlib.HIGH_SCORE),
		'')
	if msg == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	print(f'Highscore:\n{msg[1]}')


def play_question(conn: socket):
	code, data = build_send_recv_parse(
		conn,
		chatlib.PROTOCOL_CLIENT.get(chatlib.GET_QUESTION),
		'')
	if (code, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	data = data.split(chatlib.DATA_DELIMITER)
	if len(data) != 6 or code != 'YOUR_QUESTION':
		print('Some error occured!')
		return
	id = data[0]
	question = data[1]
	possible_answers = [data[i] for i in range(2, len(data))]
	print(question + '\n' +
        f'1. {possible_answers[0]}\n' + 
		f'2. {possible_answers[1]}\n' + 
		f'3. {possible_answers[2]}\n' + 
		f'4. {possible_answers[3]}\n')
	choice = input("Enter answer number [1-4]:\t")
	if int(choice) < 1 or int(choice) > 4:
		print('Some error occured!')
		return
	code, data = build_send_recv_parse(
		conn,
		chatlib.PROTOCOL_CLIENT.get(chatlib.SEND_ANSWER),
		f'{id}{chatlib.DATA_DELIMITER}{choice}')
	if (code, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	if code == 'CORRECT_ANSWER':
		print("Correct!")
	elif code == 'WRONG_ANSWER':
		print(f'Wrong!\nThe correct answer was {data}')


def get_logged_users(conn: socket):
	code, data = build_send_recv_parse(
		conn,
		chatlib.PROTOCOL_CLIENT.get(chatlib.LOGGED_USERS),
		'')
	if (code, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	print(data)


CHOICES: Dict[str, Callable] = {
	'li': login,
	'p': play_question,
	's': get_score,
	'h': get_highscore,
	'lu': get_logged_users,
	'e': logout,
}

def main():
	sock = connect()
	choice = ""
	while choice != 'li':
		print("li\t->\tLogin\n")
		try:
			choice = input("Enter your choice:\t").lower()
		except KeyboardInterrupt:
			error_and_exit(chatlib.Errors.CTRL_C_CLIENT)
	try:
		CHOICES.get(choice)(sock)
	except ConnectionResetError:
		error_and_exit(chatlib.Errors.CTRL_C_SERVER)
	while True:
		print("\n" +
			"p\t->\tPlay trivia question\n" +
			"s\t->\tGet score\n" +
			"h\t->\tGet high score\n" +
			"lu\t->\tLogged users\n" +
			"e\t->\tExit\n")
		try:
			choice = input("Enter your choice:\t").lower()
		except KeyboardInterrupt:
			error_and_exit(chatlib.Errors.CTRL_C_CLIENT)
		if choice in CHOICES.keys():
			CHOICES.get(choice)(sock)
		if choice == 'e':
			break
	sock.close()


if __name__ == '__main__':
    main()