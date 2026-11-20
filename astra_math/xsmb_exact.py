"""Exact finite-occupancy probabilities for an explicitly declared lottery null.

Unconditional model probabilities assume ``draws`` independent uniform draws WITH
replacement from ``alphabet`` distinct labels. Defaults are 27 prize tails from
00..99. The conditional ``random_k_anyhit`` baseline instead holds an observed
outcome fixed and randomizes a uniformly chosen distinct k-set. These calculations
are not evidence that real draws satisfy an iid null. No historical data, network,
solver, or third-party dependency is used.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb


def _integer(value: int, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _space(draws: int, alphabet: int) -> None:
    _integer(draws, "draws")
    _integer(alphabet, "alphabet", 1)


def _rational(value, name: str) -> Fraction:
    """Floats use their decimal repr, not their exact binary representation."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite rational number, not bool")
    try:
        return Fraction(str(value)) if isinstance(value, float) else Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite rational number") from exc


def _nonnegative(value, name: str) -> Fraction:
    result = _rational(value, name)
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def p_presence(draws: int = 27, alphabet: int = 100) -> Fraction:
    """Probability ONE specified label appears at least once."""
    _space(draws, alphabet)
    return 1 - Fraction(alphabet - 1, alphabet) ** draws


def p_all_distinct(k: int, draws: int = 27, alphabet: int = 100) -> Fraction:
    """Probability all k DISTINCT SPECIFIED labels appear at least once.

    Despite the short name, this is not the probability that every prize draw is
    different. It is the joint-presence probability for a fixed distinct k-set.
    Empty specified set has probability 1. Inclusion-exclusion is exact.
    """
    _space(draws, alphabet)
    _integer(k, "k")
    if k > alphabet:
        raise ValueError("k exceeds alphabet")
    if k > draws:
        return Fraction(0)
    numerator = sum((-1) ** j * comb(k, j) * (alphabet - j) ** draws
                    for j in range(k + 1))
    return Fraction(numerator, alphabet ** draws)


def nhay_distribution(draws: int = 27, alphabet: int = 100) -> tuple[Fraction, ...]:
    """P(one specified label occurs exactly j times), for j=0..draws."""
    _space(draws, alphabet)
    denominator = alphabet ** draws
    return tuple(Fraction(comb(draws, j) * (alphabet - 1) ** (draws - j),
                          denominator)
                 for j in range(draws + 1))


def random_k_anyhit(unique_observed: int, k: int,
                    alphabet: int = 100) -> Fraction:
    """Exact conditional baseline: random distinct k-set hits an observed u-set.

    Conditions on the realized number of different tails, u=unique_observed.
    Probability is 1-C(alphabet-u,k)/C(alphabet,k). This calculation does not
    require independent prize positions: it randomizes the selected k-set while
    holding the actual outcome fixed. It is not a forecast made before a draw.
    """
    _integer(alphabet, "alphabet", 1)
    _integer(unique_observed, "unique_observed")
    _integer(k, "k")
    if unique_observed > alphabet or k > alphabet:
        raise ValueError("unique_observed and k cannot exceed alphabet")
    miss = comb(alphabet - unique_observed, k) if k <= alphabet - unique_observed else 0
    return 1 - Fraction(miss, comb(alphabet, k))


def p_selected_occupancy(k: int, r: int, draws: int = 27,
                         alphabet: int = 100) -> Fraction:
    """Probability exactly r of a fixed k-set appear at least once.

    The other alphabet-k labels are unrestricted. Choose the r appearing labels,
    forbid the other k-r, then require every chosen label by inclusion-exclusion.
    Repeated appearances count only once in r. This is a joint occupancy event.
    """
    _space(draws, alphabet)
    _integer(k, "k")
    _integer(r, "r")
    if k > alphabet or r > k:
        raise ValueError("Require r <= k <= alphabet")
    if r > draws:
        return Fraction(0)
    numerator = comb(k, r) * sum(
        (-1) ** j * comb(r, j) * (alphabet - k + r - j) ** draws
        for j in range(r + 1))
    return Fraction(numerator, alphabet ** draws)


def selected_occupancy_distribution(k: int, draws: int = 27,
                                    alphabet: int = 100) -> tuple[Fraction, ...]:
    """Joint occupancy distribution for r=0..k; exact sum is one."""
    _space(draws, alphabet)
    _integer(k, "k")
    if k > alphabet:
        raise ValueError("k exceeds alphabet")
    return tuple(p_selected_occupancy(k, r, draws, alphabet) for r in range(k + 1))


def expected_occurrences(draws: int = 27, alphabet: int = 100) -> Fraction:
    """Expected number of occurrences of ONE specified label, not presence odds."""
    _space(draws, alphabet)
    return Fraction(draws, alphabet)


def expected_net(stake, gross_win_return, win_probability,
                 gross_loss_return=0) -> Fraction:
    """Net expectation for one fixed-payment binary event.

    Gross returns mean TOTAL cash received, including any returned stake. If a
    quote is net profit on a winning bet, add stake to obtain gross_win_return.
    stake is total amount paid, including any known fixed costs. No payout rates,
    fees, taxes, or actual betting availability are presumed by this function.
    """
    stake = _nonnegative(stake, "stake")
    win = _nonnegative(gross_win_return, "gross_win_return")
    lose = _nonnegative(gross_loss_return, "gross_loss_return")
    p = _rational(win_probability, "win_probability")
    if not 0 <= p <= 1:
        raise ValueError("win_probability outside [0,1]")
    return p * win + (1 - p) * lose - stake


def expected_net_occurrences(stake, gross_return_per_occurrence,
                             draws: int = 27, alphabet: int = 100,
                             additional_return_on_any_hit=0) -> Fraction:
    """Net expectation when a one-number bet pays once PER occurrence.

    gross_return_per_occurrence is cash paid for each appearance; it is not net
    profit. Additional returned stake, if paid once on any-hit and not already
    included in those cash payments, may be supplied separately. Never count a
    refund twice. For a cap/nonlinear payout use its full payoff distribution
    instead of this linear per-occurrence formula.
    """
    _space(draws, alphabet)
    stake = _nonnegative(stake, "stake")
    cash = _nonnegative(gross_return_per_occurrence, "gross_return_per_occurrence")
    additional = _nonnegative(additional_return_on_any_hit, "additional_return_on_any_hit")
    return expected_occurrences(draws, alphabet) * cash + p_presence(draws, alphabet) * additional - stake
