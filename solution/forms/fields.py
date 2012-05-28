# -*- coding: utf-8 -*-
import inspect
import re
from xml.sax.saxutils import quoteattr

from . import validators as v
from .utils import to_unicode

try:
    from jinja2 import Markup
except ImportError:
    Markup = unicode


__all__ = ['Markup', 'ValidationError', 'Field', 'File', 'Text',
    'Password', 'Number', 'Email', 'URL', 'Date',
    'DateTime', 'Color',]


class ValidationError(object):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __repr__(self):
        return '<ValidationError %s: %s>' % (self.code, self.message)


class Field(object):
    """A base form field. All fields must inherit from this class.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """

    _value = u''
    error = None
    name = 'unnamed'

    hide_value = False
    has_changed = False

    def __init__(self, *validators, **kwargs):
        self.validators = [val() if inspect.isclass(val) else val
            for val in validators]
        self.optional = not self._validator_in(v.Required, validators)
        # Extensibility FTW
        self.extra = kwargs

    def reset(self):
        self._value = None
        self.error = None

    def _validator_in(self, validator, validators):
        for v in validators:
            if (v == validator) or isinstance(v, validator):
                return True
        return False

    def load_value(self, python_value):
        self._value = self.to_html(python_value)

    def _get_value(self):
        return self._value if self._value and not self.hide_value else u''

    def _set_value(self, value):
        if isinstance(value, list):
            value = value[0] if value else u''
        elif value is None:
            value = u''
        self._value = value.strip()

    value = property(_get_value, _set_value)

    def to_html(self, python_value):
        return to_unicode(python_value or u'')

    def to_python(self):
        if self._value is None:
            return None
        value = self._value.strip()
        if value == u'':
            return None 
        return to_unicode(value)

    def validate(self, cleaned_data=None):
        """Validates the current value of a field.
        """
        if cleaned_data is None:
            python_value = self.to_python()
            # Do not validate optional fields
            if python_value is None and self.optional:
                return None
            self._validate_value(python_value)
            return python_value
        self._validate_form(cleaned_data)

    def _validate_value(self, python_value):
        for val in self.validators:
            if isinstance(val, v.FormValidator):
                continue
            if not val(python_value):
                self.error = ValidationError(val.code, val.message)
                break

    def _validate_form(self, cleaned_data):
        for val in self.validators:
            if not isinstance(val, v.FormValidator):
                continue
            if not val(python_value):
                self.error = ValidationError(val.code, val.message)
                break

    def _get_html_attrs(self, kwargs=None):
        """Generate HTML attributes from the provided keyword arguments.

        The output value is sorted by the passed keys, to provide consistent
        output.  Because of the frequent use of the normally reserved keyword
        `class`, `classes` is used instead. Also, all underscores are translated
        to regular dashes.

        Set any property with a `True` value.

        >>> _get_html_attrs({'id': 'text1', 'classes': 'myclass',
            'data_id': 1, 'checked': True})
        u'class="myclass" data-id="1" id="text1" checked'

        """
        kwargs = kwargs or {}
        attrs = []
        props = []

        classes = kwargs.get('classes', '').strip()
        if classes:
            classes = ' '.join(re.split(r'\s+', classes))
            classes = to_unicode(quoteattr(classes))
            attrs.append('class=%s' % classes)
        try:
            del kwargs['classes']
        except KeyError:
            pass

        for key, value in kwargs.iteritems():
            key = key.replace('_', '-')
            key = to_unicode(key)
            if isinstance(value, bool):
                if value is True:
                    props.append(key)
            else:
                value = quoteattr(to_unicode(value))
                attrs.append(u'%s=%s' % (key, value))

        attrs.sort()
        props.sort()
        attrs.extend(props)
        return u' '.join(attrs)

    def __unicode__(self):
        """Returns a HTML representation of the field. For more powerful 
        rendering, see the `__call__` method.
        """
        return self()

    def __str__(self):
        """Returns a HTML representation of the field. For more powerful 
        rendering, see the `__call__` method.
        """
        return self()

    def __html__(self):
        """Returns a HTML representation of the field. For more powerful 
        rendering, see the `__call__` method.
        """
        return self()

    def __call__(self, **kwargs):
        raise NotImplemented


class Text(Field):
    """A text field.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` will be
        returned instead.
    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'text'
    _default_validator = None

    def __init__(self, *validators, **kwargs):
        defval = self._default_validator
        validators = list(validators)
        if defval and not self._validator_in(defval, validators):
            validators.append(defval())

        super(Text, self).__init__(*validators, **kwargs)

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        if not 'type' in kwargs:
            kwargs['type'] = self._type
        kwargs['name'] = self.name
        kwargs['value'] = self.value
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<input %s>' % html_attrs
        return Markup(html)

    def as_textarea(self, **kwargs):
        kwargs['name'] = self.name
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, self.value)
        return Markup(html)


class Password(Text):
    """A password field.

    :param hide_value:
        If `True` this field will not reproduce the value on a form
        submit by default. This is the default for security purposes.
    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'password'

    def __init__(self, hide_value=True, *validators, **kwargs):
        self.hide_value = hide_value
        super(Password, self).__init__(*validators, **kwargs)


