# -*- coding: utf-8 -*-
import datetime
import pytest

from solution.forms import validators as v


def test_required():
    """Test the field validator `Required`.
    """
    validator = v.Required()
    assert validator(u'abc')
    assert validator(True)
    assert not validator(u'')
    assert not validator(None)


def test_isnumber():
    """Test the field validator `IsNumber`.
    """
    validator = v.IsNumber()
    assert validator(33)
    assert validator(2.4)
    assert not validator(u'as2')


def test_isnaturalnumber():
    """Test the field validator `IsNaturalNumber`.
    """
    validator = v.IsNaturalNumber()
    assert validator(33)
    assert not validator(2.4)
    assert not validator(-10)
    assert not validator(u'as2')


def test_isdate():
    """Test the field validator `IsDate`.
    """
    validator = v.IsDate()
    assert validator(datetime.date.today())
    assert validator(datetime.datetime.utcnow())
    assert not validator(None)
    assert not validator(u'2012-04-13')


def test_longerthan():
    """Test the field validator `LongerThan`.
    """
    validator = v.LongerThan(4)
    assert validator(u'12345')
    assert not validator(u'123')


def test_shorterthan():
    """Test the field validator `ShorterThan`.
    """
    validator = v.ShorterThan(4)
    assert validator(u'123')
    assert not validator(u'12345')


def test_lessthan():
    """Test the field validator `LessThan`.
    """
    validator = v.LessThan(4)
    assert validator(3)
    assert not validator(5)


def test_morethan():
    """Test the field validator `MoreThan`.
    """
    validator = v.MoreThan(4)
    assert validator(5)
    assert not validator(3)


def test_inrange():
    """Test the field validator `InRange`.
    """
    validator = v.InRange(4, 10)
    assert validator(4)
    assert validator(10)
    assert not validator(3)
    assert not validator(11)


def test_match():
    """Test the field validator `Match`.
    """
    validator = v.Match(r'\+\d{2}-\d')
    assert validator(u'+51-1')
    assert not validator(u'33')


def test_iscolor():
    """Test the field validator `IsColor`.
    """
    validator = v.IsColor()
    assert validator(u'#ffaf2e')
    assert not validator(u'33')


def test_validemail():
    """Test the field validator `ValidEmail`.
    """
    validator = v.ValidEmail()
    assert validator(u'juan+pablo@example.net')
    assert validator(u'juanpablo.scaletti@nic.pe')
    assert not validator(u'lalala')
    assert not validator(u'aa@a')


def test_isurl():
    """Test the field validator `ValidURL`.
    """
    validator = v.ValidURL()
    assert validator(u'http://example.com')
    assert validator(u'www.archive.org')
    assert validator(u'http://españa.es')
    assert not validator('http://')
    assert not validator(u'lalala')
    assert not validator('ñ')


def test_before():
    """Test the field validator `Before`.
    """
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = v.Before(now)
    assert validator(now - delta)
    assert not validator(now + delta)


def test_after():
    """Test the field validator `After`.
    """
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = v.After(now)
    assert validator(now + delta)
    assert not validator(now - delta)


def test_beforenow():
    """Test the field validator `BeforeNow`.
    """
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = v.BeforeNow()
    assert validator(now - delta)
    assert not validator(now + delta)


def test_afternow():
    """Test the field validator `AfterNow`.
    """
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = v.AfterNow()
    assert validator(now + delta)
    assert not validator(now - delta)


def test_areequal():
    """Test the form validator `AreEqual`.
    """
    data = {
        'password': u'lalala',
        're_password': u'lalala',
    }
    validator = v.AreEqual(*data.keys())
    assert validator(data)
    data['re_password'] = u''
    assert not validator(data)

