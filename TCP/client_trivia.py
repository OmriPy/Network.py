from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple, Dict, Callable
import chatlib

SERVER_IP = '127.0.0.1'
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
			chatlib.Protocol_Client.LOGIN,
			data)
		cmd, data = recv_message_and_parse(conn)
		if cmd == chatlib.Protocol_Server.ERROR:
			print(f"Login Failed: {data}\n")
			if data == chatlib.Errors.CTRL_C_SERVER:
				error_and_exit(data)
		else:
			print("Successful Login\n")
			return


def logout(conn: socket):
	build_and_send_message(
		conn,
		chatlib.Protocol_Client.LOGOUT,
		'')


def build_send_recv_parse(conn: socket, code: str, data: str) -> Tuple[str, str] | Tuple[chatlib.ERROR_RETURN, chatlib.ERROR_RETURN]:
	build_and_send_message(conn, code, data)
	return recv_message_and_parse(conn)


def get_score(conn: socket):
	cmd, data = build_send_recv_parse(
		conn,
		chatlib.Protocol_Client.MY_SCORE,
		'')
	if (cmd, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	print(f'Score:\t{data}')


def get_highscore(conn: socket):
	cmd, data = build_send_recv_parse(
		conn,
		chatlib.Protocol_Client.HIGHSCORE,
		'')
	if (cmd, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	print(f'Highscore:\n{data}')


def play_question(conn: socket):
	cmd, data = build_send_recv_parse(
		conn,
		chatlib.Protocol_Client.GET_QUESTION,
		'')
	if (cmd, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	data = data.split(chatlib.DATA_DELIMITER)
	if len(data) != 6 or cmd != chatlib.Protocol_Server.YOUR_QUESTION:
		print('Some error occured!')
		return
	id = data[0]
	question = data[1]
	possible_answers = [data[i] for i in range(2, len(data))]
	print(question)
	for i in range(len(possible_answers)):
		print(f'{i+1}. {possible_answers[i]}')
	choice = input("Enter answer number [1-4]:\t")
	if not choice.isnumeric() or int(choice) < 1 or int(choice) > 4:
		print('Some error occured!')
		return
	cmd, data = build_send_recv_parse(
		conn,
		chatlib.Protocol_Client.SEND_ANSWER,
		f'{id}{chatlib.DATA_DELIMITER}{choice}')
	if (cmd, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
		print('Some error occured!')
		return
	if cmd == chatlib.Protocol_Server.CORRECT_ANSWER:
		print("Correct!")
	elif cmd == chatlib.Protocol_Server.WRONG_ANSWER:
		print(f'Wrong!\nThe correct answer was {data}')


def get_logged_users(conn: socket):
	cmd, data = build_send_recv_parse(
		conn,
		chatlib.Protocol_Client.LOGGED,
		'')
	if (cmd, data) == (chatlib.ERROR_RETURN, chatlib.ERROR_RETURN):
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
			build_and_send_message(
				sock,
			  	chatlib.Protocol_Client.DISCONNECTION,
				chatlib.Errors.CTRL_C_CLIENT)
			error_and_exit(chatlib.Errors.CTRL_C_CLIENT)
		if choice in CHOICES.keys():
			CHOICES.get(choice)(sock)
		if choice == 'e':
			break
	sock.close()


if __name__ == '__main__':
    main()
