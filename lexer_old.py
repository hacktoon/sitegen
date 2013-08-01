
class Token():
	def __init__(self, token):
		self.value = self.clean_tag(token)
		self.type = self.get_type(token)

	def clean_tag(self, token):
		if TAG_REGEX.search(token):
			return CLEAR_TAG_REGEX.sub('', token).strip()
		return token

	def get_type(self, token):
		if TOKEN_BLOCK_START in token:
			if self.value == 'end':
				return CLOSE_BLOCK_TOKEN
			else:
				return OPEN_BLOCK_TOKEN
		if TOKEN_VAR_START in token:
			return VAR_TOKEN
		return TEXT_TOKEN
	
	def __str__(self):
		return '{!r} - {}'.format(self.type, self.value)



scanner = Scanner(template)
scanner.getChar()
