
import re

class CCGBankUtils:

    @staticmethod
    def word_re():
        # <L N NN NN question N>
        return re.compile('<L [^\s>]+ [^\s>]+ [^\s>]+ [^\s>]+ [^\s>]+>')

    @staticmethod
    def phrase_re():
        # <T NP 0 2>
        return re.compile('<T (?P<tag>[^\s>]+) [^\s>]+ [^\s>]+>')

    @staticmethod
    def word_iter(ccg_code):
        return re.finditer('<L (?P<tag>[^\s>]+) (?P<pos>[^\s>]+) [^\s>]+ (?P<word>[^\s>]+) [^\s>]+>', ccg_code)

    @staticmethod
    def is_word(ccg_code):
        # <L N NN NN question N>
        return re.match('^<L [^\s>]+ [^\s>]+ [^\s>]+ [^\s>]+ [^\s>]+>$', ccg_code)

    @staticmethod
    def is_phrase(ccg_code):
        # <T NP 0 2>
        return re.match('^<T [^\s>]+ [^\s>]+ [^\s>]+>$', ccg_code)

    @staticmethod
    def get_tag(ccg_code):
        return ccg_code.split()[1]

    @staticmethod
    def get_word(ccg_code):
        return ccg_code.split()[4]

    @staticmethod
    def get_pos(ccg_code):
        return ccg_code.split()[2]

