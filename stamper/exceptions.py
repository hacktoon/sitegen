
class TemplateError(Exception):
	pass


class RuntimeError(Exception):
	def __init__(self, msg, token):
		self.token = token
		super().__init__(msg)


class FileNotFoundError(Exception):
	def __init__(self, msg, token):
		self.token = token
		super().__init__(msg)
		