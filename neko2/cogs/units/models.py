#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation of the conversion data types.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from decimal import Decimal
import enum
import typing

from dataclasses import dataclass

from neko2.shared import alg

__all__ = ('UnitCategoryModel', 'UnitModel', 'UnitCollectionModel',
           'PotentialValueModel', 'ValueModel', 'pretty_print')


@enum.unique
class UnitCategoryModel(enum.Enum):
    """Holds a category of units."""
    DISTANCE = enum.auto()
    TIME = enum.auto()
    SPEED = enum.auto()
    VOLUME = enum.auto()
    FORCE_MASS = enum.auto(),
    DATA = enum.auto(),
    TEMPERATURE = enum.auto()


class UnitModel:
    """
    Representation of some unit measurement definition, such as meters.

    This will not store an arbitrary quantity. It exists as a way of
    simplifying
    the definition of what a unit is.

    The last name should be the abbreviated form to use for output. I could
    make that into a kwarg but YOLO.

    :param to_si: formulae to take a decimal and convert it to SI from this.
    :param from_si: formulae to take a decimal and convert it from SI to this.
    :param name: main name.
    :param other_names: other names and abbreviations.
    :param is_si: True if this is an SI measurement, False otherwise and by
            default.
    :param exclude_from_conversions: Defaults to false. When True, the
            measurement is allowed as valid input, but will not appear in
            lists of conversions generated by the application. This is useful
            for allowing `mm` as input while not displaying it as a separate
            entity to `m` which can be pretty-printed to `mm` anyway.
    :param never_use_std_form: Defaults to False. If True, it requests that any
            code formatting a string from this unit should not use standard
            form
            and instead prefer kilo/mega/giga prefixes, etc.
    """

    # What 1 si of whatever this unit measures is in this specific unit.
    def __init__(self,
                 to_si: typing.Callable[[Decimal], Decimal],
                 from_si: typing.Callable[[Decimal], Decimal],
                 name: str,
                 *other_names: str,
                 is_si: bool = False,
                 exclude_from_conversions=False,
                 never_use_std_form=False):
        self.names = (name, *other_names)
        self._to_si = to_si
        self._from_si = from_si
        self.is_si = is_si
        self.unit_type: UnitCategoryModel
        self.exclude_from_conversions = exclude_from_conversions
        self.never_use_std_form = never_use_std_form

    @property
    def name(self) -> str:
        return self.names[0]

    def to_si(self, this: Decimal) -> Decimal:
        """Converts this measurement to the SI equivalent."""
        return self._to_si(this)

    def from_si(self, si: Decimal) -> Decimal:
        """Converts this measurement from the SI equivalent to this."""
        return self._from_si(si)

    def __eq__(self, other: typing.Union[str, 'UnitModel']):
        """Equality is defines as a string match for any name"""
        if isinstance(other, UnitModel):
            return super().__eq__(other)
        else:
            return other.lower() in (n.lower() for n in self.names)

    def __hash__(self):
        """Enables hashing by the unit's primary name."""
        return hash(self.name.lower())

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f'<Unit name={self.name} '
            f'aliases={f", ".join(a for a in self.names[1:])}')

    def _set_unit_category(self, cat: UnitCategoryModel):
        self.unit_type = cat

    @classmethod
    def new_cv(cls,
               si_per_this: typing.Union[str, Decimal],
               name: str,
               *other_names: str,
               exclude_from_conversions=False,
               never_use_std_form=False) -> "UnitModel":
        """
        Initialises a unit that is purely a multiple of the SI quantity.

        This is useful if there is a constant linear relationship, as is for
        most measurements, except for Temperature.
        """
        if isinstance(si_per_this, str):
            si_per_this = Decimal(si_per_this)

        def to_si(c: Decimal):
            return c * si_per_this

        def from_si(c: Decimal):
            return c / si_per_this

        return cls(to_si, from_si, name, *other_names,
                   exclude_from_conversions=exclude_from_conversions,
                   never_use_std_form=never_use_std_form)

    @classmethod
    def new_si(cls, name: str, *other_names: str,
               never_use_std_form=False) -> "UnitModel":
        """Initialises a new SI measurement."""

        # noinspection PyTypeChecker
        def pass_through(x):
            return x

        return cls(pass_through, pass_through, name, *other_names, is_si=True,
                   never_use_std_form=never_use_std_form)


