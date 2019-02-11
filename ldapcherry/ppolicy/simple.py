# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
#
# The MIT License (MIT)
# LdapCherry
# Copyright (c) 2014 Carpentier Pierre-Francois

import ldapcherry.ppolicy
import re
import string


class PPolicy(ldapcherry.ppolicy.PPolicy):

    def __init__(self, config, logger):
        self.config = config
        self.min_length = self.get_param('min_length')
        self.min_lower = self.get_param('min_lower')
        self.min_upper = self.get_param('min_upper')
        self.min_digit = self.get_param('min_digit')
        self.min_punct = self.get_param('min_punct')
        self.min_point = self.get_param('min_point')

    def check(self, password):
        point = 0
        reason = 'Not enough complexity'

        if len(password) < self.min_length:
            return {'match': False, 'reason': 'Password too short'}

        if len(re.findall(r'[a-z]', password)) < self.min_lower:
            reason = 'Not enough lower case characters'
        else:
            point += 1
        if len(re.findall(r'[A-Z]', password)) < self.min_upper:
            reason = 'Not enough upper case characters'
        else:
            point += 1

        if len(re.findall(r'[0-9]', password)) < self.min_digit:
            reason = 'Not enough digits'
        else:
            point += 1

        punctuation = 0
        for char in password:
            if char in string.punctuation:
                punctuation += 1
        if punctuation < self.min_punct:
            reason = 'Not enough special caracter'
        else:
            point += 1

        if point < self.min_point:
            return {'match': False, 'reason': reason}

        return {'match': True, 'reason': 'password ok'}

    def info(self):
        return \
            "* Minimum length: %(len)d\n" \
            "* Minimum number of lowercase characters: %(lower)d\n" \
            "* Minimum number of uppercase characters: %(upper)d\n" \
            "* Minimum number of digits: %(digit)d\n" \
            "* Minimum number of punctuation characters: %(punct)d" % {
                'len': self.min_length,
                'lower': self.min_lower,
                'upper': self.min_upper,
                'digit': self.min_digit
                'punct': self.min_punct,
                }
