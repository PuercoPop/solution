# -*- coding: utf-8 -*-
import datetime
import re
import urlparse

from .utils import to_unicode


__all__ = ['Required', 'IsNumber', 'IsNaturalNumber', 'IsDate',
    'LongerThan', 'ShorterThan', 'LessThan', 'MoreThan', 'InRange', 'Match',
    'IsColor', 'ValidEmail', 'ValidURL', 'Before', 'After',
    'BeforeNow', 'AfterNow', 'FormValidator', 'AreEqual',]


class Required(object):
    """Validates that the field contains data.

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'required'
    
    def __init__(self, message=None):
        if message is None:
            message = u'This field is required.'
        self.message = message

    def __call__(self, python_value):
        return bool(python_value)


class IsNumber(object):
    """Validates that the field is a number (integer or floating point).

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'invalid'
    
    def __init__(self, message=None):
        if message is None:
            message = u'Enter a number.'
        self.message = message

    def __call__(self, python_value):
        try:
            float(python_value)
        except Exception:
            return False
        return True


class IsNaturalNumber(object):
    """Validates that the field is a natural number (positive integer
    including zero).

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'invalid'
    
    def __init__(self, message=None):
        if message is None:
            message = u'Enter a positive integer number.'
        self.message = message

    def __call__(self, python_value):
        try:
            n = int(str(python_value), 10)
        except Exception:
            return False
        return n >= 0


class IsDate(object):
    """Validates that the field is a date or a datetime.

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'invalid'
    
    def __init__(self, message=None):
        if message is None:
            message = u'Enter a valid date.'
        self.message = message

    def __call__(self, python_value):
        return isinstance(python_value, datetime.date)


class LongerThan(object):
    """Validates the length of a string is longer or equal than minimum.

    :param length:
        The minimum required length of the string.

    :param message:
        Error message to raise in case of a validation error
    """
    code = 'too_short'

    def __init__(self, length, message=None):
        assert isinstance(length, int)
        self.length = length
        if message is None:
            message = u'Field must be at least %d character long.' % length
        self.message = message

    def __call__(self, python_value):
        return len(str(python_value or u'')) >= self.length


class ShorterThan(object):
    """Validates the length of a string is shorter or equal than maximum.

    :param length:
        The maximum allowed length of the string.

    :param message:
        Error message to raise in case of a validation error
    """
    code = 'too_long'

    def __init__(self, length, message=None):
        assert isinstance(length, int)
        self.length = length
        if message is None:
            message = u'Field cannot be longer than %d character.' % length
        self.message = message

    def __call__(self, python_value):
        return len(str(python_value or u'')) <= self.length


class LessThan(object):
    """Validates that a number is less or equal than a value.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param value:
        The maximum value of the number.

    :param message:
        Error message to raise in case of a validation error
    """
    code = 'too_big'

    def __init__(self, value, message=None):
        self.value = value
        if message is None:
            message = u'Number must be less than %d.' % value
        self.message = message

    def __call__(self, python_value):
        value = python_value or 0
        return value <= self.value


class MoreThan(object):
    """Validates that a number is greater or equal than a value.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param value:
        The minimum value of the number.

    :param message:
        Error message to raise in case of a validation error
    """
    code = 'too_small'

    def __init__(self, value, message=None):
        self.value = value
        if message is None:
            message = u'Number must be greater than %s.' % value
        self.message = message

    def __call__(self, python_value):
        value = python_value or 0
        return value >= self.value


class InRange(object):
    """Validates that a number is of a minimum and/or maximum value.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param minval:
        The minimum value of the number.

    :param maxval:
        The maximum value of the number.

    :param message:
        Error message to raise in case of a validation error
    """

    def __init__(self, minval, maxval, message=None):
        self.minval = minval
        self.maxval = maxval
        if message is None:
            message = u'Number must be between %s and %s.' % (minval, maxval)
        self.message = message

    def __call__(self, python_value):
        value = python_value or 0
        if value < self.minval:
            self.code = 'too_small'
            return False
        if value > self.maxval:
            self.code = 'too_big'
            return False
        return True