class UnitCollectionModel:
    def __init__(self,
                 category: UnitCategoryModel,
                 si: UnitModel,
                 *other_conversions: UnitModel):
        self.si = si
        self.unit_type = category
        # Obviously.
        self.si.is_si = True
        self.conversions = (si, *other_conversions)

        for conversion in self.conversions:
            # noinspection PyProtectedMember
            conversion._set_unit_category(self.unit_type)

    def find_unit(self, name: str) -> typing.Optional[UnitModel]:
        """
        Looks for a unit with a matching name, and returns it.

        If one does not exist, we return None.
        """
        return alg.find(lambda c: c == name, self.conversions)

    def __contains__(self, unit: str):
        """
        Determine if we can match the given string to some unit definition.
        :param unit: string to look up.
        :return: true if we can, false otherwise.
        """
        return bool(self.find_unit(unit))

    @staticmethod
    def convert(qty: Decimal, unit: UnitModel, to: UnitModel):
        """
        Converts one quantity to another assuming they are the same
        type of unit.
        """
        if unit == to:
            return qty
        else:
            return Decimal('1')

    def find_conversions(self, qty: Decimal, unit: UnitModel):
        """
        Returns a list of all conversion equivalents for this unit.

        The unit passed in is not included in this.
        """
        results = []
        for other_unit in self.conversions:
            if other_unit == unit:
                continue

            results.append(self.convert(qty, unit, other_unit))

        return tuple(results)

    def __iter__(self) -> typing.Iterator[UnitModel]:
        return iter(self.conversions)


@dataclass()
class PotentialValueModel:
    """
    A tokenized potential measurement that matches our input regex. It has not
    yet been verified as an existing measurement in our dictionary however.
    """
    value: Decimal
    unit: str

    def __str__(self):
        return f'{self.value} {self.unit}'


@dataclass(init=False)
class ValueModel:
    """An instance of a measurement that we have interpreted successfully."""
    value: Decimal
    unit: UnitModel

    def __init__(self, value: typing.Union[str, Decimal], unit: UnitModel):
        self.value = Decimal(value)
        self.unit = unit

    @property
    def name(self):
        names = self.unit.names
        if len(names) == 1 or self.value == Decimal(1):
            return names[0]
        else:
            return names[1]

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return f'{round(float(self.value), 4):g} {self.unit.names[-1]}'


# Maps a base-10 logarithm to the suffix. For example,
# -6 = 10^-6 = micro = µ. The mapped values are a tuple of abbreviation
# and full name, so in this example, we expect the pair `-6: ('µ', 'micro')`
bases = {
    -24: ('y', 'yocto'),
    -21: ('z', 'zepto'),
    -18: ('a', 'atto'),
    -15: ('f', 'femto'),
    -12: ('p', 'pico'),
    -9: ('n', 'nano'),
    -6: ('µ', 'micro'),
    -3: ('m', 'milli'),
    -2: ('c', 'centi'),
    # Ignore deci, as this is not often used.
    +0: ('', ''),
    +3: ('k', 'kilo'),
    +6: ('M', 'mega'),
    +9: ('G', 'giga'),
    +12: ('T', 'tera'),
    +15: ('P', 'peta'),
    +18: ('E', 'exa'),
    +21: ('Z', 'zetta'),
    +24: ('Y', 'yotta'),
}


def pretty_print(d: Decimal,
                 suffix_name: str,
                 use_long_suffix=False,
                 use_std_form=True,
                 none_if_rounds_to_zero=False):
    """
    Python is a pain when it comes to formatting decimals/floats in the
    format I want. Therefore it is probably just easier for me to write the
    algorithm myself that I want to use to produce a clean representation
    of the data.

    :param d: the decimal to format
    :param suffix_name: the abbreviated unit name (e.g. m for meters)
    :param use_long_suffix: true if we should use "milli-" instead of "m".
        False if unspecified.
    :param use_std_form: False by default. When true, we just use standard
        form. This will override use_long_suffix.
    :param none_if_rounds_to_zero: False by default. If true, if we round
        down to zero, then we return None to allow the caller to exclude it
        from results.
    """

    def trunc(rounded_str):
        # Remove trailing zeros if we have any.
        if '.' in rounded_str and 'e' not in rounded_str.lower():
            while rounded_str[-1] in ('0', '.'):
                premature_break = rounded_str[-1] == '.'
                rounded_str = rounded_str[:-1]
                if premature_break:
                    break
        return rounded_str

    if d > 0:
        real_pot = int(d.log10())
    else:
        real_pot = 0

    if real_pot in bases:
        suffix = bases[real_pot]
        chosen_pot = real_pot
    else:
        # Find the closest logarithm.
        choices = bases.keys()

        differences = {abs(real_pot - c): c for c in choices}
        sorted_choices = sorted(differences.keys())

        chosen_pot = differences[sorted_choices[0]]
        suffix = bases[chosen_pot]

    # Divide by the chosen power of ten to get the
    # value in the base we want.
    if use_std_form:
        if Decimal('0.00001') <= abs(d) < Decimal('1000000000') or d.is_zero():
            rounded_str = f'{d:,.6f}'
            return f'{trunc(rounded_str)} {suffix_name}'
            # return f'{d:,.4f} {suffix_name}'
        else:
            return f'{d:,.4e} {suffix_name}'
            # return f'{d:,.4g} {suffix_name}'
    else:
        d /= Decimal(10 ** chosen_pot)

        rounded = round(d, 3)

        if rounded == Decimal(0) and none_if_rounds_to_zero:
            return None
        else:
            rounded_str = f'{rounded:,f}'
            rounded_str = trunc(rounded_str)
            return (
                f'{rounded_str} '
                f'{suffix[1 if use_long_suffix else 0]}{suffix_name}')
