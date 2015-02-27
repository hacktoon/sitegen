
class TemplateError(Exception):
	pass


class NodeError(Exception):
	def __init__(self, msg, token, parser):
		self.token = token
		self.parser = parser
		super().__init__(msg)


class RuntimeError(NodeError):
	pass


class FileNotFoundError(NodeError):
	pass