class Number(Text):
    """A number field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'number'
    _default_validator = v.IsNumber

    def to_python(self):
        try:
            return float(self._value)
        except Exception:
            return None


class NaturalNumber(Text):
    """A natural number (positive integer including zero) field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'number'
    _default_validator = v.IsNaturalNumber

    def to_python(self):
        try:
            return int(str(self._value), 10)
        except Exception:
            return None


class Email(Text):
    """An email field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'email'
    _default_validator = v.ValidEmail


class URL(Text):
    """An URL field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'url'
    _default_validator = v.ValidURL


class Date(Text):
    """A date field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'datetime'
    _default_validator = v.IsDate


class DateTime(Text):
    """A datetime field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'datetime'
    _default_validator = v.IsDate


class Color(Text):
    """A color field.

    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    _type = 'color'
    _default_validator = v.IsColor

    _re_colors = re.compile(
        r'#?(?P<hex>[0-9a-f]){3,8}|'
        r'rgba?\((?P<r>[0-9]+),(?P<g>[0-9]+),(?P<b>[0-9]+)'
        r'(?:,(?P<a>[0-9]+))?\)',
        re.IGNORECASE)

    def to_python():
        if not self._value:
            return None
        m = self._re_colors(self._value.replace(' ', ''))
        if not m:
            return None
        md = m.groupdict()
        if 'hex' in md:
            return self._normalize_hex(md['hex'])
        return self._normalize_rgb(md['r'], md['g'], md['b'], md.get('a'))

    def _normalize_hex(self, hc):
        """Transform a xxx hex color to xxxxxx.
        """
        lhc = len(hc)
        if lhc not in (3, 4, 6, 8):
            return None
        hc = hc.lower()
        if lhc >= 6:
            return '#' + hc
        nhc = u'#%s%s%s' % (hc[0] * 2, hc[1] * 2, hc[2] * 2)
        if lhc == 4:
            nhc += hc[3] * 2
        return nhc

    def _normalize_rgb(self, r, g, b, a):
        """Transform a rgb[a] color to #rgb[a].
        """
        r = int(r, 10)
        g = int(g, 10)
        b = int(b, 10)
        if a:
            a = int(a, 10)
        if r > 255 or g > 255 or b > 255 or (a and a > 255):
            return None
        color = '#%02x%02x%02x' % (r, g, b)
        if a:
            color += '%02x' % a
        return color


class File(Field):
    """ An uploaded file field.

    :param upload:
        Optional function to be call for doing the actual file upload. It must
        return a python value ready for validation.
    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """
    hide_value = True

    def __init__(self, upload=None, *validators, **kwargs):
        self.upload = upload
        super(File, self).__init__(*validators, **kwargs)

    def to_python(self, value):
        if not self.value:
            return None
        if self.upload:
            return self.upload(value)
        return value

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        kwargs['type'] = 'file'
        kwargs['name'] = self.name
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<input %s>' % html_attrs
        return Markup(html)


FALSY_VALUES = [u'', u'0', u'no', u'off', u'false',]

class Boolean(Field):
    """A True/False field.

    :param falsy:
        A list of raw values considered `False`.
    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """

    def __init__(self, falsy=FALSY_VALUES, *validators, **kwargs):
        self.falsy = falsy
        super(Boolean, self).__init__(*validators, **kwargs)

    def to_python(self, value):
        if not value or (value in self.falsy):
            return False
        return True

    def __call__(self, **kwargs):
        return self.as_checkbox(**kwargs)

    def as_checkbox(self, **kwargs):
        kwargs['type'] = 'checkbox'
        kwargs['name'] = self.name
        if self.value:
            kwargs['checked'] = True
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<input %s>' % html_attrs
        return Markup(html)

#------------------------------------------------------------------------------

class Select(Field):
    """A field with a fixed list of options for the values

    :param items:
        Either: 
        - An list of tuples with the format `(value, label)`; or
        - A function that return a list of items in that format.
    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` will be
        returned instead.
    :param *validators:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """

    def __init__(self, items, clean=None, *validators, **kwargs):
        self.items = items
        self.clean = clean
        super(Select, self).__init__(*validators, **kwargs)

    def get_items(self):
        return self.items() if callable(self.items) else self.items

    def to_python(self):
        value = self._value
        if self.clean:
            try:
                value = self.clean(value)
            except Exception:
                return None
        return value

    def __call__(self, **kwargs):
        items = self.get_items()
        if len(items) > 5:
            return self.as_select(_items=items, **kwargs)    
        return self.as_radiobuttons(_items=items, **kwargs)

    def as_select(self, _items=None, **kwargs):
        """Render the field as `<select>` element.
        
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`
        
        """
        kwargs['name'] = self.name
        html_attrs = self._get_html_attrs(kwargs)
        html = [u'<select %s>' % html_attrs]

        if _items is None:
            _items = self.get_items()
        curr_value = self.value
        for value, label in _items:
            item_attrs = {'value': value}
            if str(value) == curr_value:
                item_attrs['selected'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(u'<option %s>%s</option>' % (html_attrs, label))
        html.append(u'</select>')
        return Markup('\n'.join(html))

    def as_radiobuttons(self, _items=None, 
            tmpl=u'<label><input %(attrs)s> %(label)s</label>', **kwargs):
        """Render the field as a series of radio buttons, using the `tmpl`
        parameter as the template.
        
        :param tmpl:
            HTML template to use for rendering each item.
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`
        
        """
        if _items is None:
            _items = self.get_items()
        kwargs['type'] = 'radio'
        kwargs['name'] = self.name
        html = []
        curr_value = self.value
        for value, label in _items:
            item_attrs = kwargs.copy()
            item_attrs['value'] = value
            if str(value) == curr_value:
                item_attrs['checked'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(tmpl % {'attrs': html_attrs, 'label': label})
        return Markup('\n'.join(html))


class SelectMulti(Field):
    """A field with a fixed list of options for the values.
    Similar to `Select`, except this one can take (and validate)
    multiple choices.
    
    :param items:
        Either: 
        - An list of tuples with the format (value, label); or
        - A function that return a list of items in that format.
    :param clean:
        An optional function that takes a value and return a 'cleaned' version
        of it. If a value raise an exception it'll be filtered out from the
        final result.
    :param *validators:
        An list of validators. This will evaluate each of the selected values
        when the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """

    def __init__(self, items, clean=None, *validators, **kwargs):
        self.items = items
        self.clean = clean
        super(SelectMulti, self).__init__(*validators, **kwargs)

    def _get_value(self):
        return self._value if self._value and not self.hide_value else []

    def _set_value(self, value):
        if not isinstance(value, list):
            value = [value]
        self._value = value

    value = property(_get_value, _set_value)

    def get_items(self):
        return self.items() if callable(self.items) else self.items

    def to_python(self):
        values = self._value
        if self.clean:
            values_ = []
            for value in values:
                try:
                    values_.append(self.clean(value))
                except Exception:
                    pass
            values = values_
        return values

    def __call__(self, **kwargs):
        items = self.get_items()
        if len(items) > 5:
            return self.as_select(_items=items, **kwargs)    
        return self.as_checkboxes(_items=items, **kwargs)

    def as_select(self, _items=None, **kwargs):
        """Render the field as `<select multiple>` element.
        
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`
        
        """
        kwargs['name'] = self.name
        kwargs['multiple'] = True
        html_attrs = self._get_html_attrs(kwargs)
        html = [u'<select %s>' % html_attrs]

        if _items is None:
            _items = self.get_items()
        curr_values = self.value
        for value, label in _items:
            item_attrs = {'value': value}
            if str(value) in curr_values:
                item_attrs['selected'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(u'<option %s>%s</option>' % (html_attrs, label))
        html.append(u'</select>')
        return Markup('\n'.join(html))

    def as_checkboxes(self, _items=None,
            tmpl=u'<label><input %(attrs)s> %(label)s</label>', **kwargs):
        """Render the field as a series of checkboxes, using the `tmpl`
        parameter as the template.

        :param tmpl:
            HTML template to use for rendering each item.
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`

        """
        if _items is None:
            _items = self.get_items()
        kwargs['type'] = 'checkbox'
        kwargs['name'] = self.name
        html = []
        curr_values = self.value
        for value, label in _items:
            item_attrs = kwargs.copy()
            item_attrs['value'] = value
            if str(value) in curr_values:
                item_attrs['checked'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(tmpl % {'attrs': html_attrs, 'label': label})
        return Markup('\n'.join(html))


class Collection(Text):
    """A field that takes an open number of values of the same kind.
    For example, a list of comma separated tags or email addresses.

    :param sep:
        String to separate each value.
        When joining the values to render, it is used as-is. When splitting
        the user input, however, is tranformed first to a regexp
        when the spaces around the separator are ignored.
    :param filters:
        List of validators. If a value do not pass one of these it'll be
        filtered out from the final result.
    :param clean:
        An optional function that takes a value and return a 'cleaned' version
        of it. If a value raise an exception it'll be filtered out from the
        final result.
    :param *validators:
        An list of validators. This will evaluate each of the selected values
        when the method `validate` is called.

    Any other named parameter will be stored in `self.extra`.
    """

    def __init__(self, sep=', ', filters=None, clean=None,
            *validators, **kwargs):
        self.sep = sep
        filters = filters or []
        self.filters = [f() if inspect.isclass(f) else f for f in filters]
        self.clean = clean
        super(Collection, self).__init__(*validators, **kwargs)

    def _get_value(self):
        return self.sep.join(self._value) \
            if self._value and not self.hide_value else u''

    def _set_value(self, value):
        if not isinstance(value, list):
            value = [value]
        self._value = value

    value = property(_get_value, _set_value)
    
    def to_html(self, python_value):
        return python_value or []

    def to_python(self):
        sep = r'/s*%s/s*' % self.sep.replace(' ', '')
        values = self._value
        for f in self.filters:
            values = filter(f, values)
        if self.clean:
            values_ = []
            for value in values:
                try:
                    values_.append(self.clean(value))
                except Exception:
                    pass
            values = values_
        return values

