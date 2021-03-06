#!/usr/bin/env python3

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement


#import sys
from functools import wraps  # todo
from math import inf
from typing import Type
from typing import cast

from asserttool import eprint
from asserttool import ic
#import errno as error_number
from delay_timer import DelayTimer


def retry_on_exception(*,
                       exception: Type[Exception],
                       errno=None,
                       in_e_args=None,
                       kwargs: dict = {},
                       args: tuple = (),
                       kwargs_add_on_retry={},
                       args_add_on_retry: tuple = (),
                       kwargs_extract_from_exception=(),
                       delay: float = 1.0,
                       max_delay: float = 60.0,
                       retries: float = inf,
                       call_function_once=None,
                       call_function_once_args=(),
                       call_function_once_kwargs={},
                       verbose: bool = False,
                       debug: bool = False,
                       delay_multiplier: float = 0.6,):

    delay_timer = DelayTimer(start=delay,
                             multiplier=delay_multiplier,
                             end=max_delay,
                             verbose=verbose,)

    def retry_on_exception_decorator(function):
        @wraps(function)
        def retry_on_exception_wrapper(*args, **kwargs):
            nonlocal delay
            if not issubclass(exception, Exception):
                raise ValueError('exception must be a subclass of Exception, not:', type(exception))
            tries = 0
            if retries < 1:
                raise ValueError('retries must be >= 1: retries:', retries)
            if debug:
                ic(exception)
                ic(type(exception))
                ic(errno)
                ic(in_e_args)
                ic(kwargs)
                ic(args)
                ic(delay)
                ic(max_delay)
                ic(retries)
                ic(kwargs_add_on_retry)
                ic(args_add_on_retry)
                ic(kwargs_extract_from_exception)
                ic(call_function_once)
                ic(call_function_once_args)
                ic(call_function_once_kwargs)
                ic(delay_multiplier)

            raise_next = False
            kwargs_extracted_from_exception = {}
            #ic(raise_next)
            while True:
                if tries > (retries - 1):
                    ic(tries, '>', retries - 1, 'raising next matching exception:', exception)
                    raise_next = True
                    #ic(raise_next)
                try:
                    if verbose:
                        ic('calling:', function.__name__)
                        ic(args)
                        ic(kwargs)
                    tries += 1
                    if kwargs_extracted_from_exception:
                        return function(*args, **kwargs, **kwargs_extracted_from_exception)
                    else:
                        return function(*args, **kwargs)
                except exception as e:
                    if debug:
                        ic(e)

                    # deliberately about to raise an AttributeError if errno was passed and e does not have it, this is by design
                    # seemingly, not actually raising AttributeError yet though... TODO
                    #if errno:  # mypy not happy
                    #if isinstance(e, OSError):  # mypy is fine with this, but it's using isinstance()
                    #    if not e.errno == errno:
                    #        raise e
                    if errno:
                        if not cast(OSError, e).errno == errno:  # best way?
                            raise e


                    if in_e_args:
                        if debug:
                            ic(e.args)
                        found = False
                        for arg in e.args:
                            try:
                                if in_e_args in arg:
                                    found = True
                            except TypeError:  # TODO check for: TypeError: argument of type 'MaxRetryError' is not iterable
                                pass
                        if not found:
                            raise e

                    if kwargs_extract_from_exception:
                        for arg in e.args:
                            if isinstance(arg, dict):
                                for kw in kwargs_extract_from_exception:
                                    if kw in arg.keys():
                                        kwargs_extracted_from_exception[kw] = arg[kw]
                        for kw in kwargs_extract_from_exception:
                            if kw not in kwargs_extracted_from_exception.keys():
                                ic(kw, 'not found in', e.args, 'exception does not match, raising:', e)
                                raise e
                    # by here, the exception is valid to be caught


                    if raise_next:
                        #ic(raise_next)
                        ic(raise_next, 'raising:', e)
                        raise e
                    ic(function)
                    if verbose:
                        ic(exception)

                    if hasattr(e, 'errno'):
                    #if cast(OSError, e).errno:  # need typing.Protocol?
                        ic(e, e.errno)  # mypy: "Exception" has no attribute "errno"  [attr-defined]

                    else:
                        ic(e)
                    for index, arg in enumerate(e.args):
                        ic(index, arg)
                    if call_function_once:
                        if tries == 1:
                            call_function_once_result = call_function_once(*call_function_once_args, **call_function_once_kwargs)
                            ic(call_function_once_result)
                    delay_timer.sleep()
                except Exception as e:
                    if debug:
                        ic(e)
                        ic(type(e))
                    raise e
        return retry_on_exception_wrapper
    return retry_on_exception_decorator


#def retry_on_exception_manual(function,
#                              *,
#                              exceptions,
#                              errno=None,
#                              kwargs={},
#                              args=(),
#                              delay=1,
#                              retries=inf,
#                              verbose=False,
#                              delay_multiplier=0.5,):
#
#    if not isinstance(exceptions, tuple):
#        raise ValueError('exceptions must be a tuple, not:', type(exceptions))
#    tries = 0
#    while True:
#        if tries > retries:
#            ic(tries, '>', retries, 'breaking')
#            break
#        try:
#            if verbose:
#                ic('calling:', function.__name__)
#                ic(args)
#                ic(kwargs)
#            tries += 1
#            return function(*args, **kwargs)
#        except exceptions as e:
#            ic(e)  # need this to see what exception is being retried
#            if errno:
#                if not e.errno == errno:  # gonna throw an AttributeError if errno was passed and e does not have it, this is by design
#                    raise e
#            ic(function)
#            ic(exceptions)
#            if hasattr(e, 'errno'):
#                ic(e, e.errno)
#            else:
#                ic(e)
#            delay = delay + (delay * delay_multiplier)
#            ic(delay)
#            time.sleep(delay)