class Match(object):
    """Validates the field against a regular expression.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.

    :param flags:
        The regexp flags to use. By default re.IGNORECASE.
        Ignored if `regex` is not a string.

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'invalid'

    def __init__(self, regex, flags=re.IGNORECASE, message=None):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex

        if message is None:
            message = u'This value doesn\'t seem to be valid.'
        self.message = message

    def __call__(self, python_value):
        return self.regex.match(python_value or u'')


class IsColor(Match):
    """Validates that the field is a string representing a rgb or rgba color
    in the format `#rrggbb[aa]`.

    :param message:
        Error message to raise in case of a validation error.
    """
    regex = re.compile(r'#[0-9a-f]{6,8}', re.IGNORECASE)

    def __init__(self, message=None):
        if message is None:
            message = u'Enter a valid color.'
        self.message = message


class ValidEmail(object):
    """Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, or wen it doesn't matters very much the email is real.

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'invalid_email'

    _email_re = re.compile(
        r'''(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*'''  # dot-atom
        r'''|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"''' # quoted-string
        r''')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$''',
        re.IGNORECASE)

    def __init__(self, message=None):
        self.regex = self._email_re
        if message is None:
            message = u'Enter a valid e-mail address.'
        self.message = message

    def __call__(self, python_value):
        value = python_value or ''
        if self.regex.match(value):
            return True
        # Common case failed. Try for possible IDN domain-part
        if value and u'@' in value:
            parts = python_value.split(u'@')
            domain_part = parts[-1]
            try:
                parts[-1] = parts[-1].encode('idna')
            except UnicodeError:
                return False
            value = u'@'.join(parts)
            if self._email_re.match(value):
                return True
        return False


class ValidURL(object):
    """Simple regexp based URL validation. Much like the IsEmail validator, you
    probably want to validate the URL later by other means if the URL must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'invalid_url'

    _url_re = ur'^([a-z]{3,7}:(//)?)?([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$'

    def __init__(self, require_tld=True, message=None):
        tld_part = ur'\.[a-z]{2,10}' if require_tld else u''
        self.regex = re.compile(self._url_re % tld_part, re.IGNORECASE)
        if message is None:
            message = u'Enter a valid URL.'

    def __call__(self, python_value):
        value = python_value or ''
        if self.regex.match(value):
            return True
        # Common case failed. Try for possible IDN domain-part
        if value:
            value = to_unicode(value)
            scheme, netloc, path, query, fragment = urlparse.urlsplit(value)
            try:
                netloc = netloc.encode('idna') # IDN -> ACE
            except UnicodeError: # invalid domain part
                return False
            value = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
            if self.regex.match(value):
                return True
        return False


class Before(object):
    """Validates than the date happens before another.
    This will work with both date and datetime values.

    :param date:
        The latest valid date. 

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'too_late'

    def __init__(self, date, message=None):
        assert isinstance(date, datetime.date)
        if not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month. date.day)
        self.date = date

        if message is None:
            # TODO: Improve this!!!!
            str_date = date.isoformat()
            message = u'Enter a valid date before %s.' % str_date
        self.message = message

    def __call__(self, python_value):
        value = python_value
        if not isinstance(value, datetime.date):
            return False
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month. value.day)
        return value <= self.date


class After(object):
    """Validates than the date happens after another.
    This will work with both date and datetime values.

    :param date:
        The soonest valid date. 

    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'too_soon'

    def __init__(self, date, message=None):
        assert isinstance(date, datetime.date)
        if not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month. date.day)
        self.date = date

        if message is None:
            # TODO: Improve this!!!!
            str_date = date.isoformat()
            message = u'Enter a valid date after %s.' % str_date
        self.message = message

    def __call__(self, python_value):
        value = python_value
        if not isinstance(value, datetime.date):
            return False
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month. value.day)
        return value >= self.date


class BeforeNow(Before):
    """Validates than the date happens before now.
    This will work with both date and datetime values.

    :param message:
        Error message to raise in case of a validation error.
    """
    
    def __init__(self, message=None):
        if message is None:
            message = u'Enter a valid date in the past.'
        self.message = message

    def __call__(self, python_value):
        self.date = datetime.datetime.utcnow()
        return super(BeforeNow, self).__call__(python_value)


class AfterNow(After):
    """Validates than the date happens after now.
    This will work with both date and datetime values.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None):
        if message is None:
            message = u'Enter a valid date in the future.'
        self.message = message

    def __call__(self, python_value):
        self.date = datetime.datetime.utcnow()
        return super(AfterNow, self).__call__(python_value)


class FormValidator(object):
    """Base Form Validator."""
    pass


class AreEqual(FormValidator):
    """Form validator that assert that two fields have the same value.

    :param name1:
        Name of the first field
    :param name2:
        Name of the second field
    :param plural:
        Collective name of the fields. Eg.: 'passwords'
    :param message:
        Error message to raise in case of a validation error.
    """
    code = 'not_equal'
    
    def __init__(self, name1, name2, plural=u'fields', message=None):
        self.name1 = name1
        self.name2 = name2
        if message is None:
            message = u'The %s doesn\'t match.' % plural
        self.message = message

    def __call__(self, data):
        return data.get(self.name1) == data.get(self.name2)
