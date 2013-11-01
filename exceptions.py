
class FileNotFoundError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class SiteAlreadyInstalledError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class PageExistsError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class ValuesNotDefinedError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg
