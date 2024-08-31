quote_dict = {
    '"': '"',
    "‘": "’",
    "‛": "‚",
    "“": "”",
    "‟": "„",
    "⹂": "⹂",
    "「": "」",
    "『": "』",
    "〝": "〞",
    "﹁": "﹂",
    "﹃": "﹄",
    "＂": "＂",
    "｢": "｣",
    "«": "»",
    "‹": "›",
    "《": "》",
    "〈": "〉",
}


class StringView:
    def __init__(self, string: str):
        self.string: str = string
        self.current_index: str = 0
        self.temp: str = ""
        self.should_undo: bool = False

    @property
    def eof(self):
        return self.current_index >= len(self.string)

    def get_rest(self):
        if self.should_undo:
            word = f"{self.temp}{self.string[self.current_index:]}"
        else:
            word = self.string[self.current_index:].lstrip(" ")
        self.current_index = len(self.string)
        return word

    def undo(self):
        self.should_undo = True

    def get_next_word(self):
        if self.should_undo is True:
            self.should_undo = False
            return self.temp

        while self.string[self.current_index] in [" ", "\n"]:
            self.current_index += 1

        char = self.string[self.current_index]

        if char in quote_dict:
            next_quote = quote_dict[char]
            remaining = self.string[self.current_index + 1:]
            if next_quote in remaining:
                index = self.string.index(next_quote, self.current_index + 1)
                word = self.string[self.current_index + 1:index]
                self.current_index = index + 1

                self.temp = word
                return word

        word = ""
        while char not in [" ", "\n"]:
            try:
                word += char
                self.current_index += 1
                char = self.string[self.current_index]
            except IndexError:
                break

        self.temp = word
        return word
